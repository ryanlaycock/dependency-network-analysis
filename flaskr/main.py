from flask import Flask, request, jsonify
from flask_cors import CORS
import artifacts_network
import dependency_network

app = Flask(__name__)
"""Flask URL -> endpoints"""
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
        return jsonify(""), 404
    artifacts = artifact_deps.get_artifacts()
    return jsonify(artifacts), 200


if __name__ == '__main__':
    print("Starting dependency network analysis!")
    app.run(host='0.0.0.0', debug=True)
