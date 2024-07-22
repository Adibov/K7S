# K7S - A minimal Kubernetes as service

This project provides a set of Python scripts to handle Kubernetes deployments, specifically for PostgreSQL. It uses the Kubernetes Python client to interact with a Kubernetes cluster.

## Installation

To install the project, you need to have Python and pip installed on your system. Once you have those, you can install the project dependencies with:

```bash
pip install -r requirements.txt
```

## Usage/Examples

This project provides several APIs for handling Kubernetes deployments. Here are some examples:
- Get the status of a deployment
- Get the status of all deployments
- Deploy a PostgreSQL instance
- Deploy an application on the fly

The usage of each function can be found in the PostMan collection provided in the `K7S.postman_collection.json` file.

## Deployment

This project is intended to be run on a system with access to a Kubernetes cluster. You will need to configure your Kubernetes client to point to the cluster you want to interact with.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
