import streamlit as st
import streamlit.components.v1 as components
import re
import time
from pathlib import Path
from html import escape
from agents.supervisor_agent import supervisor_agent


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="IntelliOps-AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.html("""
<style>

html, body {
    font-family: 'Inter', Arial, sans-serif;
}

.stApp {
    background-color: #f8fafc;
    color: #0f172a;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] li {
    color: #1e293b;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    color: #e2e8f0;
}

.sidebar-brand {
    font-size: 26px;
    font-weight: 800;
    color: white;
    letter-spacing: -1px;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 25px;
}

.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #94a3b8;
    margin-top: 24px;
    margin-bottom: 12px;
}

.agent-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
    color: #e2e8f0;
    font-size: 13px;
}

.agent-description {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 5px;
}

.tech-tag {
    display: inline-block;
    background: #334155;
    color: #cbd5e1;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 11px;
    margin: 3px;
}

/* Main header */

.hero {
    background: linear-gradient(120deg, #0f172a, #1e40af);
    padding: 32px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(15,23,42,0.12);
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    color: white;
    letter-spacing: -1.5px;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 15px;
    color: #bfdbfe;
    line-height: 1.7;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 11px;
    color: #dbeafe;
    margin-bottom: 14px;
}

/* Feature cards */

.feature-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    min-height: 175px;
    box-shadow: 0 3px 10px rgba(15,23,42,0.04);
    transition: 0.2s ease;
}

.feature-card:hover {
    border-color: #3b82f6;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(37,99,235,0.08);
}

.feature-icon {
    font-size: 26px;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}

.feature-description {
    font-size: 12px;
    color: #64748b;
    margin-top: 7px;
    line-height: 1.6;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 3px 10px rgba(15,23,42,0.03);
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] th {
    color: #1e293b;
}

.agent-badge {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 12px;
}

.response-time {
    color: #64748b;
    font-size: 11px;
    margin-left: 10px;
}

/* Buttons */

.stButton > button {
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    background: white;
    color: #334155;
    font-size: 13px;
    font-weight: 500;
    min-height: 50px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #eff6ff;
    border-color: #2563eb;
    color: #2563eb;
}

[data-testid="stSidebar"] .stButton > button {
    background: #2563eb;
    border: none;
    color: white;
    font-weight: 600;
}

[data-testid="stSidebar"] .stButton > button p {
    color: white;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #1d4ed8;
}

/* Chat input */

[data-testid="stChatInput"] {
    border-radius: 15px;
    background: white;
    border: 1px solid #cbd5e1;
}

[data-testid="stChatInput"] textarea {
    color: #0f172a;
    background: white;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8;
}

[data-testid="stBottom"] {
    background-color: #f8fafc;
}

[data-testid="stBottom"] > div {
    background-color: #f8fafc;
}

/* Expanders */

[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background-color: #f8fafc;
}

[data-testid="stExpander"] summary {
    color: #475569;
}

/* Chart container */

.chart-heading {
    font-size: 15px;
    font-weight: 700;
    color: #1e40af;
    padding: 10px 0;
}

/* Footer */

