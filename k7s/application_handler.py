import base64

from flask import request, jsonify
from kubernetes import config, client
from kubernetes.client import ApiException

from kubernetes_commands import create_or_replace_secret, create_or_replace_deployment, create_or_replace_service, \
    create_or_replace_ingress
from main import app, blueprint


def deploy_application(app_name, replicas, image_address, image_tag, domain_address, service_port, resources, envs,
                       secrets, external_access, namespace='default'):
    app_name = app_name.lower()
    config.load_kube_config()

    core_v1_api = client.CoreV1Api()

    if secrets:
        try:
            create_or_replace_secret(core_v1_api, f"{app_name}-secret", namespace, secrets)
        except ApiException as e:
            if e.status == 409:
                print(f"Secret {app_name}-secret already exists.")
            else:
                raise

    try:
        create_or_replace_deployment(app_name, image_address, image_tag, replicas, namespace, envs, resources)
    except ApiException as e:
        if e.status == 409:
            print(f"Deployment {app_name} already exists.")
        else:
            raise

    try:
        create_or_replace_service(app_name, namespace, service_port)
    except ApiException as e:
        if e.status == 409:
            print(f"Service {app_name} already exists.")
        else:
            raise

    if external_access:
        try:
            create_or_replace_ingress(f"{app_name}-ingress", namespace, domain_address, app_name, service_port)
        except ApiException as e:
            if e.status == 409:
                print(f"Ingress {app_name}-ingress already exists.")
            else:
                raise


# @app.route('/deploy-application', methods=['POST'])
def deploy(request):
    data = request.get_json()

    app_name = data["AppName"]
    replicas = data["Replicas"]
    image_address = data["ImageAddress"]
    image_tag = data["ImageTag"]
    domain_address = data["DomainAddress"]
    service_port = data["ServicePort"]
    resources = {"cpu": data["Resources"]["CPU"], "memory": data["Resources"]["RAM"]}

    envs = {}
    secrets = {}
    for env in data["Envs"]:
        if env["IsSecret"] == 'True':
            encoded_value = base64.b64encode(env["Value"].encode('utf-8')).decode('utf-8')
            secrets[env["Key"]] = encoded_value
        else:
            envs[env["Key"]] = env["Value"]

    external_access = True

    deploy_application(
        app_name=app_name,
        replicas=replicas,
        image_address=image_address,
        image_tag=image_tag,
        domain_address=domain_address,
        service_port=service_port,
        resources=resources,
        envs=envs,
        secrets=secrets,
        external_access=external_access
    )

    return jsonify({"message": "Application deployed successfully"}), 200
