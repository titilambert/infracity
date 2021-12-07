from infracity.read_images import get_tile_id, get_object_id


class Block:
    """Deployment/DaemonSet/StateFulSet."""

    def __init__(self, name, wtype, color=None):
        self.name = name
        self._type = wtype
        self._color = color
        self.buildings = {}  # should be equal to replicas
        self._position = {}
        self._dimensions = {}
        self.vehicles = {}

    @property
    def type(self):
        return self._type

    @property
    def color(self):
        return self._color

    @property
    def surface(self):
        return self.raw_dimensions["x"] * self.raw_dimensions["y"]

    @property
    def height(self):
        return min(len(next(iter(self.buildings.values())).floors), 5)

    def get_object_image(self, orientation):
        return f"building_{self.color}_{orientation}_{self.height}_floors"

    def set_position(self, pos_x, pos_y):
        self._position = {"x": pos_x, "y": pos_y}

    @property
    def position(self):
        return self._position

    @property
    def position_x(self):
        return self._position["x"]

    @property
    def position_y(self):
        return self._position["y"]

    def set_dimensions(self, length_x , length_y):
        self._dimensions = {"x": length_x, "y": length_y}

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def length_x(self):
        return self._dimensions["x"]

    @property
    def length_y(self):
        return self._dimensions["y"]

    @property
    def raw_dimensions(self):
        # Create rectangles with differents width
        # Add calculation to count the routes aroud the block
        dim = {}
        if len(self.buildings) <= 1:
            # +-+
            # |B|
            # +-+
            dim["x"] = dim["y"] = 3
        else:
            # +--+
            # |BB|
            # |BB|
            # ....
            # |BB|
            # |B |
            # +--+
            dim["x"] = 4
            dim["y"] = 1 + len(self.buildings) // 2 + len(self.buildings) % 2 + 1
        return dim

    def generate(self, ground_map, objects_map, tile_list, object_list):
        for tile_x in range(self.length_x):
            for tile_y in range(self.length_y):
                object_id = None
                #if block is None and block_name in ("church",) and tile_x == length_x - 3 and tile_y == 1:
                #    tile_name = "grass_full"
                #    object_id = get_object_id(object_list, block_name)
                #elif block is None and block_name in ("bank", "firestation") and tile_x == length_x - 2 and tile_y == 1:
                #    tile_name = "grass_full"
                #    object_id = get_object_id(object_list, block_name)
                if tile_x == 0 and tile_y == 0:
                    tile_name = "street_corner_right"
                elif tile_x == 0 and tile_y == self.length_y - 1:
                    tile_name = "street_corner_bottom"
                elif tile_x == self.length_x - 1 and tile_y == 0:
                    tile_name = "street_corner_top"
                elif tile_x == self.length_x - 1 and tile_y == self.length_y - 1:
                    tile_name = "street_corner_left"
                elif tile_x == 0:
                    tile_name = "street_straight_top"
                elif tile_x == self.length_x - 1:
                    tile_name = "street_straight_bottom"
                elif tile_y == 0:
                    tile_name = "street_straight_left"
                elif tile_y == self.length_y - 1:
                    tile_name = "street_straight_right"
                else:
                    if self.type == "special":
                        tile_name = "grass_full"
                    elif len(self.buildings) == 0:
                        # workload with 0 replica
                        tile_name = "earth_full"
                    else:
                        tile_name = "grass_full"
                        if self.length_x > self.length_y:
                            object_name = self.get_object_image("left")
                        else:
                            object_name = self.get_object_image("right")
                        object_id = get_object_id(object_list, object_name)

                tile_id = get_tile_id(tile_list, tile_name)
                ground_map[tile_x + self.position_x][tile_y + self.position_y] = tile_id
                if object_id is not None:
                    objects_map[tile_x + self.position_x][tile_y + self.position_y] = object_id


