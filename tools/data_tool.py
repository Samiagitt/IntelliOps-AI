
from langchain_core.tools import tool
from agents.sql_analyst import sql_analyst


@tool
def request_data(question: str) -> dict:
    """Request business data from the SQL Analyst Agent.

    Use this tool whenever database records, aggregated
    metrics, historical data, or additional information
    are required for business analysis.

    Provide a clear natural language question.
    """

    input_schema = {
        "messages": [],
        "user_question": question,
        "curated_question": "",
        "prompt_query": "",
        "generated_SQL_Query": "",
        "is_safe": "No",
        "comments": "",
        "result": None,
        "final_response": ""
    }

    try:

        response = sql_analyst.invoke(input_schema)

        # Check SQL safety decision
        if response["is_safe"] != "Yes":
            return {
                "status": "rejected",
                "reason": response["comments"]
            }

        # Check execution failure
        if response["result"] is None:
            return {
                "status": "error",
                "message": "SQL execution failed"
            }

        # Return structured data
        return {
            "status": "success",
            "question": question,
            "sql_query": response["generated_SQL_Query"],
            "data": response["result"],
            "row_count": len(response["result"])
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
