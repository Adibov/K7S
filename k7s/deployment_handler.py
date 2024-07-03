from flask import request, jsonify
from kubernetes import config, client
from kubernetes.client import ApiException

from main import app, blueprint


# @app.route('/deployment-status', methods=['GET'])
def get_status(request):
    deployment_name = request.args.get('name')
    namespace = 'default'

    config.load_kube_config()
    api_instance = client.AppsV1Api()

    try:
        deployment = api_instance.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            return jsonify({"message": f"Deployment {deployment_name} not found"}), 404
        else:
            return jsonify({"message": "Failed to get deployment status", "error": str(e)}), 500

    core_v1_api = client.CoreV1Api()
    pod_list = core_v1_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")

    pod_statuses = []
    for pod in pod_list.items:
        pod_info = {
            "Name": pod.metadata.name,
            "Phase": pod.status.phase,
            "HostIP": pod.status.host_ip if pod.status.host_ip else "",
            "PodIP": pod.status.pod_ip if pod.status.pod_ip else "",
            "StartTime": pod.status.start_time.isoformat() if pod.status.start_time else ""
        }
        pod_statuses.append(pod_info)

    response = {
        "DeploymentName": deployment.metadata.name,
        "Replicas": deployment.spec.replicas,
        "ReadyReplicas": deployment.status.ready_replicas if deployment.status.ready_replicas else 0,
        "PodStatuses": pod_statuses
    }

    return jsonify(response), 200


# @app.route('/deployment-statuses', methods=['GET'])
def get_all_statuses(request):
    namespace = 'default'

    config.load_kube_config()
    api_instance = client.AppsV1Api()

    try:
        deployments = api_instance.list_namespaced_deployment(namespace=namespace)
    except ApiException as e:
        return jsonify({"message": "Failed to get deployments", "error": str(e)}), 500

    core_v1_api = client.CoreV1Api()
    all_statuses = []

    for deployment in deployments.items:
        app_name = deployment.metadata.name
        pod_list = core_v1_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={app_name}")

        pod_statuses = []
        for pod in pod_list.items:
            pod_info = {
                "Name": pod.metadata.name,
                "Phase": pod.status.phase,
                "HostIP": pod.status.host_ip if pod.status.host_ip else "",
                "PodIP": pod.status.pod_ip if pod.status.pod_ip else "",
                "StartTime": pod.status.start_time.isoformat() if pod.status.start_time else ""
            }
            pod_statuses.append(pod_info)

        deployment_status = {
            "DeploymentName": deployment.metadata.name,
            "Replicas": deployment.spec.replicas,
            "ReadyReplicas": deployment.status.ready_replicas if deployment.status.ready_replicas else 0,
            "PodStatuses": pod_statuses
        }
        all_statuses.append(deployment_status)

    return jsonify(all_statuses), 200
