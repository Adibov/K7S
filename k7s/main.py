from flask import Flask, jsonify, request, Blueprint

app = Flask(__name__)
blueprint = Blueprint('blueprint', __name__)


@app.route('/health', methods=['GET'])
def get_health():
    return jsonify("OK", 200)


@app.route('/deploy-application', methods=['POST'])
def deploy_application():
    return application_handler.deploy(request)


@app.route('/deployment-status', methods=['GET'])
def deployment_status():
    return deployment_handler.get_status(request)


@app.route('/deployment-statuses', methods=['GET'])
def deployment_statuses():
    return deployment_handler.get_all_statuses(request)


@app.route('/deploy-postgres', methods=['POST'])
def deploy_postgres():
    return postgresql_handler.deploy_postgres(request)


if __name__ == '__main__':
    with app.app_context():
        import application_handler, deployment_handler, postgresql_handler
    app.run(host='0.0.0.0', port=5000, debug=True)
