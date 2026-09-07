import pandas as pd
import networkx as nx


def create_unified_network(
        relationship_file,
        cdr_file,
        transaction_file,
        location_file
):
    graph = nx.Graph()

    # -----------------------
    # Helper function
    # -----------------------
    def add_relationship(source, target, relationship):

        source = str(source).strip()
        target = str(target).strip()
        relationship = str(relationship).strip()

        graph.add_node(source)
        graph.add_node(target)

        if graph.has_edge(source, target):

            # Keep all relationship types
            existing = graph[source][target].get("relationships", [])

            if relationship not in existing:
                existing.append(relationship)

            graph[source][target]["relationships"] = existing

        else:

            graph.add_edge(
                source,
                target,
                relationship=relationship,
                relationships=[relationship]
            )

    # -----------------------
    # 1. General relationships
    # -----------------------

    relationships = pd.read_csv(relationship_file)
    relationships.columns = relationships.columns.str.strip()

    for _, row in relationships.iterrows():

        source = row["source"]
        target = row["target"]
        relationship = row["type"]

        add_relationship(
            source,
            target,
            relationship
        )

    # -----------------------
    # 2. CDR relationships
    # -----------------------

    cdr = pd.read_csv(cdr_file)
    cdr.columns = cdr.columns.str.strip()

    for _, row in cdr.iterrows():

        caller = row["caller"]
        receiver = row["receiver"]

        add_relationship(
            caller,
            receiver,
            "Communication"
        )

    # -----------------------
    # 3. Financial relationships
    # -----------------------

    transactions = pd.read_csv(transaction_file)
    transactions.columns = transactions.columns.str.strip()

    for _, row in transactions.iterrows():

        sender = row["sender"]
        receiver = row["receiver"]

        add_relationship(
            sender,
            receiver,
            "Financial"
        )

    # -----------------------
    # 4. Location relationships
    # -----------------------

    locations = pd.read_csv(location_file)
    locations.columns = locations.columns.str.strip()

    for _, row in locations.iterrows():

        person = row["person"]
        location = row["location"]

        add_relationship(
            person,
            location,
            "Location"
        )

    return graph


def get_entity_type(entity):

    if entity.startswith("Person_"):
        return "Person"

    elif entity.startswith("Phone_"):
        return "Phone"

    elif entity.startswith("Bank_"):
        return "Bank"

    elif entity.startswith("Location_"):
        return "Location"

    else:
        return "Other"