class SpecialBlock(Block):

    def __init__(self, name, size_x, size_y, object_image):
        Block.__init__(self, name, "special")
        self._dimensions = {"x": size_x, "y": size_y}
        self._object_image = object_image

    def get_object_image(self):
        return self._object_image

    @property
    def height(self):
        return 1

    @property
    def raw_dimensions(self):
        return self._dimensions


class ChurchBlock(SpecialBlock):

    def __init__(self):
        SpecialBlock.__init__(self, "church", 5, 5, "church")

    def generate(self, ground_map, objects_map, tile_list, object_list):
        ground = [
                ["street_corner_right", "street_straight_top", "street_straight_top", "street_straight_top", "street_corner_bottom"],
                ["street_straight_left", "grass_full", "grass_full", "grass_full", "street_straight_right"],
                ["street_straight_left", "grass_full", "grass_full", "grass_full", "street_straight_right"],
                ["street_straight_left", "grass_full", "grass_full", "grass_full", "street_straight_right"],
                ["street_corner_top", "street_straight_bottom", "street_straight_bottom", "street_straight_bottom", "street_corner_left"],
                ]
        objects = [
                [None, None, None, None, None],
                [None, None, None, None, None],
                [None, self.get_object_image(), None, None, None],
                [None, None, None, None, None],
                [None, None, None, None, None],
                ]

        for tile_x, row in enumerate(ground):
            for tile_y, tile_name in enumerate(row):
                tile_id = get_tile_id(tile_list, tile_name)
                ground_map[tile_x + self.position_x][tile_y + self.position_y] = tile_id

        for tile_x, row in enumerate(objects):
            for tile_y, object_name in enumerate(row):
                if object_name is not None:
                    object_id = get_object_id(object_list, object_name)
                    objects_map[tile_x + self.position_x][tile_y + self.position_y] = object_id


class BankBlock(SpecialBlock):

    def __init__(self):
        SpecialBlock.__init__(self, "bank", 3, 3, "bank")

    def generate(self, ground_map, objects_map, tile_list, object_list):
        ground = [
                ["street_corner_right", "street_straight_top", "street_corner_bottom"],
                ["street_straight_left", "concrete_full", "street_straight_right"],
                ["street_corner_top", "street_straight_bottom", "street_corner_left"],
                ]
        objects = [
                [None, None, None],
                [None, self.get_object_image(), None],
                [None, None, None],
                ]

        for tile_x, row in enumerate(ground):
            for tile_y, tile_name in enumerate(row):
                tile_id = get_tile_id(tile_list, tile_name)
                ground_map[tile_x + self.position_x][tile_y + self.position_y] = tile_id

        for tile_x, row in enumerate(objects):
            for tile_y, object_name in enumerate(row):
                if object_name is not None:
                    object_id = get_object_id(object_list, object_name)
                    objects_map[tile_x + self.position_x][tile_y + self.position_y] = object_id


class FireStationBlock(SpecialBlock):

    def __init__(self):
        SpecialBlock.__init__(self, "firestation", 4, 4, "firestation")

    def generate(self, ground_map, objects_map, tile_list, object_list):
        ground = [
                ["street_corner_right", "street_straight_top", "street_straight_top", "street_corner_bottom"],
                ["street_straight_left", "concrete_full", "concrete_full", "street_straight_right"],
                ["street_corner_top", "street_straight_bottom", "street_straight_bottom", "street_corner_left"],
                ]
        objects = [
                [None, None, None, None],
                [None, self.get_object_image(), None, None],
                [None, None, None, None],
                ]

        for tile_x, row in enumerate(ground):
            for tile_y, tile_name in enumerate(row):
                tile_id = get_tile_id(tile_list, tile_name)
                ground_map[tile_x + self.position_x][tile_y + self.position_y] = tile_id

        for tile_x, row in enumerate(objects):
            for tile_y, object_name in enumerate(row):
                if object_name is not None:
                    object_id = get_object_id(object_list, object_name)
                    objects_map[tile_x + self.position_x][tile_y + self.position_y] = object_id