.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 11px;
    padding: 20px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""")


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================================
# AGENT LABELS
# ==================================================

AGENT_NAMES = {
    "sql_analyst": "🗄️ SQL Analyst Agent",
    "business_agent": "📊 Business Insights Agent",
    "direct_response": "🤖 IntelliOps Assistant"
}


# ==================================================
# CHART DIRECTORY
# ==================================================

CHART_DIRECTORY = (
    Path(__file__).resolve().parent / "outputs" / "charts"
).resolve()


# ==================================================
# DISPLAY RESPONSE AND INLINE CHARTS
# ==================================================

def display_response(answer):

    # Detect Windows and Linux chart paths
    pattern = r"outputs[\\/]+charts[\\/]+[\w-]+\.html"

    chart_paths = re.findall(pattern, answer)

    # Remove Markdown chart links completely
    clean_answer = re.sub(
        r"\[[^\]]*\]\(\s*`?" + pattern + r"`?\s*\)",
        "",
        answer
    )

    # Remove remaining raw chart paths
    clean_answer = re.sub(
        r"`?" + pattern + r"`?",
        "",
        clean_answer
    )

    # Remove empty chart labels
    clean_answer = re.sub(
        r"(?im)^[ \t]*(?:[-*]\s+)?(?:\*\*)?"
        r"(?:Line chart|Bar chart|Pie chart|Scatter plot|"
        r"Chart|Generated|Visualization)"
        r"(?:\*\*)?:?(?:\*\*)?[ \t]*$",
        "",
        clean_answer
    )

    # Display the analytical response
    if clean_answer.strip():
        st.markdown(clean_answer.strip())

    # Prevent duplicate charts
    displayed_files = set()

    # Render charts directly inside the conversation
    for chart_path in chart_paths:

        filename = Path(
            chart_path.replace("\\", "/")
        ).name

        if filename in displayed_files:
            continue

        displayed_files.add(filename)

        path = (CHART_DIRECTORY / filename).resolve()

        # Restrict access to the chart directory
        if path.parent != CHART_DIRECTORY:
            continue

        if not path.is_file():

            st.warning("Generated chart file was not found.")
            continue

        try:

            html_content = path.read_text(
                encoding="utf-8"
            )

            with st.container(border=True):

                st.html("""
                <div class="chart-heading">
                    📊 Interactive Visualization
                </div>
                """)

                components.html(
                    html_content,
                    height=550,
                    scrolling=True
                )

        except Exception:

            st.warning(
                "Unable to display the generated chart."
            )


# ==================================================
# DISPLAY ASSISTANT MESSAGE
# ==================================================

def display_assistant(message):

    agent_name = AGENT_NAMES.get(
        message.get("agent"),
        "🤖 IntelliOps Assistant"
    )

    elapsed = message.get("elapsed", 0)

    st.html(f"""
    <span class="agent-badge">
        {escape(agent_name)}
    </span>
    <span class="response-time">
        ⏱ {elapsed:.2f}s
    </span>
    """)

    display_response(message["content"])

    if message.get("reasoning"):

        with st.expander("🔍 Agent Routing Details"):

            st.markdown("**Selected Agent**")

            st.code(
                message.get("agent", ""),
                language="text"
            )

            st.markdown("**Routing Justification**")

            st.write(message["reasoning"])

            st.markdown("**Response Time**")

            st.write(f"{elapsed:.2f} seconds")


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.html("""
    <div class="sidebar-brand">◈ IntelliOps-AI</div>
    <div class="sidebar-subtitle">
        Intelligent Business Analytics
    </div>
    """)

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()

    st.html("""
    <div class="section-label">AGENT NETWORK</div>

    <div class="agent-card">
        🧠 <b>Supervisor Agent</b>
        <div class="agent-description">
            Intelligent routing and orchestration
        </div>
    </div>

    <div class="agent-card">
        🗄️ <b>SQL Analyst Agent</b>
        <div class="agent-description">
            Natural language database retrieval
        </div>
    </div>

    <div class="agent-card">
        📊 <b>Business Insights Agent</b>
        <div class="agent-description">
            Analytics, reasoning and visualization
        </div>
    </div>

    <div class="section-label">ANALYTICAL TOOLS</div>

    <div class="agent-card">
        ⚖️ Metric Comparison
    </div>

    <div class="agent-card">
        📈 Statistical Analysis
    </div>

    <div class="agent-card">
        🎨 Data Visualization
    </div>

    <div class="agent-card">
        🔄 Autonomous Data Retrieval
    </div>

    <div class="section-label">TECHNOLOGY STACK</div>

    <span class="tech-tag">LangGraph</span>
    <span class="tech-tag">LangChain</span>
    <span class="tech-tag">OpenAI</span>
    <span class="tech-tag">PostgreSQL</span>
    <span class="tech-tag">Supabase</span>
    <span class="tech-tag">Plotly</span>
    <span class="tech-tag">Pandas</span>
    <span class="tech-tag">Streamlit</span>
    """)

    st.divider()

    st.caption(
        f"Messages in session: "
        f"{len(st.session_state.messages)}"
    )

    st.caption("IntelliOps-AI · Version 0.1")


# ==================================================
# MAIN HEADER
# ==================================================

st.html("""
<div class="hero">
    <div class="hero-tag">
        MULTI-AGENT INTELLIGENCE PLATFORM
    </div>
    <div class="hero-title">
        Your Data. Intelligent Decisions.
    </div>
    <div class="hero-subtitle">
        Transform complex business data into actionable
        insights through intelligent agents, autonomous
        analytics and interactive visualizations.
    </div>
