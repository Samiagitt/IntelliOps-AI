
from tools.data_tool import request_data
from tools.analytics_tool import compare_metrics, analyze_data
from tools.visualization_tool import generate_visualization
import json


if __name__ == "__main__":

    # 1. Retrieve actual business data
    result = request_data.invoke({
        "question": """
        Calculate total fare revenue from completed rides
        grouped by request month for all available months.

        Return columns named month and revenue.
        Sort by month in chronological order.
        """
    })

    if result["status"] != "success":
        print(result)
        raise SystemExit(1)

    # Normalize column names
    data = []

    for row in result["data"]:

        month = row.get("month", row.get("request_month"))

        revenue = row.get(
            "revenue", row.get("total_fare_revenue")
        )

        if month is None or revenue is None:
            raise SystemExit(
                f"Unexpected column names or missing values: {row}"
            )

        data.append({
            "month": month,
            "revenue": revenue
        })

    if len(data) < 2:
        raise SystemExit("Insufficient data for analysis")

    # Sort data chronologically
    data.sort(key=lambda row: row["month"])

    print("\nRETRIEVED DATA:")
    print(json.dumps(data, indent=4))


    # 2. Compare first and last month
    comparison = compare_metrics.invoke({
        "metric_name": "Monthly Revenue",
        "previous_value": data[0]["revenue"],
        "current_value": data[-1]["revenue"]
    })

    print("\nMETRIC COMPARISON:")
    print(json.dumps(comparison, indent=4))


    # 3. Perform statistical analysis
    for analysis in ["summary", "trend", "anomaly"]:

        analysis_result = analyze_data.invoke({
            "data": data,
            "column": "revenue",
            "analysis_type": analysis
        })

        print(f"\n{analysis.upper()} ANALYSIS:")
        print(json.dumps(analysis_result, indent=4))


    # 4. Generate visualization
    chart = generate_visualization.invoke({
        "data": data,
        "chart_type": "line",
        "x_column": "month",
        "y_column": "revenue",
        "title": "Monthly Fare Revenue Analysis"
    })

    print("\nVISUALIZATION:")
    print(json.dumps(chart, indent=4))
