import os

BASE_DIR = "images"

def read_tiles(tile_folder):
    tiles = {}
    map_tiles = {}
    for index, png_tile in enumerate(os.listdir(tile_folder)):
        tiles[str(index + 1)] = {
            "movable": False,
            "path": BASE_DIR + "/tiles/" + png_tile,
            "name": png_tile,
        } 
    return tiles

def read_objects(object_folder):
    objects = {}
    for index, png_object in enumerate(os.listdir(object_folder)):
        objects[str(index + 1)] = {
            "movable": False,
            "interactive": True,
            "rowSpan": 1, "columnSpan": 1,
            "noTransparency": False,
            "floor": False,
            "name": png_object,
            "visuals": { "idle": { "frames": [ { "path": BASE_DIR + "/objects/" + png_object } ] } }
        }
    return objects


def get_tile_id(tile_list, tile_name):
    result = [tile_id for tile_id, tile in tile_list.items() if tile['name'] == tile_name + ".png"]
    if result:
        return result[0]
    raise Exception("Not Found")


def get_object_id(object_list, object_name):
    result = [object_id for object_id, obj in object_list.items()
              if obj['name'] == object_name + ".png"]
    if result:
        return result[0]
    raise Exception("Not Found")
