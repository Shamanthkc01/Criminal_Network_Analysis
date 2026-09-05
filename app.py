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
# ==================================================
# 📱 INSTAGRAM-STYLE MOBILE BOTTOM NAVIGATION
# ==================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Home"
# Inject custom CSS to hide the bottom footer, status indicators, and deployment button
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)
'''st.markdown("""
<style>

/* Hide Streamlit sidebar on mobile */
@media (max-width: 768px) {

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Give content space above bottom navigation */
    [data-testid="stAppViewContainer"] {
        padding-bottom: 90px;
    }

    /* Bottom navigation bar */
    div[role="radiogroup"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;

        z-index: 999999 !important;

        background: white !important;
        border-top: 1px solid #dddddd;

        padding: 7px 3px 8px 3px !important;

        display: flex !important;
        justify-content: space-around !important;
        align-items: center !important;

        box-shadow: 0 -3px 12px rgba(0,0,0,0.12);
    }

    /* Each navigation item */
    div[role="radiogroup"] label {
        flex: 1 !important;

        display: flex !important;
        flex-direction: column !important;

        align-items: center !important;
        justify-content: center !important;

        text-align: center !important;

        font-size: 11px !important;
        font-weight: 500 !important;

        padding: 4px 0 !important;

        margin: 0 !important;
    }

    /* Radio circle hidden */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* Navigation text */
    div[role="radiogroup"] label p {
        margin: 0 !important;
        padding: 0 !important;
    }
}'''
st.markdown("""
<style>
/* Desktop */
@media (min-width: 769px) {

    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 20px;
    }

}
/* Hide Streamlit branding */
header[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

footer {
    display: none !important;
}

/* Hide GitHub links inside the app */
a[href*="github.com"] {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)


navigation = st.radio(
    "Navigation",
    [
        "🏠 Home",
        "📂 Cases",
        "🕸️ Network",
        "🤖 AI",
        "👤 Profile"
    ],
    horizontal=True,
    key="mobile_navigation",
    label_visibility="collapsed"
)

st.session_state.active_page = navigation

# ==================================================
# END MOBILE BOTTOM NAVIGATION
# ==================================================
# ==================================================
# 🏠 HOME PAGE
# ==================================================

if st.session_state.active_page == "🏠 Home":

    st.title(" AI-Powered Criminal Network Analysis System")

    st.divider()

    st.header("📊 Investigation Dashboard")

    # Load investigation data
    file_path = "data/relationships.csv"
    data = pd.read_csv(file_path)

    # Count different entities
    persons = set()

    for value in data["source"]:
        if value.startswith("Person_"):
            persons.add(value)

    for key in data["target"]:
        if key.startswith("Person_"):
            persons.add(key)

    phone_records = len(
        data[data["type"] == "Phone"]
    )

    financial_links = len(
        data[data["type"] == "Financial"]
    )

    location_count = len(
        data[data["type"] == "Location"]
    )

    # Dashboard statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👤 Persons", len(persons))

    with col2:
        st.metric("📱 Phone Records", phone_records)

    with col3:
        st.metric("💰 Financial Links", financial_links)

    with col4:
        st.metric("📍 Locations", location_count)

    st.divider()

    st.subheader("🔗 Investigation Relationships")

    st.dataframe(
        data,
        use_container_width=True
    )

    st.divider()

    st.subheader("📤 Upload Investigation Data")

    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        key="home_upload"
    )

    if uploaded_file is not None:

        uploaded_data = pd.read_csv(uploaded_file)

        st.success("✅ File uploaded successfully!")

        st.dataframe(
            uploaded_data,
            use_container_width=True
        )

    else:
        st.info(
            "You can upload your own authorized investigation datasets."
        )

# ==================================================
# END HOME PAGE
# ==================================================
# ==================================================
# 📂 CASES PAGE
# ==================================================

if st.session_state.active_page == "📂 Cases":

    st.title("📂 Case Management")

    st.write(
        f"Logged in as: **{st.session_state.username}** "
        f"| Role: **{st.session_state.role}**"
    )

    st.divider()

    # Load cases
    CASE_FILE = "cases.json"

    if os.path.exists(CASE_FILE):

        with open(CASE_FILE, "r", encoding="utf-8") as f:
            st.session_state.cases = json.load(f)

    else:
        st.session_state.cases = []

    # --------------------------------------------------
    # CASE STATISTICS
    # --------------------------------------------------
    if "cases" not in st.session_state:
        if os.path.exists("cases.json"):
            with open("cases.json", "r", encoding="utf-8") as f:
                st.session_state.cases = json.load(f)
        else:
            st.session_state.cases = []

    total_cases = len(st.session_state.cases)

    open_cases = sum(
        1 for case in st.session_state.cases
        if case.get("status", "Open") == "Open"
    )

    investigation_cases = sum(
        1 for case in st.session_state.cases
        if case.get("status") in [
            "Investigating",
            "Under Investigation"
        ]
    )

    solved_cases = sum(
        1 for case in st.session_state.cases
        if case.get("status") == "Solved"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📂 Total Cases", total_cases)

    with col2:
        st.metric("🟢 Open", open_cases)

    with col3:
        st.metric("🔍 Investigating", investigation_cases)

    with col4:
        st.metric("✅ Solved", solved_cases)

    st.divider()

    # --------------------------------------------------
    # REGISTER NEW CASE
    # --------------------------------------------------

    st.subheader("📝 Register New Case")

    with st.form("mobile_case_form"):

        case_id = st.text_input("Case ID")

        case_title = st.text_input("Case Title")

        location = st.text_input("Crime Location")

        description = st.text_area("Case Description")

        priority = st.selectbox(
            "Case Priority",
            ["Low", "Medium", "High"]
        )

        detection_result = st.selectbox(
            "Detection Result",
            ["Not Detected", "Detected"]
        )

        submitted = st.form_submit_button(
            "➕ Create Case"
        )

    if submitted:

        if case_id and case_title and location:

            # Check duplicate Case ID
            existing_case = any(
                str(case.get("Case ID")) == str(case_id)
                for case in st.session_state.cases
            )

            if existing_case:

                st.error(
                    f"❌ Case ID {case_id} already exists."
                )

            else:

                new_case = {
                    "Case ID": case_id,
                    "Case Title": case_title,
                    "Location": location,
                    "Description": description,
                    "priority": priority,
                    "Detection Result": detection_result,
                    "status": "Open"
                }

                st.session_state.cases.append(new_case)

                with open(
                    CASE_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        st.session_state.cases,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )
               

                st.success(
                    f"✅ Case {case_id} created successfully!"
                )
                log_activity(case_id,"Case was created")

        else:

            st.error(
                "⚠️ Please fill in Case ID, Case Title and Crime Location."
            )

    st.divider()

    # --------------------------------------------------
    # SEARCH CASES
    # --------------------------------------------------

    st.subheader("🔍 Search Cases")

    search_id = st.text_input(
        "Enter Case ID",
        placeholder="Example: 1 or CASE001",
        key="mobile_search_id"
    )

    priority_filter = st.selectbox(
        "Priority",
        ["All", "Low", "Medium", "High"],
        key="mobile_priority_filter"
    )

    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Open",
            "Under Investigation",
            "Investigating",
            "Solved",
            "Closed"
        ],
        key="mobile_status_filter"
    )

    detection_filter = st.selectbox(
        "Detection",
        ["All", "Detected", "Not Detected"],
        key="mobile_detection_filter"
    )

    filtered_cases = st.session_state.cases.copy()

    if search_id.strip():

        search_text = search_id.strip().lower()

        filtered_cases = [
            case
            for case in filtered_cases
            if search_text in str(
                case.get("Case ID", "")
            ).lower()
        ]

    if priority_filter != "All":

        filtered_cases = [
            case
            for case in filtered_cases
            if case.get("priority") == priority_filter
        ]

    if status_filter != "All":

        filtered_cases = [
            case
            for case in filtered_cases
            if case.get("status", "Open") == status_filter
        ]

    if detection_filter != "All":

        filtered_cases = [
            case
            for case in filtered_cases
            if case.get(
                "Detection Result",
                "Not Detected"
            ) == detection_filter
        ]

    st.write(
        f"📊 **Cases Found: {len(filtered_cases)}**"
    )

    if filtered_cases:

        for case in filtered_cases:

            with st.expander(
                f"📂 {case.get('Case ID', 'N/A')} — "
                f"{case.get('Case Title', 'Untitled')}"
            ):

                st.write(
                    f"**Location:** "
                    f"{case.get('Location', 'N/A')}"
                )

                st.write(
                    f"**Description:** "
                    f"{case.get('Description', 'N/A')}"
                )

                st.write(
                    f"**Priority:** "
                    f"{case.get('priority', 'Normal')}"
                )

                st.write(
                    f"**Status:** "
                    f"{case.get('status', 'Open')}"
                )

                st.write(
                    f"**Detection:** "
                    f"{case.get('Detection Result', 'Not Detected')}"
                )

    else:

        st.info("🔎 No cases found.")

    st.divider()

    # --------------------------------------------------
    # VIEW CASE DETAILS
    # --------------------------------------------------

    st.subheader("📋 View Case Details")

    case_ids = [
        str(case.get("Case ID"))
        for case in st.session_state.cases
        if case.get("Case ID") is not None
    ]

    if case_ids:

        selected_case_id = st.selectbox(
            "Select a Case",
            ["-- Select a Case --"] + case_ids,
            key="mobile_view_case"
        )

        if selected_case_id != "-- Select a Case --":

            selected_case = next(
                (
                    case
                    for case in st.session_state.cases
                    if str(case.get("Case ID"))
                    == selected_case_id
                ),
                None
            )

            if selected_case:

                st.write("### Case Information")

                for key, value in selected_case.items():

                    st.write(
                        f"**{key.replace('_', ' ').title()}:** "
                        f"{value}"
                    )

    else:

        st.info("📂 No cases registered yet.")

    st.divider()

    # --------------------------------------------------
    # DELETE CASE
    # --------------------------------------------------
if st.session_state.active_page == "📂 Cases":
    st.subheader("🗑️ Delete Case")

    if case_ids:

        delete_case_id = st.selectbox(
            "Select Case to Delete",
            case_ids,
            key="mobile_delete_case"
        )

        if st.button(
            "🗑️ Delete Selected Case",
            key="mobile_delete_button"
        ):

            updated_cases = [
                case
                for case in st.session_state.cases
                if str(
                    case.get(
                        "Case ID",
                        case.get("case_id", "")
                    )
                ) != str(delete_case_id)
            ]

            with open(
                CASE_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    updated_cases,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            st.session_state.cases = updated_cases

            # Save permanently to GitHub
            github_saved = save_cases_to_github(
                updated_cases
            )

            if github_saved:

                st.success(
                    f"✅ Case {delete_case_id} "
                    "deleted permanently!"
                )

            else:

                st.warning(
                    "⚠️ Case deleted locally, "
                    "but GitHub could not be updated."
                )

            st.rerun()

    else:
        st.info("📂 No cases available to delete.")

# ==================================================
# 📋 INVESTIGATION ACTIVITY LOG
# ==================================================
if st.session_state.active_page == "📂 Cases":
    st.divider()
    st.subheader("📋 Investigation Activity Log")

    if "activity_log" not in st.session_state: 
        st.session_state.activity_log = []
    if st.button(
        "🗑️ Clear Activity Log",
        key="clear_activity_log"
        ):

        st.session_state.activity_log = []

        st.success("✅ Activity log cleared.")

        st.rerun()

        if st.session_state.activity_log:

            for activity in reversed(st.session_state.activity_log):

        # Handle old activity entries that may be strings
                if isinstance(activity, dict):

                    case_id = activity.get("Case ID", "N/A")
                    message = activity.get("Message", "Unknown activity")
                    activity_time = activity.get("Time", "Unknown time")
                else:
                    activity_text = str(activity)

                    case_id = "N/A"
                    message = activity_text
                    activity_time = "Time not recorded"

            # Extract time and case ID from old activity format
                    if activity_text.startswith("["):

                        try:
                            activity_time = activity_text.split("]")[0][1:]

                            if "[Case " in activity_text:
                                case_id = (
                                    activity_text
                                    .split("[Case ")[1]
                                    .split("]")[0]
                                )

                            message = activity_text.split("] ", 1)[1]

                        except Exception:
                            pass

                st.info(
                    f"📂 **Case:** {case_id}\n\n"
                    f"📝 **Activity:** {message}\n\n"
                    f"🕒 **Time:** {activity_time}"
                )

        else:

            st.info("ℹ️ No investigation activity recorded yet.")


# ==================================================
# END INVESTIGATION ACTIVITY LOG
# ==================================================


# ==================================================
# END CASES PAGE
# ==================================================
# ==================================================
# 🕸️ NETWORK PAGE
# ==================================================

if st.session_state.active_page == "🕸️ Network":

    st.title("🕸️ Criminal Network Analysis")

    st.write(
        "Analyze relationships, communications, financial links "
        "and locations."
    )

    st.divider()

    # --------------------------------------------------
    # ENTITY ANALYSIS
    # --------------------------------------------------

    st.subheader("🔎 Entity Analysis")

    file_path = "data/relationships.csv"

    graph = create_network(file_path)

    importance = calculate_importance(graph)

    entity_list = sorted(graph.nodes())

    selected_entity = st.selectbox(
        "Select an entity to investigate",
        entity_list,
        key="network_entity"
    )

    entity_type = get_entity_type(selected_entity)

    connections = list(
        graph.neighbors(selected_entity)
    )

    score = importance[selected_entity] * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Entity",
            selected_entity
        )

    with col2:
        st.metric(
            "Type",
            entity_type
        )

    with col3:
        st.metric(
            "Connections",
            len(connections)
        )

    st.write("### 📊 Network Importance Score")

    st.progress(
        min(int(score), 100)
    )

    st.write(
        f"**Importance Score: {score:.1f}/100**"
    )

    st.write(
        "• 0–20 : Low network importance"
    )

    st.write(
        "• 20–50 : Moderate network importance"
    )

    st.write(
        "• 50–80 : High network importance"
    )

    st.write(
        "• 80–100 : Critical network importance"
    )

    st.write("### 🔗 Direct Connections")

    if connections:

        for connection in connections:

            relationship = graph[
                selected_entity
            ][connection].get(
                "relationship",
                "Unknown"
            )

            st.write(
                f"**{connection}** — {relationship}"
            )

    else:

        st.info(
            "No direct connections found."
        )

    st.divider()

    # --------------------------------------------------
    # CRIMINAL NETWORK GRAPH
    # --------------------------------------------------

    st.subheader("🕸️ Criminal Network Graph")

    network = Network(
        height="600px",
        width="100%",
        bgcolor="#111111",
        font_color="white"
    )

    network.from_nx(graph)

    network.save_graph(
        "network.html"
    )

    with open(
        "network.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    st.components.v1.html(
        html,
        height=620,
        scrolling=True
    )

    st.divider()

    # --------------------------------------------------
    # CDR COMMUNICATION ANALYSIS
    # --------------------------------------------------

    st.subheader("📞 CDR Communication Analysis")

    cdr_file = "data/cdr.csv"

    cdr = pd.read_csv(cdr_file)

    cdr.columns = cdr.columns.str.strip()

    cdr["date"] = pd.to_datetime(
        cdr["date"]
    )

    total_calls = len(cdr)

    total_duration = cdr[
        "duration"
    ].sum()

    unique_callers = cdr[
        "caller"
    ].nunique()

    unique_receivers = cdr[
        "receiver"
    ].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📞 Total Calls",
            total_calls
        )

    with col2:
        st.metric(
            "⏱️ Total Duration",
            f"{total_duration} sec"
        )

    with col3:
        st.metric(
            "📱 Unique Callers",
            unique_callers
        )

    with col4:
        st.metric(
            "📲 Unique Receivers",
            unique_receivers
        )

    st.write("### Communication Records")

    st.dataframe(
        cdr,
        use_container_width=True
    )

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

    st.write(
        "### Most Frequent Communication Links"
    )

    st.dataframe(
        communication_frequency,
        use_container_width=True
    )

    st.divider()

    # --------------------------------------------------
    # FINANCIAL ANALYSIS
    # --------------------------------------------------

    st.subheader(
        "💰 Financial Transaction Analysis"
    )

    transaction_file = (
        "data/transactions.csv"
    )

    transactions = pd.read_csv(
        transaction_file
    )

    transactions.columns = (
        transactions.columns.str.strip()
    )

    transactions["date"] = pd.to_datetime(
        transactions["date"],
        format="mixed"
    )

    total_transactions = len(
        transactions
    )

    total_amount = transactions[
        "amount"
    ].sum()

    unique_senders = transactions[
        "sender"
    ].nunique()

    unique_receivers = transactions[
        "receiver"
    ].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Transactions",
            total_transactions
        )

    with col2:
        st.metric(
            "Total Amount",
            f"₹{total_amount:,.0f}"
        )

    with col3:
        st.metric(
            "Unique Senders",
            unique_senders
        )

    with col4:
        st.metric(
            "Unique Receivers",
            unique_receivers
        )

    st.write(
        "### Transaction Records"
    )

    st.dataframe(
        transactions,
        use_container_width=True
    )

    money_flow = (
        transactions
        .groupby(
            ["sender", "receiver"]
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

    st.write(
        "### Major Money-Flow Relationships"
    )

    st.dataframe(
        money_flow,
        use_container_width=True
    )

    st.divider()

    # --------------------------------------------------
    # LOCATION ANALYSIS
    # --------------------------------------------------

    st.subheader(
        "📍 Location Analysis"
    )

    location_file = (
        "data/locations.csv"
    )

    location_data = pd.read_csv(
        location_file
    )

    location_data.columns = (
        location_data.columns.str.strip()
    )

    location_data["date"] = pd.to_datetime(
        location_data["date"]
    )

    location_records = len(
        location_data
    )

    unique_people = location_data[
        "person"
    ].nunique()

    unique_locations = location_data[
        "location"
    ].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Location Records",
            location_records
        )

    with col2:
        st.metric(
            "People",
            unique_people
        )

    with col3:
        st.metric(
            "Locations",
            unique_locations
        )

    st.write(
        "### Location Records"
    )

    st.dataframe(
        location_data,
        use_container_width=True
    )

    location_groups = (
        location_data
        .groupby("location")["person"]
        .agg(
            lambda people:
            ", ".join(
                sorted(set(people))
            )
        )
        .reset_index()
    )

    location_groups["people_count"] = (
        location_groups["person"]
        .apply(
            lambda x:
            len(x.split(", "))
        )
    )

    st.write(
        "### People Associated With Each Location"
    )

    st.dataframe(
        location_groups,
        use_container_width=True
    )

    shared_locations = (
        location_groups[
            location_groups["people_count"] > 1
        ]
    )

    st.write(
        "### 📍 Locations With Multiple People"
    )

    if not shared_locations.empty:

        st.dataframe(
            shared_locations,
            use_container_width=True
        )

    else:

        st.info(
            "No locations with multiple recorded people."
        )

    st.divider()

    # --------------------------------------------------
    # UNIFIED INVESTIGATION NETWORK
    # --------------------------------------------------

    st.subheader(
        "🌐 Unified Investigation Network"
    )

    unified_graph = create_unified_network(
        "data/relationships.csv",
        "data/cdr.csv",
        "data/transactions.csv",
        "data/locations.csv"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Entities",
            unified_graph.number_of_nodes()
        )

    with col2:
        st.metric(
            "Total Relationships",
            unified_graph.number_of_edges()
        )

    st.write(
        "The unified network combines communication, "
        "financial, location and other authorized relationships."
    )

    interactive_network = Network(
        height="700px",
        width="100%",
        bgcolor="#111111",
        font_color="white"
    )

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

    for source, target, attributes in (
        unified_graph.edges(data=True)
    ):

        relationship = attributes.get(
            "relationship",
            "Unknown"
        )

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
            "zoomView": true
        }
    }
    """)

    interactive_network.save_graph(
        "unified_network.html"
    )

    with open(
        "unified_network.html",
        "r",
        encoding="utf-8"
    ) as file:

        graph_html = file.read()

    st.components.v1.html(
        graph_html,
        height=720,
        scrolling=True
    )

    st.divider()

    # --------------------------------------------------
    # INVESTIGATION PRIORITY
    # --------------------------------------------------

    if st.session_state.role in [
        "Administrator",
        "Investigator"
    ]:

        st.subheader(
            "🚨 Investigation Priority Analysis"
        )

        priority_data = calculate_priority(
            unified_graph
        )

        priority_data = priority_data.sort_values(
            "Priority Score",
            ascending=False
        )

        st.write(
            "Entities are ranked using explainable "
            "network relationship indicators."
        )

        st.dataframe(
            priority_data,
            use_container_width=True
        )

        st.write(
            "### Highest Priority Entities"
        )

        top_entities = priority_data.head(5)

        for _, row in top_entities.iterrows():

            st.write(
                f"**{row['Entity']}** "
                f"({row['Type']}) — "
                f"Priority Score: "
                f"{row['Priority Score']}"
            )

            st.write(
                f"Connections: {row['Connections']} | "
                f"Communication: {row['Communication']} | "
                f"Financial: {row['Financial']} | "
                f"Location: {row['Location']}"
            )

