import re
import math

from kubernetes import client, config

from arrange import arrange_town
from read_images import get_tile_id, get_object_id


class Island:

    def __init__(self, name, towns):
        self.name = name
        self.towns = towns

    @property
    def surface(self):
        return self.dimensions["x"] * self.dimensions["y"]

    @property
    def dimensions(self):
        dim = {"x": None, "y": None}
        town_surface = sum([(math.sqrt(t.surface) + 2) ** 2 for t in self.towns.values()])
        dim["x"] = dim["y"] = int(math.sqrt(town_surface)) + 3
        return dim

    def draw(self):
        groundMap = []
        for row in range(self.dimensions["x"]):
            column = ["0"] * self.dimensions["y"]
            groundMap.append({"row": column})
        return groundMap


class Town:
    """Namespace."""

    def __init__(self, name):
        self.name = name
        self.districts = {}
        self._ground_map = []
        self._objects_map = []
        self._district_packing = []

    @property
    def surface(self):
        # Need to do a calculation to add more empty green tiles around the town
        return sum([d.surface for d in self.districts.values()])
    
    @property
    def ground_map(self):
        return self._ground_map

    @property
    def objects_map(self):
        return self._objects_map

    @property
    def dimensions(self):
        dim = {"x": None, "y": None}
        dim["x"] = max(sum(max([(tc[1], tc[3]) for tc in self._district_packing])), sum(max([(tc[3], tc[1]) for tc in self._district_packing])))
        dim["y"] = max(sum(max([(tc[2], tc[4]) for tc in self._district_packing])), sum(max([(tc[4], tc[2]) for tc in self._district_packing])))
        return dim

    def arrange(self, tile_list, object_list):
        self._district_packing = arrange_town(self)

        for column in range(self.dimensions["x"]):
            self._ground_map.append([0 for i in range(self.dimensions["y"])])
            self._objects_map.append([0 for i in range(self.dimensions["y"])])

        # Place objects and tiles on the groundmap and objectsmap
        for district_data in self._district_packing:
            pos_x = district_data[1]
            pos_y = district_data[2]
            length_x = district_data[3]
            length_y = district_data[4]
            district_name = district_data[-1]
            #print(district_name, length_x, length_y)
            #district = self.districts[district_name]
            for tile_x in range(length_x):
                for tile_y in range(length_y):
                    object_id = None
                    if tile_x == 0 and tile_y == 0:
                        tile_name = "street_corner_right"
                    elif tile_x == 0 and tile_y == length_y - 1:
                        tile_name = "street_corner_bottom"
                    elif tile_x == length_x - 1 and tile_y == 0:
                        tile_name = "street_corner_top"
                    elif tile_x == length_x - 1 and tile_y == length_y - 1:
                        tile_name = "street_corner_left"
                    elif tile_x == 0:
                        tile_name = "street_straight_top"
                    elif tile_x == length_x - 1:
                        tile_name = "street_straight_bottom"
                    elif tile_y == 0:
                        tile_name = "street_straight_left"
                    elif tile_y == length_y - 1:
                        tile_name = "street_straight_right"
                    else:
                        tile_name = "grass_full"
                        if length_x > length_y:
                            object_name = "base_red_left"
                        else:
                            object_name = "base_red_right"
                        object_id = get_object_id(object_list, object_name)

                    if tile_name.startswith("street_"):
                        # TODO check the tiles around the current one (tile_x + pos_x , tile_y + pos_y)
                        # And check if there any other streets to connect the streets together
                        pass

                    tile_id = get_tile_id(tile_list, tile_name)
                    self._ground_map[tile_x + pos_x][tile_y + pos_y] = tile_id
                    if object_id is not None:
                        self._objects_map[tile_x + pos_x][tile_y + pos_y] = object_id

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
        #import ipdb;ipdb.set_trace()

class District:
    """Deployment/DaemonSet/StateFulSet."""

    def __init__(self, name, wtype):
        self.name = name
        self._type = wtype
        self.buildings = {}  # should be equal to replicas

    def type(self):
        return self._type

    @property
    def surface(self):
        return self.dimensions["x"] * self.dimensions["y"]

    @property
    def dimensions(self):
        # Create rectangles with differents width
        # Add calculation to count the routes aroud the district
        dim = {}
        if len(self.buildings) == 1:
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


class Building:
    """Pods."""

    def __init__(self, name):
        self.name = name
        self.floors = {}

    @property
    def size(self):
        return len(self.floors)


class Floor:
    """Container."""
    
    def __init__(self, name, ready, state):
        self.name = name
        self.state = state
        self.ready = ready



def dump_data():
    """Collect all needed data from k8s."""

    config.load_kube_config()

    v1 = client.CoreV1Api()
    appsv1 = client.AppsV1Api()

    namespaces = v1.list_namespace()
    pods = v1.list_pod_for_all_namespaces()
    #secrets = v1.list_secret_for_all_namespaces()
    #service_accounts = v1.list_service_account_for_all_namespaces()
    #services = v1.list_service_for_all_namespaces()
    #config_maps = v1.list_config_map_for_all_namespaces()
    #pvs = v1.list_persistent_volume()
    #pvcs = v1.list_persistent_volume_claim_for_all_namespaces()

    daemonsets = appsv1.list_daemon_set_for_all_namespaces()
    deployments = appsv1.list_deployment_for_all_namespaces()
    #replica_sets = appsv1.list_replica_set_for_all_namespaces()
    #stateful_sets = appsv1.list_stateful_set_for_all_namespaces()

    k8s_cluster = Island("Kubernetes", {})
    for namespace in namespaces.items:
        k8s_cluster.towns[namespace.metadata.name] = Town(namespace.metadata.name)

    for deployment in deployments.items:
        district = District(deployment.metadata.name, "deployment")
        k8s_cluster.towns[deployment.metadata.namespace].districts[deployment.metadata.name] = district
    for daemonset in daemonsets.items:
        district = District(daemonset.metadata.name, "daemonset")
        k8s_cluster.towns[daemonset.metadata.namespace].districts[daemonset.metadata.name] = district

    for pod in pods.items:
        building = Building(pod.metadata.name)
        if not pod.status.container_statuses:
            print("Skipping pod {}/{}".format(pod.metadata.namespace, pod.metadata.name))
            continue

        for container in pod.status.container_statuses:
            floor = Floor(container.name, container.ready, container.state)
            building.floors[container.name] = floor
        if pod.metadata.owner_references is None:
            print("Skipping pod {}/{}".format(pod.metadata.namespace, pod.metadata.name))
            continue
        if pod.metadata.owner_references[0].kind == 'ReplicaSet':
            owner_name = pod.metadata.owner_references[0].name.rsplit("-", 1)[0]
        elif pod.metadata.owner_references[0].kind == 'DaemonSet':
            owner_name = pod.metadata.owner_references[0].name
        else:
            continue
        k8s_cluster.towns[pod.metadata.namespace].districts[owner_name].buildings[pod.metadata.name] = building

    return k8s_cluster
