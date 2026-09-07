def generate_investigation_summary(entity, graph):

    if entity not in graph:
        return "Entity not found."

    connections = list(graph.neighbors(entity))

    total_connections = len(connections)

    communication = []
    financial = []
    locations = []
    other = []

    for connection in connections:

        edge_data = graph[entity][connection]

        # Get all relationship types
        relationships = edge_data.get(
            "relationships",
            [edge_data.get("relationship", "Unknown")]
        )

        for relationship in relationships:

            relationship = str(relationship).strip()

            if relationship == "Communication":

                if connection not in communication:
                    communication.append(connection)

            elif relationship == "Financial":

                if connection not in financial:
                    financial.append(connection)

            elif relationship == "Location":

                if connection not in locations:
                    locations.append(connection)

            else:

                if connection not in other:
                    other.append(connection)

    summary = f"""
### 🤖 Investigation Summary: {entity}

**Entity:** {entity}

**Total direct connections:** {total_connections}

**Communication relationships:** {len(communication)}

**Financial relationships:** {len(financial)}

**Location relationships:** {len(locations)}
"""

    if communication:

        summary += "\n**📞 Communication connections:**\n"

        for person in communication:
            summary += f"- {person}\n"

    if financial:

        summary += "\n**💰 Financial connections:**\n"

        for person in financial:
            summary += f"- {person}\n"

    if locations:

        summary += "\n**📍 Location associations:**\n"

        for location in locations:
            summary += f"- {location}\n"

    if other:

        summary += "\n**🔗 Other relationships:**\n"

        for connection in other:
            summary += f"- {connection}\n"

    summary += """

### ⚠️ Review Guidance

This analysis identifies relationships
present in the supplied dataset.

It does not establish criminality,
guilt, intent, or wrongdoing.

Investigators should review the
underlying authorized source records
before drawing conclusions.
"""

    return summary
