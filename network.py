import pandas as pd 
import networkx as nx

def create_network(file_path):
    data = pd.read_csv(file_path)
    graph = nx.Graph()
    for _, row in data.iterrows():
        source = row["source"]
        target = row["target"]
        relationship=row["type"]
        graph.add_node(source) 
        graph.add_node(target)
        graph.add_edge(
            source,
            target,
            relationship=relationship
        )
    return graph
def get_entity_type(entity):
    if (entity.startswith("Person_")): 
        return "Person"
    elif (entity.startswith("Phone_")):
        return "Phone"
    elif (entity.startswith("Bank_")): 
        return "Bank"
    elif (entity.startswith("Location_")):
        return "Location"
    else:
        return "Unknown"

def calculate_priority(graph):
    results = []

    for entity in graph.nodes():

        connections = list(graph.neighbors(entity))

        total_connections = len(connections)

        communication = 0
        financial = 0
        location = 0

        for neighbor in connections:

            edge_data = graph[entity][neighbor]

            # New unified network stores all relationship types here
            relationships = edge_data.get("relationships", [])

            # Backward compatibility with old graph format
            if not relationships:
                relationship = edge_data.get("relationship", "")
                relationships = [relationship]

            if "Communication" in relationships:
                communication += 1

            if "Financial" in relationships:
                financial += 1

            if "Location" in relationships:
                location += 1

        # Explainable priority indicator
        score = (
            total_connections * 5
            + communication * 3
            + financial * 4
            + location * 2
        )

        results.append({
            "Entity": entity,
            "Type": get_entity_type(entity),
            "Connections": total_connections,
            "Communication": communication,
            "Financial": financial,
            "Location": location,
            "Priority Score": score
        })

    return pd.DataFrame(results)
def calculate_importance(graph):
    importance = nx.degree_centrality(graph)
    return importance
