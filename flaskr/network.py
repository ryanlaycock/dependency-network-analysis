import networkx as nx
import graph_db


class Network:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.db = graph_db.GraphDb()
        self.db_driver = self.db.get_driver()
        self.query_end = ("UNWIND nodes(p) as allnodes WITH COLLECT(ID(allnodes)) AS ALLID "
                          "MATCH (a)-[r2]-(b) "
                          "WHERE ID(a) IN ALLID AND ID(b) IN ALLID "
                          "WITH DISTINCT r2 "
                          "RETURN startNode(r2), type(r2), endNode(r2)")

    def get_stats(self):
        num_of_nodes = self.graph.number_of_nodes()
        num_of_edges = self.graph.number_of_edges()
        num_of_node_types = self.__get_node_count_of_types()
        num_of_edge_types = self.__get_edge_count_of_types()
        return {
            'num_of_nodes': num_of_nodes,
            'num_of_edges': num_of_edges,
            'num_of_node_types': num_of_node_types,
            'num_of_edge_types': num_of_edge_types
        }

    def get_project_node(self):
        for node in self.graph.nodes(data=True):
            if node[1]['type'] == "Project":
                project_node = node
                return project_node
        print("Project node not found")
        return

    def is_empty(self):
        return nx.is_empty(self.graph)

    def neo4j_to_network(self, records):
        """Takes a neo4j result.records and generates a networkx network into self.graph"""
        for record in records:
            self.__add_node(record[0])  # Add parent/source node
            self.__add_node(record[2])  # Add child/target node
            self.__add_edge(record[0], record[1], record[2])  # Add edge

    def __add_node(self, node):
        node_id = node.id
        node_type = list(node.labels)[0]
        if node_type == "Project":
            self.graph.add_node(node_id, id=node["id"], name=node["id"], type=node_type)
        elif node_type == "Artifact":
            self.graph.add_node(node_id, id=node["id"], group=node["group"], artifact=node["artifact"], type=node_type)

    def __add_edge(self, source_node, relation_type, target_node):
        self.graph.add_edge(source_node.id, target_node.id, type=relation_type)

    def add_metrics_to_nodes(self, node_metrics):
        # TODO Add this back in
        return
        # with self.db_driver.session() as session:
        #     for node_id, metric in node_metrics.items():
        #         print("Adding metrics to node id:", node_id)
        #         session.write_transaction(self.__metrics_to_node_tx, node_id, metric)

    def __metrics_to_node_tx(self, tx, node_id, metrics):
        properties = ",".join('{0}:{1}'.format(key, val) for key, val in metrics.items())
        transaction = ("MATCH (n) WHERE id(n)=" + str(node_id) +
                       " SET n += {" + properties + "}")
        return tx.run(transaction)
