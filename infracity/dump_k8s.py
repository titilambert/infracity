import re
import math
import random

from kubernetes import client, config
from rectpack import newPacker, PackingMode
import rectpack.maxrects as maxrects

#from arrange import arrange_island
#from read_images import get_tile_id, get_object_id

from infracity.island import Island
from infracity.town import Town
from infracity.block import Block
from infracity.building import Building
from infracity.floor import Floor
from infracity.vehicle import Vehicle


def get_secrets(workload_spec, block):
    # search for secrets:
    for container in workload_spec.template.spec.containers:
        if container.env:
            for env in container.env:
                if hasattr(env.value_from, "secret_key_ref") and env.value_from.secret_key_ref:
                    secret_name = env.value_from.secret_key_ref.name
                    if secret_name in block.vehicles:
                        vehicle = block.vehicles[secret_name]
                    else:
                        vehicle = Vehicle(secret_name, "ambulance", "bank")
                    block.vehicles[secret_name] = vehicle

    if workload_spec.template.spec.volumes:
        for volume in workload_spec.template.spec.volumes:
            if volume.secret:
                secret_name = volume.secret.secret_name
                if secret_name in block.vehicles:
                    vehicle = block.vehicles[secret_name]
                else:
                    vehicle = Vehicle(secret_name, "ambulance", "bank")
                block.vehicles[secret_name] = vehicle


def dump_data():
    """Collect all needed data from k8s."""

    config.load_kube_config()

    v1 = client.CoreV1Api()
    appsv1 = client.AppsV1Api()

    namespaces = v1.list_namespace()
    pods = v1.list_pod_for_all_namespaces()
    secrets = v1.list_secret_for_all_namespaces()
    #service_accounts = v1.list_service_account_for_all_namespaces()
    #services = v1.list_service_for_all_namespaces()
    #config_maps = v1.list_config_map_for_all_namespaces()
    #pvs = v1.list_persistent_volume()
    #pvcs = v1.list_persistent_volume_claim_for_all_namespaces()

    daemonsets = appsv1.list_daemon_set_for_all_namespaces()
    deployments = appsv1.list_deployment_for_all_namespaces()
    #replica_sets = appsv1.list_replica_set_for_all_namespaces()
    statefulsets = appsv1.list_stateful_set_for_all_namespaces()

    k8s_cluster = Island("Kubernetes", {})
    for namespace in namespaces.items:
        k8s_cluster.towns[namespace.metadata.name] = Town(namespace.metadata.name)

    for deployment in deployments.items:
        block = Block(deployment.metadata.name, "deployment", "red")
        get_secrets(deployment.spec, block)
        k8s_cluster.towns[deployment.metadata.namespace].blocks[deployment.metadata.name] = block
    for daemonset in daemonsets.items:
        block = Block(daemonset.metadata.name, "daemonset", "brown")
        get_secrets(daemonset.spec, block)
        k8s_cluster.towns[daemonset.metadata.namespace].blocks[daemonset.metadata.name] = block
    for statefulset in statefulsets.items:
        block = Block(statefulset.metadata.name, "statefulset", "yellow")
        get_secrets(statefulset.spec, block)
        k8s_cluster.towns[statefulset.metadata.namespace].blocks[statefulset.metadata.name] = block

    for pod in pods.items:
        # TODO capture pod status to put fire if there is an error
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
        elif pod.metadata.owner_references[0].kind == 'StatefulSet':
            owner_name = pod.metadata.owner_references[0].name
        else:
            continue
        k8s_cluster.towns[pod.metadata.namespace].blocks[owner_name].buildings[pod.metadata.name] = building

    return k8s_cluster
