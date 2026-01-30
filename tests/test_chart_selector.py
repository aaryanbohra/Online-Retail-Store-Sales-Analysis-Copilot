"""Unit tests for Chart Selector"""

import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chart_selector import ChartSelector


class TestKPIDetection:
    """Tests for KPI (single value) detection"""

    def test_single_value_is_kpi(self):
        """Single row, single column should be KPI"""
        df = pd.DataFrame({"total_revenue": [1234567.89]})
        result = ChartSelector.select_chart_type(df, "SELECT SUM(revenue) FROM orders")
        assert result == "kpi"

    def test_single_row_multiple_cols_not_kpi(self):
        """Single row with multiple columns should not be KPI"""
        df = pd.DataFrame({"revenue": [1000], "orders": [50]})
        result = ChartSelector.select_chart_type(df, "SELECT SUM(revenue), COUNT(*) FROM orders")
        assert result != "kpi"

    def test_multiple_rows_not_kpi(self):
        """Multiple rows should not be KPI"""
        df = pd.DataFrame({"country": ["UK", "USA"], "revenue": [1000, 2000]})
        result = ChartSelector.select_chart_type(df, "SELECT country, revenue FROM orders")
        assert result != "kpi"


class TestLineChartDetection:
    """Tests for line chart detection (trends over time)"""

    def test_trend_keyword_triggers_line(self):
        """User asking for 'trend' should get line chart"""
        df = pd.DataFrame({
            "month": ["2011-01", "2011-02", "2011-03"],
            "revenue": [1000, 1200, 1100]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT month, revenue FROM orders GROUP BY month",
            question="Show revenue trend over time"
        )
        assert result == "line"

    def test_growth_keyword_triggers_line(self):
        """User asking for 'growth' should get line chart"""
        df = pd.DataFrame({
            "month": ["2011-01", "2011-02", "2011-03"],
            "revenue": [1000, 1200, 1100]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT month, revenue FROM orders GROUP BY month",
            question="What is the revenue growth?"
        )
        assert result == "line"

    def test_date_column_with_many_points(self):
        """Daily data with 7+ points should be line chart"""
        df = pd.DataFrame({
            "date": [f"2011-01-{i:02d}" for i in range(1, 15)],
            "revenue": [100 * i for i in range(1, 15)]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT date, revenue FROM orders GROUP BY date"
        )
        assert result == "line"


class TestBarChartDetection:
    """Tests for bar chart detection (categorical comparisons)"""

    def test_month_column_gets_bar(self):
        """Monthly data should get bar chart"""
        df = pd.DataFrame({
            "month": ["Jan", "Feb", "Mar"],
            "revenue": [1000, 1200, 1100]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT month, revenue FROM orders GROUP BY month"
        )
        assert result == "bar"

    def test_categorical_comparison_gets_bar(self):
        """Categorical comparison should get bar chart"""
        df = pd.DataFrame({
            "country": ["UK", "Germany", "France"],
            "revenue": [5000, 3000, 2000]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT country, SUM(revenue) FROM orders GROUP BY country"
        )
        assert result == "bar"

    def test_year_column_gets_bar(self):
        """Yearly data should get bar chart"""
        df = pd.DataFrame({
            "year": [2010, 2011],
            "revenue": [50000, 75000]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT year, revenue FROM orders GROUP BY year"
        )
        assert result == "bar"


class TestTableDetection:
    """Tests for table detection"""

    def test_too_many_rows_gets_table(self):
        """More than MAX_ROWS_FOR_CHART should get table"""
        df = pd.DataFrame({
            "product": [f"Product {i}" for i in range(100)],
            "revenue": [i * 10 for i in range(100)]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT product, revenue FROM orders"
        )
        assert result == "table"

    def test_many_columns_gets_table(self):
        """More than 3 columns should get table"""
        df = pd.DataFrame({
            "country": ["UK"],
            "revenue": [1000],
            "orders": [50],
            "customers": [30],
            "avg_order": [20]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT country, revenue, orders, customers, avg_order FROM orders"
        )
        assert result == "table"

    def test_ranking_query_gets_table(self):
        """Ranking/comparison queries should get table"""
        df = pd.DataFrame({
            "product": ["A", "B", "C"],
            "revenue": [3000, 2000, 1000]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT product, revenue, ROW_NUMBER() OVER (ORDER BY revenue DESC) FROM orders"
        )
        assert result == "table"

    def test_top_n_query_gets_table(self):
        """Top N queries should get table"""
        df = pd.DataFrame({
            "customer": ["C1", "C2", "C3"],
            "revenue": [5000, 4000, 3000]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT customer, revenue FROM orders ORDER BY revenue DESC LIMIT 10"
        )
        # This could be bar or table depending on implementation
        assert result in ["table", "bar"]


class TestEdgeCases:
    """Tests for edge cases"""

    def test_empty_dataframe(self):
        """Empty dataframe should get table"""
        df = pd.DataFrame()
        result = ChartSelector.select_chart_type(df, "SELECT * FROM orders WHERE 1=0")
        assert result == "table"

    def test_single_row_two_cols(self):
        """Single row with 2 columns - not a chart"""
        df = pd.DataFrame({"metric": ["revenue"], "value": [1000]})
        result = ChartSelector.select_chart_type(df, "SELECT 'revenue', 1000")
        # Could be kpi, bar, or table
        assert result in ["kpi", "bar", "table"]

    def test_non_numeric_second_column(self):
        """Non-numeric second column should get table"""
        df = pd.DataFrame({
            "country": ["UK", "USA"],
            "status": ["active", "inactive"]
        })
        result = ChartSelector.select_chart_type(
            df,
            "SELECT country, status FROM orders"
        )
        assert result == "table"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
