import os
from flask import render_template, url_for

BASE_DIR = "images"

def read_tiles(tile_folder):
    tiles = {}
    map_tiles = {}
    for index, png_tile in enumerate(os.listdir(tile_folder)):
        tiles[str(index + 1)] = {
            "movable": png_tile.startswith("street_"),
            "path": "images/tiles/" + png_tile,
            "name": png_tile,
        } 
    return tiles

def read_objects(object_folder):
    objects = {}
    for index, png_object in enumerate(os.listdir(object_folder)):
        column_span = 1
        if png_object == "church.png":
            column_span = 3
        if png_object == "firestation.png":
            column_span = 2
        objects[str(index + 1)] = {
            "movable": False,
            "interactive": True,
            "rowSpan": 1, "columnSpan": column_span,
            "noTransparency": False,
            "floor": False,
            "name": png_object,
            "visuals": { "idle": { "frames": [ { "path": "images/objects/" + png_object } ] } }
        }
    return objects


def read_vehicles(vehicles_folder, vehicles):
    vehicle_key = max([int(k) for k in vehicles.keys()]) + 1
    for index, vehicle_name in enumerate(os.listdir(vehicles_folder)):
        vehicle = {
            "movable": True,
            "interactive": True,
            "rowSpan": 1, "columnSpan": 1,
            "noTransparency": False,
            "floor": False,
            "name": vehicle_name,
            "visuals": {
            }
        }
        for png_object in os.listdir(os.path.join(vehicles_folder, vehicle_name)):
            direction = png_object.rsplit("_")[-1].split(".")[0].lower()
            vehicle["visuals"][f"idle_{direction}"] = {"frames": [{"path": "images/vehicles/" + vehicle_name + "/" + png_object}]}
            vehicle["visuals"][f"move_{direction}"] = {"frames": [{"path": "images/vehicles/" + vehicle_name + "/" + png_object}]}

        vehicle["visuals"]["idle"] = vehicle["visuals"]["idle_se"].copy()
        vehicles[str(vehicle_key + index)] = vehicle

    return vehicles


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
    raise Exception("Not Found", object_name)


def get_vehicle_id(object_list, object_name):
    result = [object_id for object_id, obj in object_list.items()
              if obj['name'] == object_name]
    if result:
        return result[0]
    raise Exception("Not Found", object_name)
