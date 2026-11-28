from langchain_core.tools import tool
import pandas as pd
import numpy as np
from typing import Literal, Optional
@tool
def compare_metrics(metric_name:str, previous_value: float, current_value: float)->dict:
    """Compare two business metric values and calculate their
    difference, percentage change, and direction."""
    
    abs_diff=round(current_value-previous_value,2)
    
    if previous_value==0:
        percentage_change=None
    else:
        percentage_change=round((abs_diff/previous_value)*100,2)
    
    #determine direction
    if current_value>previous_value:
        direction="increase"
    elif current_value<previous_value:
        direction="decrease"
    else:
        direction="unchancged"
        
    return {
        "metric":metric_name,
        "previous_value": previous_value,
        "current_value":current_value,
        "absolute_difference": abs_diff,
        "percentage_change":percentage_change,
        "direction":direction
    }

@tool
def analyze_data(data:list[dict],column:str, analysis_type:str, second_col:str=None)->dict:  #additional col(second col) for correlation analysis
    """Perform statistical analysis on business data.

The analysis_type parameter must be exactly one of:

- "summary": Calculate mean, median, min, max and standard deviation.
- "trend": Analyze changes over chronological periods.
- "correlation": Calculate Pearson correlation between two columns.
- "anomaly": Detect potential outliers using the IQR method.

Perform only ONE analysis type per tool call.
For multiple analyses, call this tool separately for each type.

For trend analysis, provide chronologically ordered data
with equally spaced periods and no missing values.

For correlation, provide second_col.
"""
    df=pd.DataFrame(data)
    df = pd.DataFrame(data)

    if column not in df.columns:
        return {"error": "Column not found"}

    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": "Column must contain numeric data"}

    values = df[column].dropna()

    if values.empty:
        return {"error": "No numeric values available"}

    if analysis_type == "summary":
        mean = values.mean()
        median = values.median()
        minimum = values.min()
        maximum = values.max()
        std_dev = values.std()

        return {
            "column": column,
            "analysis_type": analysis_type,
            "mean": round(float(mean), 2),
            "median": round(float(median), 2),
            "min": float(minimum),
            "max": float(maximum),
            "standard_deviation": round(float(std_dev), 2)
                if len(values) > 1 else None
        }
    # 2. Trend analysis
    elif analysis_type == "trend":

        if len(values) < 2:
            return {"error": "At least two values are required"}

        if len(values) != len(df):
            return {"error": "Trend analysis requires no missing values"}

        starting_value = float(values.iloc[0])
        ending_value = float(values.iloc[-1])

        if starting_value == 0:
            percentage_change = None
        else:
            percentage_change = round(
                ((ending_value - starting_value) / starting_value) * 100, 2
            )

        average_change = values.diff().mean()

        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        if np.isclose(slope, 0):
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "column": column,
            "analysis_type": analysis_type,
            "starting_value": starting_value,
            "ending_value": ending_value,
            "percentage_change": percentage_change,
            "average_change_per_period": round(float(average_change), 2),
            "slope": round(float(slope), 4),
            "trend": trend
        }

    # 3. Correlation analysis
    elif analysis_type == "correlation":

        if second_col is None:
            return {"error": "Second column is required"}

        if second_col not in df.columns:
            return {"error": "Second column not found"}

        if not pd.api.types.is_numeric_dtype(df[second_col]):
            return {"error": "Second column must contain numeric data"}

        paired_data = df[[column, second_col]].dropna()

        if len(paired_data) < 3:
            return {"error": "At least three paired observations are required"}

        if not np.isfinite(paired_data.to_numpy()).all():
            return {"error": "Data contains infinite values"}

        if (paired_data.iloc[:, 0].nunique() < 2 or
                paired_data.iloc[:, 1].nunique() < 2):
            return {"error": "Correlation is undefined for constant values"}

        correlation = paired_data.iloc[:, 0].corr(
            paired_data.iloc[:, 1]
        )

        if not np.isfinite(correlation):
            return {"error": "Correlation could not be calculated"}

        if abs(correlation) < 0.3:
            strength = "weak"
        elif abs(correlation) < 0.7:
            strength = "moderate"
        else:
            strength = "strong"

        if np.isclose(correlation, 0):
            direction = "none"
        elif correlation > 0:
            direction = "positive"
        else:
            direction = "negative"

        return {
            "column": column,
            "second_column": second_col,
            "analysis_type": analysis_type,
            "correlation": round(float(correlation), 4),
            "strength": strength,
            "direction": direction,
            "sample_size": len(paired_data)
        }

    # 4. Anomaly detection using IQR
    elif analysis_type == "anomaly":

        if len(values) < 4:
            return {"error": "At least four values are required"}

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        anomalies = values[
            (values < lower_bound) |
            (values > upper_bound)
        ]

        return {
            "column": column,
            "analysis_type": analysis_type,
            "lower_bound": round(float(lower_bound), 2),
            "upper_bound": round(float(upper_bound), 2),
            "total_observations": len(values),
            "anomaly_count": len(anomalies),
            "anomaly_percentage": round(
                (len(anomalies) / len(values)) * 100, 2
            ),
            "anomalies": [
                {
                    "row_index": int(index),
                    "value": float(value)
                }
                for index, value in anomalies.items()
            ]
        }

    return {"error": "Unsupported analysis type"} 
