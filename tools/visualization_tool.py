import pandas as pd
import plotly.express as px
from typing import Literal
from langchain_core.tools import tool
from pathlib import Path
from uuid import uuid4


@tool
def generate_visualization(
    data: list[dict],
    chart_type: Literal["bar", "line", "pie", "scatter"],
    x_column: str,
    y_column: str,
    title: str
) -> dict:
    """Generate a business data visualization.

    Use bar charts for category comparisons, line charts
    for chronological trends, pie charts for proportions,
    and scatter charts for numerical relationships.
    """

    df = pd.DataFrame(data)

    # Input validation
    if df.empty:
        return {"error": "Dataset is empty"}

    if x_column not in df.columns or y_column not in df.columns:
        return {"error": "Required column not found"}

    if not pd.api.types.is_numeric_dtype(df[y_column]):
        return {"error": "Y column must contain numeric data"}

    df = df.dropna(subset=[x_column, y_column])

    if df.empty:
        return {"error": "No valid observations"}

    try:
        # Bar chart
        if chart_type == "bar":
            fig = px.bar(
                df, x=x_column, y=y_column, title=title
            )

        # Line chart
        elif chart_type == "line":
            fig = px.line(
                df, x=x_column, y=y_column,
                title=title, markers=True
            )

        # Pie chart
        elif chart_type == "pie":

            if (df[y_column] < 0).any() or df[y_column].sum() <= 0:
                return {"error": "Invalid values for pie chart"}

            fig = px.pie(
                df, names=x_column,
                values=y_column, title=title
            )

        # Scatter chart
        elif chart_type == "scatter":

            if not pd.api.types.is_numeric_dtype(df[x_column]):
                return {"error": "X column must contain numeric data"}

            fig = px.scatter(
                df, x=x_column, y=y_column, title=title
            )

        else:
            return {"error": "Unsupported chart type"}

        # Create output directory
        output_dir = Path("outputs/charts")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        filename = f"{chart_type}_{uuid4().hex[:8]}.html"
        file_path = output_dir / filename

        # Save interactive chart
        fig.write_html(str(file_path))

        return {
            "status": "success",
            "chart_type": chart_type,
            "title": title,
            "file_path": str(file_path),
            "data_points": len(df)
        }

    except Exception as e:
        return {"error": str(e)}
