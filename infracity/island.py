import re
import math
import random

from kubernetes import client, config
from rectpack import newPacker, PackingMode
import rectpack.maxrects as maxrects

from infracity.read_images import get_tile_id, get_object_id


class Island:

    def __init__(self, name, towns):
        self.name = name
        self.towns = towns
        self._ground_map = []
        self._objects_map = []
        self._town_packing = []

    @property
    def surface(self):
        return self.dimensions["x"] * self.dimensions["y"]

    @property
    def ground_map(self):
        return self._ground_map

    @property
    def objects_map(self):
        return self._objects_map


    @property
    def dimensions(self):
        dim = {"x": None, "y": None}
        dim["x"] = len(self._ground_map[0])
        dim["y"] = len(self._ground_map)
        return dim

    def generate(self, tile_list, object_list):
        """Arrange towns on a island.

        Using MaxRectsBlsf, the island tries to seem like a square.
        """
        # Generate towns
        for town in self.towns.values():
            town.generate(tile_list, object_list)

        # Generate island
        # https://gorillasun.de/blog/Rectangle-Packing-An-incredibly-difficult-problem
        # pip install rectpack
        # Using algo: MaxRectsBlsf
        packer = newPacker(mode=PackingMode.Offline, pack_algo=maxrects.MaxRectsBlsf, rotation=0)
        for town in self.towns.values():
            if not town.dimensions["x"]:
                continue
            packer.add_rect(town.dimensions["x"], town.dimensions["y"], town.name)

        packer.add_bin(10000, 10000)
        packer.pack()
        self._town_packing = packer.rect_list()

        # Try to find the size of the rectangle containing all the town
        fullsize_x = max([sum([tc[1], tc[3]]) for tc in self._town_packing])
        fullsize_y = max([sum([tc[2], tc[4]]) for tc in self._town_packing])

        for column in range(fullsize_x):
            self._ground_map.append([0 for i in range(fullsize_y)])
            self._objects_map.append([0 for i in range(fullsize_y)])

        # Place objects and tiles on the groundmap and objectsmap
        for town_data in self._town_packing:
            pos_x = town_data[1]
            pos_y = town_data[2]
            length_x = town_data[3]
            length_y = town_data[4]
            town_name = town_data[-1]
            #print(town_name, length_x, length_y)
            town = self.towns[town_name]
            for tile_x in range(length_x):
                for tile_y in range(length_y):
                    self._ground_map[tile_x + pos_x][tile_y + pos_y] = town.ground_map[tile_x][tile_y]
                    self._objects_map[tile_x + pos_x][tile_y + pos_y] = town.objects_map[tile_x][tile_y]

        # Fill the gaps by forest
        for row_index, row in enumerate(self._ground_map):
            for column_index, tile_id in enumerate(row):
                if tile_id == 0:
                    tile_id = get_tile_id(tile_list, "grass_full")
                    object_id = get_object_id(object_list, "forest_{}".format(random.randint(1, 10)))
                    self._ground_map[row_index][column_index] = tile_id
                    self._objects_map[row_index][column_index] = object_id

        # Add a 3 tile margin arround the island
        tile_sea_id = get_tile_id(tile_list, "sea_full")
        row_length = len(self._ground_map[0])
        margin_row = [tile_sea_id for i in range(row_length + 6)]

        tile_beach_right_id = get_tile_id(tile_list, "beach_right")
        tile_beach_left_id = get_tile_id(tile_list, "beach_left")
        for row in self._ground_map:
            row.insert(0, tile_beach_right_id)
            row.insert(0, tile_sea_id)
            row.insert(0, tile_sea_id)
            row.append(tile_beach_left_id)
            row.append(tile_sea_id)
            row.append(tile_sea_id)

        tile_beach_bottom_id = get_tile_id(tile_list, "beach_bottom")
        tile_beach_corner_right_id = get_tile_id(tile_list, "beach_corner_right")
        tile_beach_corner_bottom_id = get_tile_id(tile_list, "beach_corner_bottom")
        margin_top_row = [tile_sea_id, tile_sea_id, tile_beach_corner_right_id] + \
                [tile_beach_bottom_id for i in range(row_length)] + \
                [tile_beach_corner_bottom_id, tile_sea_id, tile_sea_id]
        self._ground_map.insert(0, margin_top_row)
        self._ground_map.insert(0, margin_row)
        self._ground_map.insert(0, margin_row)

        tile_beach_top_id = get_tile_id(tile_list, "beach_top")
        tile_beach_corner_left_id = get_tile_id(tile_list, "beach_corner_left")
        tile_beach_corner_top_id = get_tile_id(tile_list, "beach_corner_top")
        margin_bottom_row = [tile_sea_id, tile_sea_id, tile_beach_corner_top_id] + \
                [tile_beach_top_id for i in range(row_length)] + \
                [tile_beach_corner_left_id, tile_sea_id, tile_sea_id]
        self._ground_map.append(margin_bottom_row)
        self._ground_map.append(margin_row)
        self._ground_map.append(margin_row)

        margin_row = [0 for i in range(len(self._objects_map[0]) + 6)]
        for row in self._objects_map:
            row.insert(0, 0)
            row.insert(0, 0)
            row.insert(0, 0)
            row.append(0)
            row.append(0)
            row.append(0)
        self._objects_map.insert(0, margin_row)
        self._objects_map.insert(0, margin_row)
        self._objects_map.insert(0, margin_row)
        self._objects_map.append(margin_row)
        self._objects_map.append(margin_row)
        self._objects_map.append(margin_row)
