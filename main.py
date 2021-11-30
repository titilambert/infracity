import json
from dump_k8s import dump_data
from arrange import arrange_town

from read_images import read_tiles, read_objects, get_tile_id, get_object_id

# Read tile and object images
tiles = read_tiles("html/images/tiles")
objects = read_objects("html/images/objects")

# Get Cluster data
k8s_cluster = dump_data()

# Choose a namespace (Only one namespace is handle for now)
namespace_name = "default"

# Arrange districts in the town (calling bin packing algo)
town_coords = arrange_town(k8s_cluster.towns[namespace_name])

# Get the dimensions of the town
town_size_x = sum(max([(tc[1], tc[3]) for tc in town_coords]))
town_size_y = sum(max([(tc[2], tc[4]) for tc in town_coords]))

# Prepare groundmap and objectsmap
groundMap = []
objectsMap = []
for column in range(town_size_x):
    groundMap.append({"row": [0 for i in range(town_size_y)]})
    objectsMap.append({"row": [0 for i in range(town_size_y)]})


# Place objects and tiles on the groundmap and objectsmap
for district_data in town_coords:
    pos_x = district_data[1]
    pos_y = district_data[2]
    district_name = district_data[-1]
    district = k8s_cluster.towns[namespace_name].districts[district_name]
    for tile_x in range(district.dimensions["x"]):
        for tile_y in range(district.dimensions["y"]):
            object_id = None
            if tile_x == 0 and tile_y == 0:
                tile_name = "street_curve_right"
            elif tile_x == 0 and tile_y == district.dimensions["y"] - 1:
                tile_name = "street_curve_bottom"
            elif tile_x == district.dimensions["x"] - 1 and tile_y == 0:
                tile_name = "street_curve_top"
            elif tile_x == district.dimensions["x"] - 1 and tile_y == district.dimensions["y"] - 1:
                tile_name = "street_curve_left"
            elif tile_x == 0 or tile_x == district.dimensions["x"] - 1:
                tile_name = "street_straight_right"
            elif tile_y == 0 or tile_y == district.dimensions["y"] - 1:
                tile_name = "street_straight_top"
            else:
                tile_name = "grass_full"
                if district.dimensions["x"] > district.dimensions["y"]:
                    object_name = "base_red_left"
                else:
                    object_name = "base_red_right"
                object_id = get_object_id(objects, object_name)
            tile_id = get_tile_id(tiles, tile_name)
            try:
                groundMap[tile_x + pos_x]['row'][tile_y + pos_y] = tile_id
                if object_id is not None:
                    objectsMap[tile_x + pos_x]['row'][tile_y + pos_y] = object_id
            except:
                import ipdb; ipdb.set_trace()


# Generate final map data
map_data = {
    "tiles": tiles,
    "objects": objects,
    "groundMap": groundMap,
    "objectsMap": objectsMap,
    "initialControllableLocation": { "columnIndex": 0, "rowIndex": 0},
}

# Write json file
with open("html/mapDataIC.json", "w") as fhic:
    json.dump(map_data, fhic, indent=4, sort_keys=True)

print("Please run: python3 -m http.server 8000")
print("And go to: http://127.0.0.1:8000/html/map.html")