# ==================================================
# END NETWORK PAGE
# ==================================================
# ==================================================
# 🤖 AI PAGE
# ==================================================

if st.session_state.active_page == "🤖 AI":
    unified_graph = create_unified_network(
            "data/relationships.csv",
            "data/cdr.csv",
            "data/transactions.csv",
            "data/locations.csv"
        )
    
    st.title("🤖 AI Investigation Center")

    st.write(
        "AI-assisted analysis for authorized investigation data."
    )

    st.divider()

    # --------------------------------------------------
    # AI INVESTIGATION ASSISTANT
    # --------------------------------------------------

    if st.session_state.role in [
        "Administrator",
        "Investigator"
    ]:

        st.subheader("🤖 AI Investigation Assistant")

        # Create unified network
        unified_graph = create_unified_network(
            "data/relationships.csv",
            "data/cdr.csv",
            "data/transactions.csv",
            "data/locations.csv"
        )

        ai_entity = st.selectbox(
            "Select an entity for AI-assisted analysis",
            sorted(unified_graph.nodes()),
            key="mobile_ai_entity"
        )

        if st.button(
            "🧠 Generate Investigation Summary",
            key="mobile_ai_summary"
        ):

            summary = generate_investigation_summary(
                ai_entity,
                unified_graph
            )

            st.markdown(summary)

    else:

        st.warning(
            "🔒 AI investigation tools are available "
            "only to authorized investigators."
        )

    st.divider()

    # --------------------------------------------------
    # LOAD AI RESULTS
    # --------------------------------------------------

    AI_FILE = "ai_results.json"

    if "ai_results" not in st.session_state:

        if os.path.exists(AI_FILE):

            with open(
                AI_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                st.session_state.ai_results = json.load(f)

        else:

            st.session_state.ai_results = {}

    # --------------------------------------------------
    # AI ANALYSIS & CASE RECORD
    # --------------------------------------------------

    st.subheader("🔬 AI Analysis & Case Record")

    case_id = st.text_input(
        "Enter Case ID for this analysis",
        key="mobile_analysis_case"
    )

    analysis_file = st.file_uploader(
        "Upload image for analysis",
        type=["jpg", "jpeg", "png"],
        key="mobile_case_analysis_image"
    )

    if analysis_file is not None and case_id:

        file_bytes = np.asarray(
            bytearray(analysis_file.read()),
            dtype=np.uint8
        )

        image = cv2.imdecode(
            file_bytes,
            cv2.IMREAD_COLOR
        )

        if image is not None:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades +
                "haarcascade_frontalface_default.xml"
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5
            )

            result = {
                "faces_detected": len(faces)
            }

            st.session_state.ai_results[
                case_id
            ] = result

            with open(
                AI_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    st.session_state.ai_results,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            st.success(
                f"✅ AI analysis saved to Case {case_id}"
            )

            st.metric(
                "👤 Faces Detected",
                len(faces)
            )

            st.warning(
                "⚠️ This is only a computer-vision "
                "observation. It does not establish "
                "identity or criminal responsibility."
            )

        else:

            st.error(
                "❌ Could not process the uploaded image."
            )

    elif analysis_file is not None:

        st.warning(
            "⚠️ Enter a Case ID first."
        )

    st.divider()

    # --------------------------------------------------
    # SAVED AI RESULTS
    # --------------------------------------------------

    st.subheader("📊 Saved AI Results")

    if st.session_state.ai_results:

        for saved_case_id, result in (
            st.session_state.ai_results.items()
        ):

            with st.expander(
                f"📂 Case {saved_case_id}"
            ):

                st.write(
                    f"**Faces Detected:** "
                    f"{result.get('faces_detected', 0)}"
                )

    else:

        st.info(
            "No AI analysis results saved yet."
        )

    st.divider()

    # --------------------------------------------------
    # INVESTIGATION REPORT GENERATOR
    # --------------------------------------------------

    if st.session_state.role in [
        "Administrator",
        "Investigator"
    ]:

        st.subheader(
            "📄 Investigation Report Generator"
        )

        report_entity = st.selectbox(
            "Select an entity for the report",
            sorted(unified_graph.nodes()),
            key="mobile_report_entity"
        )

        if st.button(
            "📄 Generate Investigation Report",
            key="mobile_generate_report"
        ):

            entity_type = get_entity_type(
                report_entity
            )

            connections = list(
                unified_graph.neighbors(
                    report_entity
                )
            )

            summary = generate_investigation_summary(
                report_entity,
                unified_graph
            )

            priority_data = calculate_priority(
                unified_graph
            )

            report_priority = priority_data[
                priority_data["Entity"]
                == report_entity
            ]

            if not report_priority.empty:

                priority_score = (
                    report_priority.iloc[0][
                        "Priority Score"
                    ]
                )

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
                    f"{connection} -> "
                    f"{relationship}\n"
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
                "✅ Investigation report generated."
            )

            st.text_area(
                "Generated Report",
                report,
                height=500,
                key="mobile_generated_report"
            )

            st.download_button(
                label="⬇️ Download Investigation Report",
                data=report,
                file_name=(
                    f"{report_entity}_investigation_report.txt"
                ),
                mime="text/plain",
                key="mobile_download_report"
            )

    st.divider()

    # --------------------------------------------------
    # CASE REPORT
    # --------------------------------------------------

    st.subheader("📋 Generate Case Report")

    report_case_id = st.text_input(
        "Enter Case ID",
        key="mobile_report_case_id"
    )

    if st.button(
        "📊 Generate Case Report",
        key="mobile_case_report"
    ):

        case_found = next(
            (
                case
                for case in st.session_state.cases
                if str(
                    case.get("Case ID", "")
                ).lower()
                == report_case_id.lower()
            ),
            None
        )

        if case_found:

            report_text = f"""
INVESTIGATION REPORT

Case ID: {case_found["Case ID"]}
Case Title: {case_found["Case Title"]}
Location: {case_found["Location"]}

Description:
{case_found["Description"]}
"""

            if report_case_id in (
                st.session_state.ai_results
            ):

                result = st.session_state.ai_results[
                    report_case_id
                ]

                report_text += f"""

AI ANALYSIS

Faces Detected:
{result.get("faces_detected", 0)}
"""

            report_text += """

NOTE:
AI observations are not proof of identity
or criminal responsibility.

All findings must be reviewed by a
qualified investigator.
"""

            st.success(
                "✅ Case report generated."
            )

            st.text_area(
                "Case Report",
                report_text,
                height=400,
                key="mobile_case_report_text"
            )

            st.download_button(
                label="📤 Download Case Report",
                data=report_text,
                file_name=(
                    f"{report_case_id}_report.txt"
                ),
                mime="text/plain",
                key="mobile_download_case_report"
            )

        else:

            st.error(
                f"❌ Case {report_case_id} not found."
            )
