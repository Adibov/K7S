import base64
import random
import string

from flask import jsonify
from kubernetes import config, client
from kubernetes.client import ApiException

from kubernetes_commands import create_or_replace_secret, create_or_replace_configmap, create_or_replace_service


def deploy_postgresql(app_name, resources, external_access, namespace='default'):
    config.load_kube_config()

    core_v1_api = client.CoreV1Api()
    apps_v1_api = client.AppsV1Api()

    username = 'admin'
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    secret_data = {
        'username': base64.b64encode(username.encode('utf-8')).decode('utf-8'),
        'password': base64.b64encode(password.encode('utf-8')).decode('utf-8')
    }
    create_or_replace_secret(core_v1_api, f"{app_name}-secret", namespace, secret_data)

    # Create ConfigMap
    config_data = {
        'postgresql.conf': """
        # PostgreSQL configuration file
        shared_buffers = 128MB
        max_connections = 100
        """
    }
    create_or_replace_configmap(core_v1_api, f"{app_name}-configmap", namespace, config_data)

    # Create StatefulSet
    container = client.V1Container(
        name=app_name,
        image="postgres:latest",
        ports=[client.V1ContainerPort(container_port=5432)],
        env=[
            client.V1EnvVar(name='POSTGRES_USER', value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name=f"{app_name}-secret", key='username'))),
            client.V1EnvVar(name='POSTGRES_PASSWORD', value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name=f"{app_name}-secret", key='password')))
        ],
        resources=client.V1ResourceRequirements(
            limits=resources
        ),
        volume_mounts=[
            client.V1VolumeMount(name='config-volume', mount_path='/etc/postgresql/postgresql.conf',
                                 sub_path='postgresql.conf')
        ]
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": app_name}),
        spec=client.V1PodSpec(containers=[container], volumes=[
            client.V1Volume(name='config-volume',
                            config_map=client.V1ConfigMapVolumeSource(name=f"{app_name}-configmap"))
        ])
    )

    spec = client.V1StatefulSetSpec(
        service_name=app_name,
        replicas=1,
        selector={'matchLabels': {"app": app_name}},
        template=template,
    )

    statefulset = client.V1StatefulSet(
        api_version="apps/v1",
        kind="StatefulSet",
        metadata=client.V1ObjectMeta(name=app_name),
        spec=spec
    )

    try:
        apps_v1_api.create_namespaced_stateful_set(namespace=namespace, body=statefulset)
        print(f"StatefulSet {app_name} created successfully.")
    except ApiException as e:
        if e.status == 409:
            print(f"StatefulSet {app_name} already exists. Replacing it...")
            apps_v1_api.replace_namespaced_stateful_set(name=app_name, namespace=namespace, body=statefulset)
        else:
            raise

    create_or_replace_service(app_name, namespace, 5432)


def deploy_postgres(request):
    data = request.get_json()

    app_name = data["AppName"]
    resources = {"cpu": data["Resources"]["cpu"], "memory": data["Resources"]["memory"]}
    external_access = data.get("External", False)

    try:
        deploy_postgresql(
            app_name=app_name,
            resources=resources,
            external_access=external_access
        )
        response = {"message": "PostgreSQL deployment started successfully."}
        return jsonify(response), 200
    except ApiException as e:
        response = {"message": "PostgreSQL deployment failed.", "error": str(e)}
        return jsonify(response), 500
