import re
import math

from kubernetes import client, config

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

    @property
    def surface(self):
        # Need to do a calculation to add more empty green tiles around the town
        return sum([d.surface for d in self.districts.values()])
    
    @property
    def dimensions(self):
        small_districts = 0
        sdx = 0
        sdy = 0
        i = 0
        """
        1 : 3 x 3 
        2 : 3 x 5
        3 : 5 x 5
        4 : 5 x 5
        5 : 5 x 7
        6 : 5 x 7
        7 : 7 x 7
        8 : 7 x 7
        9 : 7 x 7
        10 : 7 x 9
        11 : 7 x 9
        12 : 7 x 9
        12 : 7 x 9
        """
        small_districts = [d for d in self.districts.values() if d.surface == 9]
        # Looking for the next above square
        current = math.sqrt(len(small_districts))
        while math.sqrt(int(current)**2) != current:
            current = int(current) + 1
        sdx = sdy = current + current + 1
        #if math.sqrt(len(small_districts)) == int(math.sqrt(len(small_districts))):
        #    sdx = sdy = math.sqrt(len(small_districts)) + math.sqrt(len(small_districts)) + 1
        #else:
        #    import ipdb;ipdb.set_trace()


        


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
