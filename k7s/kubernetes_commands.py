from kubernetes import client
from kubernetes.client import ApiException


def create_or_replace_secret(api_instance, secret_name, namespace, secret_data):
    body = client.V1Secret(
        metadata=client.V1ObjectMeta(name=secret_name),
        data=secret_data,
        type='Opaque'
    )
    try:
        api_instance.replace_namespaced_secret(secret_name, namespace, body)
        print(f"Secret {secret_name} replaced successfully.")
    except ApiException as e:
        if e.status == 404:
            api_instance.create_namespaced_secret(namespace, body)
            print(f"Secret {secret_name} created successfully.")
        else:
            raise


def create_or_replace_deployment(app_name, image, image_tag, replicas, namespace, envs, resources, monitor=True):
    container = client.V1Container(
        name=app_name,
        image=f"{image}:{image_tag}",
        ports=[client.V1ContainerPort(container_port=80)],
        env=[client.V1EnvVar(name=k, value=v) for k, v in envs.items()],
        resources=client.V1ResourceRequirements(
            limits=resources
        )
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": app_name, "monitor": "false" if not monitor else "true"}),
        spec=client.V1PodSpec(containers=[container])
    )

    spec = client.V1DeploymentSpec(
        replicas=replicas,
        template=template,
        selector={'matchLabels': {"app": app_name}}
    )

    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=app_name),
        spec=spec
    )

    api_instance = client.AppsV1Api()
    try:
        api_instance.create_namespaced_deployment(
            namespace=namespace,
            body=deployment
        )
        print(f"Deployment {app_name} created successfully.")
    except ApiException as e:
        if e.status == 409:  # Conflict
            print(f"Deployment {app_name} already exists. Replacing it...")
            api_instance.replace_namespaced_deployment(
                name=app_name,
                body=deployment,
                namespace=namespace
            )
        else:
            raise


def create_or_replace_service(service_name, namespace, service_port, service_type="ClusterIP"):
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector={"app": service_name},
            ports=[client.V1ServicePort(port=service_port, target_port=service_port)],
            type=service_type
        )
    )
    api_instance = client.CoreV1Api()
    try:
        api_instance.create_namespaced_service(namespace, body)
        print(f"Service {service_name} created successfully.")
    except ApiException as e:
        if e.status == 409:  # Conflict
            print(f"Service {service_name} already exists. Replacing it...")
            api_instance.replace_namespaced_service(
                name=service_name,
                namespace=namespace,
                body=body
            )
        else:
            raise


def create_or_replace_ingress(ingress_name, namespace, domain_address, service_name, service_port):
    path = client.V1HTTPIngressPath(
        path="/",
        path_type="ImplementationSpecific",
        backend=client.V1IngressBackend(
            service=client.V1IngressServiceBackend(
                name=service_name,
                port=client.V1ServiceBackendPort(number=service_port)
            )
        )
    )

    rule = client.V1IngressRule(
        host=domain_address,
        http=client.V1HTTPIngressRuleValue(paths=[path])
    )

    spec = client.V1IngressSpec(rules=[rule], ingress_class_name="nginx")

    body = client.V1Ingress(
        metadata=client.V1ObjectMeta(name=ingress_name),
        spec=spec
    )

    api_instance = client.NetworkingV1Api()
    try:
        api_instance.create_namespaced_ingress(namespace=namespace, body=body)
        print(f"Ingress {ingress_name} created successfully.")
    except ApiException as e:
        if e.status == 409:  # Conflict
            print(f"Ingress {ingress_name} already exists. Replacing it...")
            api_instance.replace_namespaced_ingress(
                name=ingress_name,
                namespace=namespace,
                body=body
            )
        else:
            raise


def create_or_replace_configmap(api_instance, configmap_name, namespace, config_data):
    body = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name=configmap_name),
        data=config_data
    )
    try:
        api_instance.create_namespaced_config_map(namespace, body)
        print(f"ConfigMap {configmap_name} created successfully.")
    except ApiException as e:
        if e.status == 409:
            print(f"ConfigMap {configmap_name} already exists. Replacing it...")
            api_instance.replace_namespaced_config_map(configmap_name, namespace, body)
        else:
            raise