</div>
""")


# ==================================================
# WELCOME SCREEN
# ==================================================

suggested_question = None

if not st.session_state.messages:

    st.markdown("### Explore your business data")

    features = [
        (
            "🗄️",
            "Query Your Data",
            "Retrieve business information using natural language."
        ),
        (
            "📈",
            "Analyze Performance",
            "Compare metrics and discover performance trends."
        ),
        (
            "🔍",
            "Detect Anomalies",
            "Identify unusual patterns and statistical outliers."
        ),
        (
            "📊",
            "Visualize Insights",
            "Generate interactive charts from business data."
        )
    ]

    columns = st.columns(4)

    for col, feature in zip(columns, features):

        icon, title, description = feature

        with col:

            st.html(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    {escape(icon)}
                </div>
                <div class="feature-title">
                    {escape(title)}
                </div>
                <div class="feature-description">
                    {escape(description)}
                </div>
            </div>
            """)

    st.write("")

    st.markdown("### ✨ Try a suggested question")

    suggestions = [
        "How many completed rides are in the database?",

        "Analyze monthly completed-ride revenue, identify "
        "potential anomalies and generate a line chart.",

        "Compare completed-ride revenue between January "
        "2025 and January 2026.",

        "Analyze the correlation between ride distance "
        "and fare and generate a scatter plot.",

        "Compare completed-payment revenue across payment "
        "methods and generate a bar chart.",

        "Investigate the decline in completed-ride revenue "
        "between January and February 2026."
    ]

    col1, col2 = st.columns(2)

    for index, question in enumerate(suggestions):

        with col1 if index % 2 == 0 else col2:

            if st.button(
                question,
                key=f"suggestion_{index}",
                use_container_width=True
            ):

                suggested_question = question

    st.html("""
    <div class="footer">
        Powered by intelligent agent orchestration
        and live database retrieval.
    </div>
    """)


# ==================================================
# DISPLAY CONVERSATION HISTORY
# ==================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.markdown(message["content"])

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            display_assistant(message)


# ==================================================
# USER INPUT
# ==================================================

chat_input = st.chat_input(
    "Ask anything about your business data..."
)

question = chat_input or suggested_question


# ==================================================
# EXECUTE MULTI-AGENT WORKFLOW
# ==================================================

if question and question.strip():

    question = question.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(question)

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        try:

            start_time = time.perf_counter()

            with st.spinner(
                "IntelliOps-AI is analyzing your request..."
            ):

                response = supervisor_agent.invoke({
                    "user_question": question
                })

            elapsed_time = (
                time.perf_counter() - start_time
            )

            assistant_message = {
                "role": "assistant",
                "content": response["final_response"],
                "agent": response["selected_agent"],
                "reasoning": response.get("reasoning", ""),
                "elapsed": elapsed_time
            }

            st.session_state.messages.append(
                assistant_message
            )

            st.rerun()

        except Exception as error:

            # Log the error in the terminal
            print("IntelliOps-AI Error:", error)

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "Unable to complete your request. "
                    "Please try again."
                ),
                "agent": "direct_response",
                "elapsed": time.perf_counter() - start_time
            })

            st.rerun()


