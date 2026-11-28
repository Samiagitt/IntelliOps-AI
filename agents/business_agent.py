from tools.analytics_tool import compare_metrics, analyze_data
from tools.visualization_tool import generate_visualization
from tools.data_tool import request_data
from utils.llm_pick import pick_llm
from Models.schema import BusinessAgentSchema
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

tools = [
    compare_metrics,
    analyze_data,
    generate_visualization,
    request_data
]

llm = pick_llm("medium")

llm = llm.model_copy(
    update={"use_responses_api": True}
)

llm_with_tools = llm.bind_tools(tools)

system_prompt = """
You are a Business Intelligence and Data Analysis Agent.

Your responsibilities are to:

- Retrieve business data from the SQL Analyst Agent.
- Compare business performance metrics.
- Analyze trends, correlations and potential anomalies.
- Generate appropriate business visualizations.
- Provide actionable business insights.

Use the available tools whenever calculations,
database retrieval or visualization are required.

Inspect the returned column names before calling
analytical or visualization tools.

If additional information is needed, request it
using the request_data tool.

Never invent business data or analytical results.

Do not confuse correlation with causation.
When using analyze_data, the analysis_type must be
exactly one of: summary, trend, correlation, anomaly.

Never combine multiple analysis types in one tool call.
Call analyze_data separately for each required analysis.

If a tool returns an error, inspect the supported
arguments and retry with valid parameters.

Reuse previously retrieved data instead of requesting
the same data again unnecessarily.

Explicitly disclose any analysis that could not be
completed successfully.

If a tool fails, inspect the error and correct
your arguments when possible.

Provide clear, concise and evidence-based findings.
"""

def business_agent_node(state: BusinessAgentSchema) -> dict:
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        *state.messages
    ])

    return {
        "messages": [response]
    }
    
business_graph = StateGraph(BusinessAgentSchema)
business_graph.add_node("business_agent", business_agent_node)
business_graph.add_node("tools",ToolNode(tools))
business_graph.add_edge(START,"business_agent")
business_graph.add_conditional_edges("business_agent",tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)
business_graph.add_edge("tools","business_agent")  #ReAct Loop
business_agent = business_graph.compile()

