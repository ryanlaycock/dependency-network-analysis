from flask import Flask, request, jsonify
from flask_cors import CORS
import artifacts_network
import dependency_network
import time


def create_app(test_config=None):
    """Flask URL -> endpoints"""
    app = Flask(__name__)
    CORS(app)

    # Routes
    @app.route('/artifacts/pageranks', methods=['GET'])
    def get_pagerank():
        artifacts = artifacts_network.ArtifactsNetwork()
        artifacts_pagerank = artifacts.compute_pagerank()
        if artifacts is not None:
            return jsonify(artifacts_pagerank), 200
        return 500

    @app.route('/artifacts/<string:owner>/<string:repo>', methods=['GET'])
    def get_project_artifacts(owner, repo):
        project_name = owner + "/" + repo
        artifact_deps = dependency_network.DependencyNetwork(project_name)
        if artifact_deps.is_empty():
            return 404
        artifacts = artifact_deps.get_artifacts()
        return jsonify(artifacts), 200

    return app


if __name__ == '__main__':
    flask_app = create_app()
    flask_app.debug = True
    flask_app.run(host='0.0.0.0', port=5001)
