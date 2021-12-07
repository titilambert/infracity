import re
import math
import random
import copy

from kubernetes import client, config
from rectpack import newPacker, PackingMode
import rectpack.maxrects as maxrects

from infracity.read_images import get_tile_id, get_object_id, get_vehicle_id
from infracity.block import SpecialBlock, ChurchBlock, BankBlock, FireStationBlock
from infracity.vehicle import Vehicle


class Town:
    """Town."""

    def __init__(self, name):
        self.name = name
        self.blocks = {}
        self._ground_map = []
        self._objects_map = []
        self._block_packing = []
        self.set_default_blocks()

    @property
    def surface(self):
        # Need to do a calculation to add more empty green tiles around the town
        return sum([d.surface for d in self.blocks.values()])
    
    @property
    def ground_map(self):
        return self._ground_map

    @property
    def objects_map(self):
        return self._objects_map

    @property
    def dimensions(self):
        dim = {"x": 0, "y": 0}
        if self._ground_map:
            dim["x"] = len(self._ground_map)
            dim["y"] = len(self._ground_map[0])
        return dim
    
    def set_position(self, row, col):
        self._row = row
        self._col = col

    @property
    def row(self):
        return self._row
    
    @property
    def col(self):
        return self._col

    def set_default_blocks(self):
        bank = BankBlock()
        church = ChurchBlock()
        firestation = FireStationBlock()
        self.blocks = {
            "bank": bank,
            "church": church,
            "firestation": firestation
        }

    def generate_vehicles(self, object_list):
        # Add vehicles
        vehicles = {}
        for block in self.blocks.values():
            for bvehicle in block.vehicles.values():
                if bvehicle.name in vehicles:
                    vehicle = vehicles[bvehicle.name]
                else:
                    vehicle = copy.copy(bvehicle)
                    vehicles[vehicle.name] = vehicle
                    if vehicle.common_base_name:
                        vehicle.add_stop(self.blocks[vehicle.common_base_name].position)
                vehicle.add_stop(block.position)

        for vehicle in vehicles.values():
            object_id = get_vehicle_id(object_list, vehicle.vtype)
            self._objects_map[vehicle.start_position["x"]][vehicle.start_position["y"]] = object_id
        self.vehicles = vehicles

    def generate(self, tile_list, object_list):
        # Bin packing
        packer = newPacker(mode=PackingMode.Offline, pack_algo=maxrects.MaxRectsBlsf, rotation=1)
        for block in self.blocks.values():
            packer.add_rect(block.raw_dimensions["x"], block.raw_dimensions["y"], block.name)
        packer.add_bin(1000, 1000)
        packer.pack()
        self._block_packing =  packer.rect_list()

        # Skip Empty namespace
        if not self._block_packing:
            return

        # Try to find the size of the rectangle containing all the block
        fullsize_x = max([sum([tc[1], tc[3]]) for tc in self._block_packing])
        fullsize_y = max([sum([tc[2], tc[4]]) for tc in self._block_packing])

        for column in range(fullsize_x):
            self._ground_map.append([0 for i in range(fullsize_y)])
            self._objects_map.append([0 for i in range(fullsize_y)])

        # Place objects and tiles on the groundmap and objectsmap
        for block_data in self._block_packing:
            block_name = block_data[-1]
            block = self.blocks[block_name]
            pos_x = block_data[1]
            pos_y = block_data[2]
            block.set_position(pos_x, pos_y)
            length_x = block_data[3]
            length_y = block_data[4]
            block.set_dimensions(length_x, length_y)
            block.generate(self._ground_map, self._objects_map, tile_list, object_list)

        # Vehicles
        self.generate_vehicles(object_list)

        # Fill the gaps by parks
        for row_index, row in enumerate(self._ground_map):
            for column_index, tile_id in enumerate(row):
                if tile_id == 0:
                    tile_id = get_tile_id(tile_list, "park")
                    self._ground_map[row_index][column_index] = tile_id

        # Add a 3 tile margin arround the city
        tile_grass_id = get_tile_id(tile_list, "grass_full")
        margin_row = [tile_grass_id for i in range(len(self._ground_map[0]) + 6)]

        for row in self._ground_map:
            row.insert(0, tile_grass_id)
            row.insert(0, tile_grass_id)
            row.insert(0, tile_grass_id)
            row.append(tile_grass_id)
            row.append(tile_grass_id)
            row.append(tile_grass_id)
        self._ground_map.insert(0, margin_row)
        self._ground_map.insert(0, margin_row)
        self._ground_map.insert(0, margin_row)
        self._ground_map.append(margin_row)
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
