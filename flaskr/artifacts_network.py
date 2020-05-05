import network
import networkx as nx
import functions


class ArtifactsNetwork(network.Network):
    """Class representing a project and it's dependencies."""

    def __init__(self):
        # TODO Check if graph exists
        network.Network.__init__(self)
        records = self.__fetch_data()
        self.neo4j_to_network_artifact(records)
        print(functions.log_time(), "Fetched data and built graph.")
        self.__page_rank = self.compute_pagerank()
        print(functions.log_time(), "Calculated pagerank.")

    def __fetch_data(self):
        print(functions.log_time(), "Fetching artifacts")
        query = ("MATCH p=(:Artifact)"
                 "UNWIND nodes(p) as allnodes WITH COLLECT(ID(allnodes)) AS ALLID "
                 "MATCH (a)-[r2]-(b) "
                 "WHERE ID(a) IN ALLID AND ID(b) IN ALLID "
                 "WITH DISTINCT r2 "
                 "RETURN id(startNode(r2)), type(r2), id(endNode(r2))")
        with self.db_driver.session() as session:
            result = session.run(query)
            return result.records()

    def compute_pagerank(self):
        artifacts = {}
        pagerank = nx.pagerank(self.graph)
        sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)  # Sort descending
        rank = 0
        last_rank_val = None
        for id, pr in sorted_pagerank:
            if last_rank_val != pagerank[id]:  # Only increment if the pagerank value is different ie. not joint rank
                rank += 1
            last_rank_val = pagerank[id]
            artifacts[id] = {
                "pagerank": pagerank[id],
                "overall_rank": rank,
            }
        return artifacts

    def neo4j_to_network_artifact(self, records):
        """Takes a neo4j result.records and generates a networkx network into self.graph"""
        for record in records:
            self.__add_node_artifact(record[0])  # Add parent/source node
            self.__add_node_artifact(record[2])  # Add child/target node
            self.__add_edge_artifact(record[0], record[1], record[2])  # Add edge

    def __add_node_artifact(self, node):
        self.graph.add_node(node)

    def __add_edge_artifact(self, source_node, relation_type, target_node):
        self.graph.add_edge(source_node, target_node, type=relation_type)
