import json

from dump_k8s import dump_data
from read_images import read_tiles, read_objects, get_tile_id, get_object_id

# Read tile and object images
tiles = read_tiles("html/images/tiles")
objects = read_objects("html/images/objects")

# Get Cluster data
k8s_cluster = dump_data()

# Choose a namespace (Only one namespace is handle for now)
namespace_name = "kube-system"

# Arrange districts in the town (calling bin packing algo)
k8s_cluster.towns[namespace_name].arrange(tiles, objects)

# Generate final map data
map_data = {
    "tiles": tiles,
    "objects": objects,
    "groundMap": [{"row": r} for r in k8s_cluster.towns[namespace_name].ground_map],
    "objectsMap": [{"row": r} for r in k8s_cluster.towns[namespace_name].objects_map],
    "initialControllableLocation": { "columnIndex": 0, "rowIndex": 0},
}

# Write json file
with open("html/mapDataIC.json", "w") as fhic:
    json.dump(map_data, fhic, indent=4, sort_keys=True)

print("Please run: python3 -m http.server 8000")
print("And go to: http://127.0.0.1:8000/html/map.html")
