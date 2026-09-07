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
        connections = list( 
            graph.neighbors(entity)
        )
        total_connections = len(connections)
        communication = 0
        financial = 0
        location = 0

        for neighbor in connections:
            relationship = graph[entity] [neighbor].get( "relationship","")

            if relationship == "Communication":
                communication += 1
            elif relationship == "Financial": 
                financial += 1
            elif relationship == "Location": 
                location += 1

                # Explainable priority indicator
                score = (total_connections * 5+communication *3+financial * 4+location * 2)

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