if st.session_state.active_page == "🤖 AI":
# Step 28: Live Dashboard Statistics
    st.subheader("📊 Live Investigation Statistics")
    if "cases" not in st.session_state:
        st.session_state.cases =[]

    total_cases = len(st.session_state.cases)
    if "evidence" not in st.session_state:
        st.session_state.evidence = {}

    total_evidence = sum(
        len(files)
        for files in st.session_state.evidence.values()
    )
    if "ai_results" not in st.session_state:
        st.session_state.ai_results = {}
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
                log_activity(update_case_id,f"Status changed to {new_status}.")
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

if st.session_state.active_page == "🤖 AI":

# ==================================================
# 📋 INVESTIGATION ACTIVITY LOG
# ==================================================

    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []


    def log_activity(case_id, message):

        if "activity_log" not in st.session_state:
            st.session_state.activity_log = []

            activity = {
            "Case ID": str(case_id),
            "Message": str(message),
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.activity_log.append(activity)


    st.subheader("📋 Investigation Activity Log")


    if st.button(
        "🗑️ Clear Activity Log",
        key="clear_activity_log"
    ):

        st.session_state.activity_log = []

        st.success("✅ Activity log cleared.")

        st.rerun()


    if st.session_state.activity_log:

        for activity in reversed(st.session_state.activity_log):

        # Handle old activity entries that may be strings
            if isinstance(activity, dict):

                case_id = activity.get("Case ID", "N/A")
                message = activity.get("Message", "Unknown activity")
                activity_time = activity.get("Time", "Unknown time")
            else:
                activity_text = str(activity)

                case_id = "N/A"
                message = activity_text
                activity_time = "Time not recorded"

            # Extract time and case ID from old activity format
                if activity_text.startswith("["):

                    try:
                        activity_time = activity_text.split("]")[0][1:]

                        if "[Case " in activity_text:
                            case_id = (
                                activity_text
                                .split("[Case ")[1]
                                .split("]")[0]
                            )

                        message = activity_text.split("] ", 1)[1]

                    except Exception:
                        pass
    
            st.info(
                f"📂 **Case:** {case_id}\n\n"
                f"📝 **Activity:** {message}\n\n"
                f"🕒 **Time:** {activity_time}"
            )

    else:

        st.info("ℹ️ No investigation activity recorded yet.")


# ==================================================
# END INVESTIGATION ACTIVITY LOG
# ==================================================


# ==================================================
# END AI PAGE
# ==================================================
# ==================================================
# 👤 PROFILE PAGE
# ==================================================

if st.session_state.active_page == "👤 Profile":

    st.title("👤 Profile")

    st.divider()

    # --------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------

    st.subheader("🔐 Account Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "👤 Username",
            st.session_state.username
        )

    with col2:
        st.metric(
            "🛡️ Role",
            st.session_state.role
        )

    st.divider()

    # --------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------

    st.subheader("💻 System Information")

    st.write(
        "**System:** AI-Powered Criminal Network Analysis System"
    )

    st.write(
        "**Event:** Smart India Hackathon 2026"
    )

    st.write(
        "**Problem Statement:** 26189"
    )

    st.write(
        "**Access:** Authorized Investigation Portal"
    )

    st.divider()

    # --------------------------------------------------
    # ADMINISTRATOR PANEL
    # --------------------------------------------------

    if st.session_state.role == "Administrator":

        st.subheader("👑 Administrator Panel")

        st.success(
            "Administrator access enabled."
        )

        st.write(
            "Administrator functions can include:"
        )

        st.write("• 👥 User management")
        st.write("• ⚙️ System configuration")
        st.write("• 🛡️ Security monitoring")
        st.write("• 📋 Audit log management")

        st.divider()

    # --------------------------------------------------
    # INVESTIGATOR ACCESS
    # --------------------------------------------------

    elif st.session_state.role == "Investigator":

        st.subheader("🕵️ Investigator Access")

        st.success(
            "Investigator access enabled."
        )

        st.write(
            "You can access authorized investigation "
            "and AI-analysis features."
        )

        st.divider()

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------

    st.subheader("🚪 Account")

    if st.button(
        "🚪 Logout",
        key="mobile_profile_logout",
        use_container_width=True
    ):

        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = ""

        st.success(
            "✅ You have been logged out."
        )

        st.rerun()

# ==================================================
# END PROFILE PAGE
# ==================================================
  
# Step 28: Live Dashboard Statistics


# Step 31: Logout

if st.session_state.get("logged_in", False):

    st.sidebar.divider()
    st.sidebar.subheader("🔐 Account")

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None

        st.success("✅ You have been logged out.")

        st.rerun()  

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


def log_activity(case_id, message):

    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []

    activity = {
        "Case ID": str(case_id),
        "Message": str(message),
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.activity_log.append(activity)
