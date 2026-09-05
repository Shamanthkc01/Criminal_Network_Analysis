import streamlit as st
import pandas as pd
import networkx as nx
import cv2
import numpy as np
import json
import os
from datetime import datetime
from pyvis.network import Network
from authentication import authenticate
from unified_network import create_unified_network
from network import create_network, get_entity_type, calculate_importance,calculate_priority
from unified_network import create_unified_network,create_unified_network,get_entity_type
from ai_analysis import generate_investigation_summary
import base64
import requests
import streamlit as st


GITHUB_REPO = "Shamanthkc01/Criminal_Network_Analysis"
GITHUB_FILE = "cases.json"
GITHUB_BRANCH = "main"


def save_cases_to_github(cases):
    """Save the latest cases.json directly to GitHub."""

    token = st.secrets["GITHUB_TOKEN"]

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/contents/{GITHUB_FILE}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # Get current file information
    response = requests.get(
        url,
        headers=headers,
        params={"ref": GITHUB_BRANCH}
    )

    if response.status_code != 200:
        st.error(
            f"❌ Could not access cases.json on GitHub: "
            f"{response.status_code}"
        )
        return False

    file_data = response.json()
    sha = file_data["sha"]

    # Convert cases to JSON
    json_content = json.dumps(
        cases,
        indent=4,
        ensure_ascii=False
    )

    encoded_content = base64.b64encode(
        json_content.encode("utf-8")
    ).decode("utf-8")

    # Update GitHub
    update_data = {
        "message": "Update cases.json from Streamlit",
        "content": encoded_content,
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    update_response = requests.put(
        url,
        headers=headers,
        json=update_data
    )

    if update_response.status_code in [200, 201]:
        return True

    st.error(
        f"❌ GitHub update failed: "
        f"{update_response.status_code}"
    )

    return False
st.set_page_config(
    page_title="Criminal Network AI",
    page_icon="",
    layout="wide"
    )

def log_activity(case_id, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.activity_log.append(
        f"[{timestamp}][Case {case_id}] {message}"
    )
# --------------------------------------------------
# LOGIN SYSTEM
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""


if not st.session_state.authenticated:

    st.title("🔐 Secure Investigation Portal")

    st.write(
        "Authorized access only"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )
    if st.button("Login"):

        role = authenticate(
            username,
            password
        )

        if role:

            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = role

            st.success(
                "Login successful!"
            )

            st.rerun()

        else:

            st.error(
            "Invalid username or password."
        )
    st.stop()

st.write(f"logged in as: **{st.session_state.username}**"
         f"| Role: **{st.session_state.role}**")
if st.sidebar.button(" Logout"):
    st.session_state.authenticated=False
    st.session_state.username = ""
    st.session_state.role = ""

    st.rerun()
st.title(" AI-Powered Criminal Network Analysis System")
st.write("Smart India Hackathon 2026 | Problem Statement 26189")
st.divider()
st.header("Investigation Dashboard")

# Load sample data 
file_path = "data/relationships.csv"
data = pd.read_csv(file_path)

# Count different entities
persons = set()
for value in data["source"]:
    if value.startswith("Person_"): 
        persons.add(value)

for key in data["target"]: 
    if key.startswith("Person_"): 
        persons.add(value)

phone_records = len(
    data[data["type"] == "Phone"]
)
financial_links = len( 
    data[data["type"] == "Financial"]
)
locations = len( 
    data[data["type"] == "Location"]
)
# Dashboard statistics 
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Persons", len(persons))
with col2: 
    st.metric("Phone Records", phone_records)
with col3:
    st.metric("Financial Links", financial_links)
with col4:
    st.metric("Locations", locations)
st.divider()

# Display investigation data
st.subheader(" Investigation Relationships")
st.dataframe(
    data,
    use_container_width=True
)
st.divider()
st.subheader(" Upload Investigation Data")
uploaded_file = st.file_uploader( 
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    uploaded_data = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    st.dataframe( 
        uploaded_data,
        use_container_width=True
)
else:
    st.info("You can upload your own authorized investigation datasets")

st.divider()
st.subheader(" Entity Analysis")

graph = create_network(file_path)
importance = calculate_importance(graph)
entity_list = sorted(graph.nodes())
selected_entity = st.selectbox(
    "Select an entity to investigate", 
    entity_list
)

entity_type = get_entity_type(selected_entity)
connections = list(graph.neighbors(selected_entity))
score = importance[selected_entity] * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Entity", selected_entity)

with col2: 
    st.metric("Type", entity_type)
with col3:
    st.metric(
        "Connections",
          len(connections)
    )

st.write("###  Network Importance Score")

st.progress( min(int(score), 100))
st.write(f"Importance score: {score:.1f}/100")
st.write("NETWORK IMPORTANT SCORE")
st.write ("• 0-20 : Low network importance")
st.write("• 20-50 : Moderate")

st.write("### Direct Connections")
if connections:
    for connection in connections:
        relationship = graph[selected_entity][connection][ "relationship"]
        st.write( f"**{connection}** - {relationship}")
else:
    st.info("No direct connections found.")

st.subheader(" Criminal Network Graph")
graph = create_network(file_path)
network = Network(
    height="600px",
    width="100%", 
    bgcolor="#111111", 
    font_color="white"
)
network.from_nx(graph)
network.save_graph("network.html")
with open("network.html", "r", encoding="utf-8") as file: 
    html = file.read()

st.components.v1.html(
    html,
    height=620,
    scrolling=True
)
st.divider()

st.subheader(" CDR Communication Analysis")
cdr_file = "data/cdr.csv"
cdr = pd.read_csv(cdr_file)
# Convert date column
cdr["date"] = pd.to_datetime(cdr["date"])
cdr.columns=cdr.columns.str.strip()

# Basic statistics 
total_calls = len(cdr)
total_duration = cdr["duration"].sum()
unique_callers = cdr["caller"].nunique()
unique_receivers = cdr["receiver"].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Calls",total_calls)
with col2:
    st.metric( "Total Duration", f"{total_duration} sec")
with col3:
    st.metric("Unique Callers",unique_callers)
with col4:
    st.metric("Unique Receivers",unique_receivers)

st.write("###Communication Records")

st.dataframe(cdr,use_container_width=True)

# Communication frequency 
communication_frequency = ( 
    cdr.groupby(
        ["caller", "receiver"]
        )
        .size()
        .reset_index( 
            name="call_count"
            )
        .sort_values( 
            "call_count",
            ascending=False
        )
)
st.write("### Most Frequent Communication Links")

st.dataframe(
    communication_frequency, 
    use_container_width=True
)
st.divider()

st.subheader(" Financial Transaction Analysis")

transaction_file = "data/transactions.csv"
transactions = pd.read_csv(transaction_file)
transactions.columns=transactions.columns.str.strip()
# Convert date
transactions ["date"] = pd.to_datetime(transactions["date"],format="mixed")

# Basic statistics 
total_transactions = len(transactions)
total_amount = transactions ["amount"].sum()
unique_senders = transactions ["sender"].nunique()
unique_receivers = transactions ["receiver"].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric( "Transactions", total_transactions)

with col2:
    st.metric( "Total Amount", f"*{total_amount:,.0f}")

with col3:
    st.metric("Unique Senders",unique_senders)

with col4:
    st.metric("Unique Receivers", unique_receivers)

st.write("### Transaction Records")

st.dataframe(
    transactions,
    use_container_width=True
)
# Money flow between entities

money_flow = (
    transactions
    .groupby( ["sender", "receiver"]
    )["amount"]
    .agg(
    transaction_count="count",
      total_amount="sum"
      )
      .reset_index()
      .sort_values(
          "total_amount",
          ascending=False
          )
)
st.write("### Major Money-Flow Relationships")

st.dataframe(
    money_flow,
    use_container_width=True
)
st.divider()

st.subheader(" Location Analysis")
location_file = "data/locations.csv"
locations = pd.read_csv(location_file)
locations.columns=locations.columns.str.strip()
# Convert date
locations["date"] = pd.to_datetime( locations["date"])


# Basic statistics 
location_records = len(locations)
unique_people = locations ["person"].nunique()
unique_locations = locations ["location"].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Location Records", location_records)

with col2:
    st.metric( "People", unique_people)

with col3:
    st.metric("Locations",unique_locations)
st.write("### Location Records")

st.dataframe(locations,use_container_width=True)

# Find people associated with each location 
location_groups = (
    locations
    .groupby("location") ["person"]
    .agg(
        lambda people:", ".join(sorted(set(people)))
)
    .reset_index()

)

location_groups["people_count"] = ( location_groups["person"]
                                   .apply(lambda x: len(x.split(", ")))
)

st.write("### People Associated With Each Location")

st.dataframe(location_groups,use_container_width=True)

# Shared locations

shared_locations = location_groups[
    location_groups["people_count"]>1
]

st.write("###  Locations With Multiple People")

if not shared_locations.empty:
    st.dataframe(shared_locations, use_container_width=True)
else:
    st.info("No locations with multiple recorded people.")

st.divider()

st.subheader(" Unified Investigation Network")

unified_graph = create_unified_network(
    "data/relationships.csv", 
    "data/cdr.csv", 
    "data/transactions.csv", 
    "data/locations.csv"
)

col1, col2 = st.columns(2)

with col1:
    st.metric( "Total Entities", unified_graph.number_of_nodes())

with col2:
    st.metric("Total Relationships", unified_graph.number_of_edges())

st.write("The unified network combines communication, "
         "financial, location and other authorized relationships.")

st.write("### Interactive Network")
# Create interactive network

interactive_network = Network( 
    height="700px", 
    width="100%",
    bgcolor="#111111", 
    font_color="white"

)

# Add nodes

for node in unified_graph.nodes():
    entity_type = get_entity_type(node)

    if entity_type == "Person":
        shape = "dot"
        size = 25
    elif entity_type == "Phone":
        shape = "square" 
        size = 20
    elif entity_type == "Bank":
        shape = "diamond"
        size = 25
    elif entity_type == "Location":
        shape = "triangle"
        size = 25
    else:
        shape = "ellipse"
        size = 20

    interactive_network.add_node(
        node,
        label=node,
        title=f"Type: {entity_type}",
        shape=shape,
        size=size
    )

# Add relationships

for source, target, attributes in unified_graph.edges( data=True):
    relationship = attributes.get( "relationship","Unknown")

    interactive_network.add_edge(
        source,
        target,
        title=relationship,
        label=relationship

)

interactive_network.set_options("""
{
    "physics": {
        "enabled": true,
        "stabilization": {
            "iterations": 150
        }
    },
    "interaction": {
        "hover": true,
        "navigationButtons": true,
        "ZoomView":true
    }
}
""")

interactive_network.save_graph("unified_network.html")

with open(
    "unified_network.html",
    "r",
    encoding="utf-8"
) as file:
    graph_html = file.read()

st.components.v1.html( 
    graph_html, 
    height=720, 
    scrolling=True)
st.divider()
if st.session_state.role in [
    "Administrator",
    "Investigator"
]:

    st.subheader(" Investigation Priority Analysis")

    priority_data = calculate_priority( unified_graph)

    priority_data = priority_data.sort_values( "Priority Score",ascending=False)

    st.write(
        "Entities are ranked using explainable network "
        "relationship indicators."
    )

    st.dataframe( priority_data,
              use_container_width=True
    )

    st.write("###  Highest Priority Entities")

    top_entities = priority_data.head(5)
    for _, row in top_entities.iterrows():
        st.write(
        f"**{row['Entity']}** " 
        f"({row['Type']}) - " 
        f"Priority Score: " 
        f"{row['Priority Score']}"
    )
        st.write(
        f"Connections:{row['Connections']} |"
        f"Communication:{row['Communication']}| "
        f"Financial:{row['Financial']} |"
        f"Location: {row['Location']}"
    )
        
st.divider()

if st.session_state.role in [
        "Administrator",
        "Investigator"
]:
    st.subheader("🤖 AI Investigation Assistant")

    ai_entity = st.selectbox(
    "Select an entity for AI-assisted analysis",
    sorted(unified_graph.nodes()),
    key="ai_entity"
)

    if st.button("Generate Investigation Summary"):

        summary = generate_investigation_summary(
        ai_entity,
        unified_graph
    )

        st.markdown(summary)
st.divider()
if st.session_state.role in [
    "Administrator",
    "Investigator"
]:
    st.subheader("📄 Investigation Report Generator")

report_entity = st.selectbox(
    "Select an entity for the report",
    sorted(unified_graph.nodes()),
    key="report_entity"
)

if st.button("Generate Investigation Report"):

    entity_type = get_entity_type(report_entity)

    connections = list(
        unified_graph.neighbors(report_entity)
    )

    summary = generate_investigation_summary(
        report_entity,
        unified_graph
    )

    priority_score = 0

    report_priority = priority_data[
        priority_data["Entity"] == report_entity
    ]

    if not report_priority.empty:
        priority_score = report_priority.iloc[0]["Priority Score"]
    else:
        priority_score = 0

    report = f"""
AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM
===========================================

INVESTIGATION ANALYSIS REPORT

Entity: {report_entity}
Entity Type: {entity_type}
Priority Score: {priority_score}

Number of Direct Connections:
{len(connections)}

-------------------------------------------
DIRECT CONNECTIONS
-------------------------------------------
"""

    for connection in connections:

        relationship = unified_graph[
            report_entity
        ][connection].get(
            "relationship",
            "Unknown"
        )

        report += (
            f"{connection} "
            f"-> {relationship}\n"
        )

    report += """
-------------------------------------------
AI-ASSISTED ANALYSIS
-------------------------------------------
"""

    report += summary

    report += """
    
-------------------------------------------
IMPORTANT NOTICE
-------------------------------------------

This report is an analytical aid based on
the supplied authorized dataset.

It does not establish criminality, guilt,
intent, or wrongdoing.

Investigators must verify the underlying
source records and apply applicable legal
and procedural requirements.

-------------------------------------------
END OF REPORT
-------------------------------------------
"""

    st.success(
        "Investigation report generated successfully."
    )

    st.text_area(
        "Generated Report",
        report,
        height=500
    )

    st.download_button(
        label="⬇️ Download Investigation Report",
        data=report,
        file_name=f"{report_entity}_investigation_report.txt",
        mime="text/plain"
    )
    
if st.session_state.role == "Administrator":

    st.divider()

    st.subheader(
        "👑 Administrator Panel"
    )

    st.success(
        "Administrator access enabled."
    )

    st.write(
        "Administrator functions can include:"
    )

    st.write(
        "• User management"
    )

    st.write(
        "• System configuration"
    )

    st.write(
        "• Security monitoring"
    )
    st.write("• Audit log management")

# Step 17: Investigation Dashboard
if not st.session_state.get("logged_in", True):
    st.warning("🔒 Please log in to access the investigation system.")
    st.stop()

st.subheader("🔍 Investigation Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Cases", "0")

with col2:
    st.metric("Persons Detected", "0")

with col3:
    st.metric("Alerts", "0")

st.divider()

st.write("### 📋 Investigation Tools")

option = st.selectbox(
    "Select a tool",
    [
        "Face Detection",
        "Criminal Database",
        "Case Search",
        "Evidence Analysis"
    ]
)
st.info(f"Selected tool: {option}")
# Step 18: Case Registration
CASE_FILE = "cases.json"

if os.path.exists(CASE_FILE):
    with open(CASE_FILE, "r", encoding="utf-8") as f:
        st.session_state.cases = json.load(f)
else:
    st.session_state.cases = []

st.subheader("📝 Register New Case")


with st.form("case_form"):
    case_id = st.text_input("Case ID")
    case_title = st.text_input("Case Title")
    location = st.text_input("Crime Location")
    description = st.text_area("Case Description")
    priority = st.selectbox(
        "Case Priority",
        ["Low","Medium","High"]
    )
    
    detection_result= st.selectbox(
            "Detection Result",
            ["Not Detected","Detected"],
            index=0
        )
    submitted = st.form_submit_button("Create Case")

if submitted:
    if case_id and case_title and location:
        new_case = {
            "Case ID": case_id,
            "Case Title": case_title,
            "Location": location,
            "Description": description,
            "priority": priority,
            "Detection Result": detection_result
        }

        st.session_state.cases.append(new_case)

        # Save cases permanently
        with open(CASE_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.cases, f, indent=4)

        st.success(f"✅ Case {case_id} created successfully!")

    else:
        st.error("⚠️ Please fill in Case ID, Case Title and Crime Location")
# ================= DELETE CASE =================

st.subheader("🗑️ Delete Case")

case_ids = [
    str(case.get("Case ID", case.get("case_id", "")))
    for case in st.session_state.cases
    if case.get("Case ID", case.get("case_id", "")) != ""
]

if case_ids:

    delete_case_id = st.selectbox(
        "Select Case ID to Delete",
        case_ids,
        key="delete_case_select"
    )

    if st.button(
        "🗑️ Delete Selected Case",
        key="delete_case_button"
    ):

        # Remove selected case
        updated_cases = [
            case for case in st.session_state.cases
            if str(
                case.get(
                    "Case ID",
                    case.get("case_id", "")
                )
            ) != str(delete_case_id)
        ]

        # Save locally
        with open(CASE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                updated_cases,
                f,
                indent=4,
                ensure_ascii=False
            )

        # Update session state
        st.session_state.cases = updated_cases

        # Save permanently to GitHub
        github_saved = save_cases_to_github(updated_cases)

        if github_saved:
            st.success(
                f"✅ Case {delete_case_id} deleted permanently!"
            )
            st.info(
                "☁️ Updated cases.json has been saved to GitHub."
            )
        else:
            st.warning(
                "⚠️ Case deleted locally, but GitHub could not "
                "be updated."
            )

        st.rerun()

else:
    st.info("📂 No cases available to delete.")
    
#-----EDIT CASE-----
st.subheader("✏️ Edit Case")

edit_case_id = st.text_input(
    "Enter Case ID to Edit",
    key="edit_case_id"
)

if st.button("Load Case", key="load_case_button"):

    edit_case = next(
        (
            case for case in st.session_state.cases
            if str(case.get("Case ID")) == str(edit_case_id)
        ),
        None
    )

    if edit_case:
        st.session_state.edit_case = edit_case
        st.success(f"✅ Case {edit_case_id} loaded.")
    else:
        st.error(f"❌ Case {edit_case_id} not found.")
if "edit_case" in st.session_state:

    edit_case = st.session_state.edit_case

    edited_title = st.text_input(
        "Case Title",
        value=edit_case.get("Case Title", ""),
        key="edited_title"
    )

    edited_location = st.text_input(
        "Location",
        value=edit_case.get("Location", ""),
        key="edited_location"
    )

    edited_description = st.text_area(
        "Description",
        value=edit_case.get("Description", ""),
        key="edited_description"
    )

    if st.button("Save Changes", key="save_case_changes"):
        for case in st.session_state.cases:
                if case.get("Case ID") == edit_case.get("Case ID"):
                    case["Case Title"] = edited_title
                    case["Location"] = edited_location
                    case["Description"] = edited_description
                    break
        with open(CASE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                st.session_state.cases,
                f,
                indent=4,
                ensure_ascii=False
            )
        del st.session_state["edit_case"]

        st.success("✅ Case updated successfully!")

# ================= SEARCH CASES =================

if "search_id" not in st.session_state:
    st.session_state.search_reset =False
def reset_search():
    st.session_state.search_id = ""

st.subheader("🔍 Search Cases")

search_id = st.text_input(
    "Enter Case ID to search",
    placeholder="Example: 1 or theft",
    key="search_id"
)

priority_filter = st.selectbox(
    "Filter by priority",
    ["All", "Low", "Medium", "High"]
)

status_filter = st.selectbox(
    "Filter by Status",
    ["All", "Open", "Investigating", "Solved", "Closed"]
)

detection_filter = st.selectbox(
    "Detection Result",
    ["All", "Detected", "Not Detected"]
)
# Reset button
st.button(
    "🔄 Reset Search",
    on_click=reset_search
)

if st.button("🔄 Refresh Cases"):
    st.rerun()

# ================= FILTER CASES =================

filtered_cases = []

# Search by Case ID
if search_id.strip() != "":
    search_text = search_id.strip().lower()

    for case in st.session_state.cases:

        case_id = str(
            case.get("Case ID", case.get("case_id", ""))
        ).strip().lower()

        if search_text in case_id:
            filtered_cases.append(case)


# Priority filter
if priority_filter != "All":
    filtered_cases = [
        case for case in filtered_cases
        if case.get("priority", "Normal") == priority_filter
    ]


# Status filter
if status_filter != "All":
    filtered_cases = [
        case for case in filtered_cases
        if case.get("status", "Open") == status_filter
    ]


# Detection Result filter
if detection_filter != "All":
    filtered_cases = [
        case for case in filtered_cases
        if case.get("Detection Result", "Not Detected") == detection_filter
    ]


# ================= CASES FOUND =================

st.write(f"📊 Cases Found: {len(filtered_cases)}")

if filtered_cases:

    for case in filtered_cases:

        st.write("---")

        st.write(f"**Case ID:** {case.get('Case ID', 'N/A')}")
        st.write(f"**Case Title:** {case.get('Case Title', 'N/A')}")
        st.write(f"**Location:** {case.get('Location', 'N/A')}")
        st.write(f"**Description:** {case.get('Description', 'N/A')}")
        st.write(f"**Priority:** {case.get('priority', 'N/A')}")
        status= case.get("update_case_id", "Not Applicable")
        st.write(f"**Status:** {case.get('status', 'N/A')}")
        

else:

    st.warning("🔎 No cases found matching your search.")

st.subheader("📂 View Case Details")

case_ids = [
    str(case.get("Case ID"))
    for case in st.session_state.cases
    if case.get("Case ID") is not None
]
if case_ids:
    selected_case_id = st.selectbox(
        "Select",
         ["Select a case"]+ case_ids,
        index=0
    )
    if selected_case_id =="Select a case":
        selected_case_id = None
else:
    selected_case_id = None
    
if selected_case_id:
    selected_case = next(
        (
            case for case in st.session_state.cases
            if str(case.get("Case ID")) == selected_case_id
        ),
        None
    )

    if selected_case:
        st.write("### Case Information")
        priority = selected_case.get("priority", "Normal")

        if priority == "High":
            st.error(f"🚨 Priority: {priority}")
        elif priority == "Medium":
            st.warning(f"⚠️ Priority: {priority}")
        else:
            st.success(f"🟢 Priority: {priority}")

        detection_result = selected_case.get("Detection Result", "Not Detected")

        if detection_result == "Detected":
            st.error(f"🔴 Detection Result: {detection_result}")
        else:
            st.info(f"🟢 Detection Result: {detection_result}")    

        status = selected_case.get("status", "Unknown")
        if status == "Investigating":
            st.warning(f"🔍 Status: {status}")
        elif status == "Solved":
            st.success(f"✅ Status: {status}")
        elif status == "Closed":
            st.info(f"🔒 Status: {status}")
        else:
            st.write(f"📌 Status: {status}")

    
        for key, value in selected_case.items():
            st.markdown(f"**{key.replace('_',' ').title()}:**{value}")

# Step 21: Evidence Upload
if "evidence" not in st.session_state:
    st.session_state.evidence = {}

# Step 22: Link Evidence to Case

st.subheader("📁 Case Evidence")

EVIDENCE_FILE = "evidence.json"
EVIDENCE_FOLDER = "case_evidence"

os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

if "evidence" not in st.session_state:
    if os.path.exists(EVIDENCE_FILE):
        with open(EVIDENCE_FILE, "r", encoding="utf-8") as f:
            st.session_state.evidence = json.load(f)
    else:
        st.session_state.evidence = {}

selected_case = st.text_input("Enter Case ID")

uploaded_file = st.file_uploader(
    "Upload evidence image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None and selected_case:

    safe_name = os.path.basename(uploaded_file.name)

    image_path = os.path.join(
        EVIDENCE_FOLDER,
        f"{selected_case}_{safe_name}"
    )

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    file_bytes = np.asarray(
        bytearray(uploaded_file.getvalue()),
        dtype = np.uint8

    )

    if selected_case not in st.session_state.evidence:
        st.session_state.evidence[selected_case] = []

    st.session_state.evidence[selected_case].append(
        image_path
    )

    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            st.session_state.evidence,
            f,
            indent=4,
            ensure_ascii=False
        )

    st.success(
        f"✅ Evidence saved to Case {selected_case}"
    )

elif uploaded_file is not None:
    st.warning("⚠️ Enter a Case ID first.")        
st.divider()
# Step 23: AI Evidence Analysis
AI_FILE = "ai_results.json"

if "ai_results" not in st.session_state:
    if os.path.exists(AI_FILE):
        with open(AI_FILE, "r", encoding="utf-8") as f:
            st.session_state.ai_results = json.load(f)
    else:
        st.session_state.ai_results = {}

AI_IMAGE_FOLDER = "ai_analysis_images"
if not os.path.exists(AI_IMAGE_FOLDER):
    os.makedirs(AI_IMAGE_FOLDER)


st.subheader("🤖 AI Analysis & Case Record")

case_id = st.text_input(
    "Enter Case ID for this analysis",
    key="analysis_case"
)

analysis_file = st.file_uploader(
    "Upload image for analysis",
    type=["jpg", "jpeg", "png"],
    key="case_analysis_image"
)

if analysis_file is not None and case_id:

    file_bytes = np.asarray(
        bytearray(analysis_file.read()),
        dtype=np.uint8
    )

    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )
    result = {
    "image": image_path,
    "faces_detected": len(faces)
}

    st.session_state.ai_results[case_id] = result
    with open(AI_FILE, "w", encoding="utf-8") as f:
        json.dump(
        st.session_state.ai_results,
        f,
        indent=4,
        ensure_ascii=False
    )

    st.success(
    f"✅ AI analysis saved to Case {case_id}"
)
    st.warning(
    "⚠️ This result is only a computer-vision observation.\n"
    "It does not establish identity or criminal responsibility."
    )

elif analysis_file is not None:
    st.warning("⚠️ Enter a Case ID first.")

st.subheader("📊 Saved AI Results")

if st.session_state.ai_results:
    
    for case_id, result in st.session_state.ai_results.items():

        st.divider()
        
else:
    st.info("No AI analysis results saved yet.")

st.subheader("📄 Generate Case Report")

report_case_id = st.text_input(
    "Enter Case ID",
    key="report_case_id"
)

if st.button("📊 Generate Report"):
    
    case_found = None
    
    for case in st.session_state.cases:
        if case["Case ID"].lower() == report_case_id.lower():
            case_found = case
            break
            
    if case_found:
        report_text = f"""
INVESTIGATION REPORT

Case ID: {case_found["Case ID"]}
Case Title: {case_found["Case Title"]}
Location: {case_found["Location"]}

Description:
{case_found["Description"]}
"""

    if report_case_id in st.session_state.ai_results:

        result = st.session_state.ai_results[report_case_id]

        report_text += f"""

    AI ANALYSIS

    Evidence Image: {result["image"]}
    Faces Detected: {result["faces_detected"]}
    """

    report_text += """

    NOTE:
    AI observations are not proof of identity or criminal responsibil
    All findings must be reviewed by a qualified investigator.
    """

    st.download_button(
    label="📤 Download Case Report",
    data=report_text,
    file_name=f"{report_case_id}_report.txt",
    mime="text/plain"
    )

# Step 28: Live Dashboard Statistics

st.subheader("📊 Live Investigation Statistics")

total_cases = len(st.session_state.cases)

total_evidence = sum(
    len(files)
    for files in st.session_state.evidence.values()
)

total_ai_results = len(st.session_state.ai_results)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📂 Total Cases", total_cases)

with col2:
    st.metric("📎 Evidence Files", total_evidence)

with col3:
    st.metric("🤖 AI Analyses", total_ai_results)
# Case Status
if "case_status" not in st.session_state:
    st.session_state.case_status ={}


st.subheader("🔄 Update Case Status")

update_case_id = st.text_input("Enter Case ID",key="update_case_id")

new_status = st.selectbox(
    "Select New Status",
    ["Open", "Under Investigation", "Solved", "Closed"],
    key="new_status"
)

if st.button("Update Status",key="update_status_button"):

    case_found = False

    for case in st.session_state.cases:

        if str(case.get("Case ID")) == str(update_case_id):

            case["status"] = new_status
            case_found = True

            # Save updated cases to JSON
            with open(CASE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    st.session_state.cases,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            st.success(
                f"✅ Case {update_case_id} status updated to {new_status}"
            )

            break

    if not case_found:
        st.error(f"❌ Case {update_case_id} not found")
# 📋 Case Status
st.subheader("📋 Case Status")

if update_case_id.strip():

    selected_status_case = next(
        (
            case for case in st.session_state.cases
            if str(case.get("Case ID", "")) == str(update_case_id)
        ),
        None
    )

    if selected_status_case:
        status = selected_status_case.get("status", "Unknown")

        if status == "Under Investigation":
            st.warning(f"🔍 Status: {status}")

        elif status == "Solved":
            st.success(f"✅ Status: {status}")

        elif status == "Closed":
            st.info(f"🔒 Status: {status}")

        elif status == "Open":
            st.write(f"📌 Status: {status}")

        else:
            st.write(f"📌 Status: {status}")

    else:
        st.info("Enter a valid Case ID to view its status.")
else:
    st.info("Enter a Case ID above to view its current status.")
# Step 30: Case Management Table

st.subheader("📋 Case Management")

if st.session_state.cases:
    
    table_data = []
    
    for case in st.session_state.cases:
        
        case_id = case["Case ID"]
        status = case.get("status","Open")
        
        evidence_count = len(
            st.session_state.evidence.get(case_id, [])
        )
        
        ai_count = (
            1
            if case_id in st.session_state.ai_results
            else 0
        )
        
        table_data.append({
            "Case ID": case_id,
            "Case Title": case["Case Title"],
            "Location": case["Location"],
            "Status": status,
            "Evidence": evidence_count,
            "AI Analysis": ai_count
        })
        
    st.dataframe(
        table_data,
        use_container_width=True
                 )
else:
    st.info("No cases registered yet.") 


# Step 31: Logout

if st.session_state.get("logged_in", False):

    st.sidebar.divider()
    st.sidebar.subheader("🔐 Account")

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None

        st.success("✅ You have been logged out.")

        st.rerun()  
  
# Step 33: Activity Log

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []
st.subheader("📋 Investigation Activity Log")

if st.button("Clear Activity Log "):
    st.session_state.activity_log=[]
    st.rerun()

if st.session_state.activity_log:
    for activity in reversed(st.session_state.activity_log):
        st.info(f"• {activity}")

else:
    st.info("No investigation activity recorded yet.")
log_activity(case_id, "Case was created.")
log_activity(update_case_id,f"status changed to {new_status}.")




