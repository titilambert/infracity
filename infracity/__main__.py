import json
import os

from flask import render_template, url_for, g
from flask import Flask

from infracity.dump_k8s import dump_data
from infracity.read_images import read_tiles, read_objects, read_vehicles, get_tile_id, get_object_id


def generate_map():
    global map_data
    # Read tile and object images
    current_dir = os.path.dirname(__file__)
    tiles = read_tiles(os.path.join(current_dir, 'static', 'images', 'tiles'))
    objects = read_objects(os.path.join(current_dir, 'static', 'images', 'objects'))
    objects = read_vehicles(os.path.join(current_dir, 'static', 'images', 'vehicles'), objects)

    # Get Cluster data
    k8s_cluster = dump_data()

    # Arrange districts in the town (calling bin packing algo)
    k8s_cluster.generate(tiles, objects)

    # Generate final map data
    map_data = {
        "tiles": tiles,
        "objects": objects,
        "groundMap": [{"row": r} for r in k8s_cluster.ground_map],
        "objectsMap": [{"row": r} for r in k8s_cluster.objects_map],
        "initialControllableLocation": { "columnIndex": 0, "rowIndex": 0},
    }

    # Write json file
    #with open("html/mapDataIC.json", "w") as fhic:
    #    json.dump(map_data, fhic, indent=4, sort_keys=True)
    return map_data, k8s_cluster


def create_app():
    app = Flask("infracity")
    app.secret_key = b'_gdsg5#y2L"F4Q8z\n\xec]/'
    return app



def main():
    MAP_DATA, K8S_CLUSTER = generate_map()

    app = create_app()

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/vehicles')
    def vehicles():
        map_data = MAP_DATA.copy()
        vehicles_by_town = {}
        for town in K8S_CLUSTER.towns.values():
            vehicles_by_town[town.name] = {}
            for vehicle in town.vehicles.values():
                vehicles_by_town[town.name][vehicle.name] = [{"x": s["x"] + 6, "y": s["y"] + 6} for s in vehicle.stops]
        return vehicles_by_town

    @app.route('/mapdata.json')
    def mapdata():
        map_data = MAP_DATA.copy()
        for tile in map_data['tiles'].values():
            if not tile['path'].startswith('/static/'):
                tile['path'] = url_for("static", filename=tile['path'])
        for obj in map_data['objects'].values():
            for visuals in obj['visuals'].values():
                for frame in visuals['frames']:
                    if not frame['path'].startswith('/static/'):
                        frame['path'] = url_for("static", filename=frame['path'])
        return map_data

    app.run()


if __name__ == "__main__":
    main()
