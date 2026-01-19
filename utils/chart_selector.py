import pandas as pd
from config import MAX_ROWS_FOR_CHART


class ChartSelector:
    @staticmethod
    def select_chart_type(df: pd.DataFrame, sql: str, question: str = "") -> str:
        if len(df) == 1 and len(df.columns) == 1:
            return 'kpi'

        if len(df) > MAX_ROWS_FOR_CHART:
            return 'table'

        question_lower = question.lower() if question else ""
        trend_keywords = ['trend', 'over time', 'overtime', 'growth', 'change', 'evolution',
                          'progression', 'trajectory', 'pattern over', 'how has', 'how did']
        user_wants_trend = any(keyword in question_lower for keyword in trend_keywords)

        col_names = [col.lower() for col in df.columns]
        col_names_str = ' '.join(col_names)
        has_date = 'date' in col_names_str and 'month' not in col_names_str
        has_time_period = any(word in col_names_str for word in ['month', 'year', 'week', 'quarter'])

        if user_wants_trend and (has_date or has_time_period) and len(df) >= 2:
            return 'line'

        sql_lower = sql.lower()
        is_comparison = any(keyword in sql_lower for keyword in [
            'row_number', 'rank', 'dense_rank', 'partition by',
            'max(', 'min(', 'top ', 'highest', 'lowest', 'best', 'worst'
        ])

        if is_comparison:
            return 'table'

        if len(df.columns) > 3:
            return 'table'

        if len(df.columns) == 2 and len(df) <= 20:
            if pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
                if has_date and len(df) >= 7:
                    return 'line'

                if has_time_period and len(df) >= 2:
                    return 'bar'

                if not has_time_period and not has_date and len(df) >= 2 and len(df) <= 15:
                    return 'bar'

        return 'table'
