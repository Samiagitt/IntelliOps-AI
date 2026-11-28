from agents.sql_analyst import sql_analyst
from agents.business_agent import business_agent

from Models.schema import SupervisorSchema, RouterSchema
from utils.llm_pick import pick_llm

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

llm = pick_llm("low")

router_llm = llm.with_structured_output(RouterSchema)

def route_question(state: SupervisorSchema) -> dict:
    
    prompt = f"""
    You are the Supervisor Agent of IntelliOps-AI.

    Your responsibility is to route the user's question
    to the most appropriate specialized agent.

    Available routes:

    1. sql_analyst:
       - Database retrieval
       - Simple aggregations
       - Counts, totals and factual business data

    2. business_agent:
       - Business performance analysis
       - Metric comparisons
       - Trend analysis
       - Anomaly detection
       - Correlation analysis
       - Data visualization
       - Business recommendations

    3. direct_response:
       - Greetings
       - Questions about system capabilities
       - General conversational questions that do not
         require database retrieval or business analysis

    Select the most appropriate route.
    Do not answer the user's question yourself.

    User question:
    {state.user_question}
    """

    response = router_llm.invoke(prompt)

    return {
        "selected_agent": response.selected_agent,
        "reasoning": response.reasoning
    }

def call_sql_analyst(state: SupervisorSchema) -> dict:
    
    input_schema = {
        "messages": [],
        "user_question": state.user_question,
        "curated_question": "",
        "prompt_query": "",
        "generated_SQL_Query": "",
        "is_safe": "No",
        "comments": "",
        "result": None,
        "final_response": ""
    }

    response = sql_analyst.invoke(input_schema)

    return {
        "final_response": response["final_response"]
    }
    
def call_business_agent(state: SupervisorSchema) -> dict:
    
    response = business_agent.invoke(
        {
            "messages": [
                HumanMessage(content=state.user_question)
            ]
        },
        config={"recursion_limit": 20}
    )

    return {
        "final_response": response["messages"][-1].text
    }
    
def direct_response(state: SupervisorSchema) -> dict:
    
    prompt = f"""
    You are IntelliOps-AI, a business intelligence
    and decision support assistant.

    You can help users retrieve business data,
    compare metrics, analyze trends, detect anomalies,
    and generate visualizations.

    Respond politely and concisely.
    Do not invent database information.

    User question:
    {state.user_question}
    """

    response = llm.invoke(prompt)

    return {
        "final_response": response.text
    }
    
supervisor_graph = StateGraph(SupervisorSchema)

supervisor_graph.add_node("router", route_question)

supervisor_graph.add_node("sql_analyst", call_sql_analyst)

supervisor_graph.add_node("business_agent", call_business_agent)

supervisor_graph.add_node("direct_response", direct_response)

#routing condition
def routing_condition(state: SupervisorSchema) -> str:
    return state.selected_agent

supervisor_graph.add_edge(START, "router")

supervisor_graph.add_conditional_edges(
    "router",
    routing_condition,
    {
        "sql_analyst": "sql_analyst",
        "business_agent": "business_agent",
        "direct_response": "direct_response"
    }
)

supervisor_graph.add_edge("sql_analyst", END)

supervisor_graph.add_edge("business_agent", END)

supervisor_graph.add_edge("direct_response", END)

supervisor_agent = supervisor_graph.compile()

if __name__ == "__main__":
    
    test_questions = [
        "How many completed rides are in the database?",
        "Analyze monthly revenue trends and generate a line chart.",
        "Hello, what can you do?"
    ]

    for question in test_questions:

        response = supervisor_agent.invoke({
            "user_question": question
        })

        print("\n" + "=" * 60)

        print("USER QUESTION:")
        print(question)

        print("\nSELECTED AGENT:")
        print(response["selected_agent"])

        print("\nROUTING REASON:")
        print(response["reasoning"])

        print("\nFINAL RESPONSE:")
        print(response["final_response"])