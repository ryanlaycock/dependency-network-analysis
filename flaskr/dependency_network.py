import network
import networkx as nx
import functions


class DependencyNetwork(network.Network):
    """Class representing a project and it's dependencies and dependents."""

    def __init__(self, project_name):
        # TODO Check if graph exists
        network.Network.__init__(self)
        dependencies = self.__fetch_dependency_data(project_name)
        dependents = self.__fetch_dependent_data(project_name)
        self.neo4j_to_network(dependencies)
        self.neo4j_to_network(dependents)

    def __fetch_dependency_data(self, project_name):
        print(functions.log_time(), "Fetching dependencies.")
        # Dependencies
        query = ("MATCH p = (parent:Project{id:$projectName})"
                 "-[:Contains*0..1]->(child:Artifact)"
                 "-[:Depends*0..2]->(dep:Artifact) " + self.query_end)

        with self.db_driver.session() as session:
            result = session.run(query, parameters={"projectName": project_name})
            return result.records()

    def __fetch_dependent_data(self, project_name):
        print(functions.log_time(), "Fetching dependents.")
        # Dependent projects
        query = ("MATCH p = (parent:Project{id:$projectName})"
                 "-[:Contains*0..1]->(child:Artifact)"
                 "<-[:Depends*0..1]-(dep:Artifact)" + self.query_end)

        with self.db_driver.session() as session:
            result = session.run(query, parameters={"projectName": project_name})
            return result.records()

    def get_artifacts(self):
        project_node = self.get_project_node()
        if project_node is None:
            print(functions.log_time(), "Error: project node not found")
            return
        project_artifacts = nx.ego_graph(self.graph, project_node[0], center=False)
        # Graph of all artifacts, without the project node (all relations should be "Depends")
        graph_of_artifacts_only = nx.ego_graph(self.graph, project_node[0], center=False, undirected=True, radius=100)
        reversed_graph = graph_of_artifacts_only.reverse()
        direct_dependencies = {}
        transitive_dependencies = {}
        dependents = {}
        project_artifact_details = {}

        # Search through direct dependencies and dependents
        for project_artifact in project_artifacts:
            project_artifact_details[project_artifact] = self.graph.nodes[project_artifact]
            project_artifact_details[project_artifact]["internal_id"] = project_artifact
            if self.graph.nodes[project_artifact]["type"] == "Artifact":
                # Outgoing nodes from artifact (dependencies)
                artifact_dependencies = nx.ego_graph(self.graph, project_artifact, center=False, radius=1)
                # Direct dependencies
                for artifact_dependency in artifact_dependencies:
                    if self.graph.nodes[artifact_dependency]["type"] == "Artifact" \
                            and artifact_dependency not in direct_dependencies \
                            and artifact_dependency not in project_artifacts:
                        direct_dependencies[artifact_dependency] = self.graph.nodes[artifact_dependency]
                        direct_dependencies[artifact_dependency]["internal_id"] = artifact_dependency

                # Incoming nodes into artifact (dependents)
                artifact_dependents = nx.ego_graph(reversed_graph, project_artifact)
                for artifact_dependent in artifact_dependents:
                    if self.graph.nodes[artifact_dependent]["type"] == "Artifact" \
                            and artifact_dependent not in dependents:
                        dependents[artifact_dependent] = self.graph.nodes[artifact_dependent]
                        dependents[artifact_dependent]["internal_id"] = artifact_dependent

        # Search all nodes for nodes not direct dependency or project artifact
        for artifact in graph_of_artifacts_only:
            if self.graph.nodes[artifact]["type"] == "Artifact" and artifact not in direct_dependencies \
                    and artifact not in project_artifact_details and artifact not in dependents:
                transitive_dependencies[artifact] = self.graph.nodes[artifact]
                transitive_dependencies[artifact]["internal_id"] = artifact

        return {
            "Artifact": project_artifact_details,
            "DirectDependency": direct_dependencies,
            "TransitiveDependency": transitive_dependencies,
            "Dependent": dependents,
        }
