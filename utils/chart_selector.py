"""Logic for selecting appropriate chart type"""

import pandas as pd
from config import MAX_ROWS_FOR_CHART

class ChartSelector:
    """Determines best chart type for query results

    Rules:
    - Comparing values → Table or Bar chart
    - Trend lines or growth over time → Line chart
    """

    @staticmethod
    def select_chart_type(df: pd.DataFrame, sql: str, question: str = "") -> str:
        """Select appropriate chart type based on data shape and query intent

        Args:
            df: Query results dataframe
            sql: Generated SQL query
            question: Original user question (optional)
        """

        # Single value = KPI
        if len(df) == 1 and len(df.columns) == 1:
            return 'kpi'

        # Too many rows = table
        if len(df) > MAX_ROWS_FOR_CHART:
            return 'table'

        # Analyze user question for intent
        question_lower = question.lower() if question else ""

        # HARDCODED: If user asks about trend or over time, force line chart
        trend_keywords = ['trend', 'over time', 'overtime', 'growth', 'change', 'evolution',
                         'progression', 'trajectory', 'pattern over', 'how has', 'how did']

        user_wants_trend = any(keyword in question_lower for keyword in trend_keywords)

        # Analyze column names early for trend detection
        col_names = [col.lower() for col in df.columns]
        col_names_str = ' '.join(col_names)
        has_date = 'date' in col_names_str and 'month' not in col_names_str
        has_time_period = any(word in col_names_str for word in ['month', 'year', 'week', 'quarter'])

        # PRIORITY: If user explicitly asks for trend/growth AND has time data → force line chart
        # This overrides column count or other rules
        if user_wants_trend and (has_date or has_time_period) and len(df) >= 2:
            return 'line'

        # Analyze SQL query patterns
        sql_lower = sql.lower()

        # Window functions, ranking, top N = comparison → table
        is_comparison = any(keyword in sql_lower for keyword in [
            'row_number', 'rank', 'dense_rank', 'partition by',
            'max(', 'min(', 'top ', 'highest', 'lowest', 'best', 'worst'
        ])

        if is_comparison:
            return 'table'

        # Multiple columns = table
        if len(df.columns) > 3:
            return 'table'

        # Simple 2-column numeric data
        if len(df.columns) == 2 and len(df) <= 20:
            if pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
                # Line chart for daily data with 7+ points
                if has_date and len(df) >= 7:
                    return 'line'

                # Bar chart ONLY for categorical comparisons across multiple items
                # Need at least 2 rows to make a meaningful bar chart
                if has_time_period and len(df) >= 2:
                    return 'bar'

                # Bar chart for non-time categorical data with multiple items
                if not has_time_period and not has_date and len(df) >= 2 and len(df) <= 15:
                    return 'bar'

        # Default to table for everything else
        return 'table'