"""SQL Execution Tests - Verify query patterns work against real database"""

import pytest
import sqlite3
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_PATH


@pytest.fixture
def db_connection():
    """Create database connection for tests"""
    conn = sqlite3.connect(DATABASE_PATH)
    yield conn
    conn.close()


def execute_query(conn, sql):
    """Execute SQL and return DataFrame"""
    return pd.read_sql_query(sql, conn)


class TestDatabaseConnection:
    """Tests for database connectivity"""

    def test_database_exists(self, db_connection):
        """Database file should exist and be accessible"""
        assert db_connection is not None

    def test_tables_exist(self, db_connection):
        """Required tables should exist"""
        tables = execute_query(
            db_connection,
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = tables['name'].tolist()
        assert 'orders' in table_names
        assert 'order_items' in table_names
        assert 'customers' in table_names

    def test_orders_has_data(self, db_connection):
        """Orders table should have data"""
        result = execute_query(db_connection, "SELECT COUNT(*) as cnt FROM orders")
        assert result['cnt'].iloc[0] > 0

    def test_order_items_has_data(self, db_connection):
        """Order items table should have data"""
        result = execute_query(db_connection, "SELECT COUNT(*) as cnt FROM order_items")
        assert result['cnt'].iloc[0] > 0


class TestBasicQueryPatterns:
    """Tests for basic query patterns from the prompt"""

    def test_total_revenue(self, db_connection):
        """Calculate total revenue"""
        sql = "SELECT SUM(revenue) AS total_revenue FROM order_items"
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert result['total_revenue'].iloc[0] > 0

    def test_revenue_by_country(self, db_connection):
        """Revenue grouped by country"""
        sql = """
        SELECT o.country, SUM(oi.revenue) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        GROUP BY o.country
        ORDER BY total_revenue DESC
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0
        assert 'country' in result.columns
        assert 'total_revenue' in result.columns

    def test_revenue_by_year(self, db_connection):
        """Revenue grouped by year"""
        sql = """
        SELECT strftime('%Y', o.invoice_date) AS year, SUM(oi.revenue) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        GROUP BY strftime('%Y', o.invoice_date)
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0
        assert 'year' in result.columns

    def test_monthly_revenue_trend(self, db_connection):
        """Monthly revenue trend"""
        sql = """
        SELECT strftime('%Y-%m', o.invoice_date) AS month, SUM(oi.revenue) AS monthly_revenue
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        GROUP BY strftime('%Y-%m', o.invoice_date)
        ORDER BY month
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0
        assert 'month' in result.columns
        assert 'monthly_revenue' in result.columns


class TestWindowFunctions:
    """Tests for window function patterns"""

    def test_row_number_ranking(self, db_connection):
        """ROW_NUMBER for ranking"""
        sql = """
        SELECT country, total_revenue, rn FROM (
            SELECT o.country, SUM(oi.revenue) AS total_revenue,
                   ROW_NUMBER() OVER (ORDER BY SUM(oi.revenue) DESC) AS rn
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            GROUP BY o.country
        ) WHERE rn <= 5
        """
        result = execute_query(db_connection, sql)
        assert len(result) <= 5
        assert 'rn' in result.columns

    def test_top_n_per_group(self, db_connection):
        """Top N per group using window functions"""
        sql = """
        SELECT country, customer_id, total_revenue FROM (
            SELECT o.country, o.customer_id, SUM(oi.revenue) AS total_revenue,
                   ROW_NUMBER() OVER (PARTITION BY o.country ORDER BY SUM(oi.revenue) DESC) AS rn
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE o.customer_id IS NOT NULL
            GROUP BY o.country, o.customer_id
        ) WHERE rn <= 3
        ORDER BY country, total_revenue DESC
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0

    def test_lag_for_growth(self, db_connection):
        """LAG function for growth calculation"""
        sql = """
        SELECT month, monthly_revenue,
            LAG(monthly_revenue, 1) OVER (ORDER BY month) AS prev_month_revenue
        FROM (
            SELECT strftime('%Y-%m', o.invoice_date) AS month, SUM(oi.revenue) AS monthly_revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE strftime('%Y', o.invoice_date) = '2011'
            GROUP BY strftime('%Y-%m', o.invoice_date)
        ) ORDER BY month
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0
        assert 'prev_month_revenue' in result.columns


class TestSubqueryPatterns:
    """Tests for subquery patterns - critical for the failing query"""

    def test_nested_subquery_with_alias(self, db_connection):
        """Nested subquery must have alias"""
        sql = """
        SELECT AVG(monthly_revenue) AS avg_monthly_revenue FROM (
            SELECT SUM(oi.revenue) AS monthly_revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE strftime('%Y', o.invoice_date) = '2010'
            GROUP BY strftime('%Y-%m', o.invoice_date)
        ) AS monthly_totals
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert 'avg_monthly_revenue' in result.columns

    def test_cross_join_subqueries_with_aliases(self, db_connection):
        """CROSS JOIN with both subqueries having aliases"""
        sql = """
        SELECT
            low.month AS lowest_month,
            low.monthly_revenue AS lowest_revenue,
            avg_data.avg_monthly_revenue
        FROM (
            SELECT strftime('%Y-%m', o.invoice_date) AS month, SUM(oi.revenue) AS monthly_revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE strftime('%Y', o.invoice_date) = '2010'
            GROUP BY strftime('%Y-%m', o.invoice_date)
            ORDER BY monthly_revenue ASC
            LIMIT 1
        ) AS low
        CROSS JOIN (
            SELECT AVG(monthly_revenue) AS avg_monthly_revenue FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2010'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS monthly_totals
        ) AS avg_data
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert 'lowest_month' in result.columns
        assert 'lowest_revenue' in result.columns
        assert 'avg_monthly_revenue' in result.columns

    def test_subquery_in_from_needs_alias(self, db_connection):
        """Subquery in FROM clause needs alias - this pattern should work"""
        sql = """
        SELECT * FROM (
            SELECT o.country, COUNT(*) as order_count
            FROM orders o
            GROUP BY o.country
        ) AS country_orders
        WHERE order_count > 10
        """
        result = execute_query(db_connection, sql)
        assert len(result) >= 0  # May have results or not, but should not error


class TestDateFiltering:
    """Tests for date filtering patterns"""

    def test_filter_by_year(self, db_connection):
        """Filter by year using strftime"""
        sql = """
        SELECT SUM(oi.revenue) AS revenue_2011
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        WHERE strftime('%Y', o.invoice_date) = '2011'
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1

    def test_filter_by_month(self, db_connection):
        """Filter by specific month"""
        sql = """
        SELECT SUM(oi.revenue) AS revenue_jan_2011
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        WHERE strftime('%Y-%m', o.invoice_date) = '2011-01'
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1

    def test_daily_data_in_month(self, db_connection):
        """Daily data within a specific month"""
        sql = """
        SELECT strftime('%Y-%m-%d', o.invoice_date) AS date, SUM(oi.revenue) AS daily_revenue
        FROM order_items oi
        JOIN orders o ON oi.invoice_id = o.invoice_id
        WHERE strftime('%Y-%m', o.invoice_date) = '2011-01'
        GROUP BY strftime('%Y-%m-%d', o.invoice_date)
        ORDER BY date
        """
        result = execute_query(db_connection, sql)
        assert len(result) > 0


class TestComparisonQueries:
    """Tests for comparison query patterns (the user's failing query type)"""

    def test_min_vs_max(self, db_connection):
        """Compare minimum vs maximum"""
        sql = """
        SELECT
            min_data.min_revenue,
            max_data.max_revenue
        FROM (
            SELECT MIN(monthly_revenue) AS min_revenue FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2011'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS monthly
        ) AS min_data
        CROSS JOIN (
            SELECT MAX(monthly_revenue) AS max_revenue FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2011'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS monthly
        ) AS max_data
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert result['min_revenue'].iloc[0] <= result['max_revenue'].iloc[0]

    def test_value_vs_average(self, db_connection):
        """Compare specific value vs average - the user's query pattern"""
        sql = """
        SELECT
            specific.month AS lowest_month,
            specific.revenue AS lowest_revenue,
            average.avg_revenue
        FROM (
            SELECT strftime('%Y-%m', o.invoice_date) AS month, SUM(oi.revenue) AS revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE strftime('%Y', o.invoice_date) = '2010'
            GROUP BY strftime('%Y-%m', o.invoice_date)
            ORDER BY revenue ASC
            LIMIT 1
        ) AS specific
        CROSS JOIN (
            SELECT AVG(monthly_rev) AS avg_revenue FROM (
                SELECT SUM(oi.revenue) AS monthly_rev
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2010'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS months
        ) AS average
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert 'lowest_month' in result.columns
        assert 'lowest_revenue' in result.columns
        assert 'avg_revenue' in result.columns
        # Lowest should be <= average
        assert result['lowest_revenue'].iloc[0] <= result['avg_revenue'].iloc[0]


class TestSQLiteLimitations:
    """Tests for SQLite-specific workarounds (median, etc.)"""

    def test_median_calculation(self, db_connection):
        """Median calculation using LIMIT/OFFSET pattern"""
        sql = """
        SELECT AVG(monthly_revenue) AS median_monthly_revenue
        FROM (
            SELECT monthly_revenue
            FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2010'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS data
            ORDER BY monthly_revenue
            LIMIT 2 - (SELECT COUNT(*) FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2010'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS cnt) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM (
                SELECT SUM(oi.revenue) AS monthly_revenue
                FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                WHERE strftime('%Y', o.invoice_date) = '2010'
                GROUP BY strftime('%Y-%m', o.invoice_date)
            ) AS cnt)
        ) AS median_calc
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert 'median_monthly_revenue' in result.columns
        assert result['median_monthly_revenue'].iloc[0] > 0

    def test_lowest_vs_median_comparison(self, db_connection):
        """Compare lowest month revenue vs median - the user's query pattern"""
        sql = """
        SELECT
            low.month AS lowest_month,
            low.monthly_revenue AS lowest_revenue,
            median_data.median_monthly_revenue
        FROM (
            SELECT strftime('%Y-%m', o.invoice_date) AS month, SUM(oi.revenue) AS monthly_revenue
            FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
            WHERE strftime('%Y', o.invoice_date) = '2010'
            GROUP BY strftime('%Y-%m', o.invoice_date)
            ORDER BY monthly_revenue ASC
            LIMIT 1
        ) AS low
        CROSS JOIN (
            SELECT AVG(monthly_revenue) AS median_monthly_revenue
            FROM (
                SELECT monthly_revenue
                FROM (
                    SELECT SUM(oi.revenue) AS monthly_revenue
                    FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                    WHERE strftime('%Y', o.invoice_date) = '2010'
                    GROUP BY strftime('%Y-%m', o.invoice_date)
                ) AS data
                ORDER BY monthly_revenue
                LIMIT 2 - (SELECT COUNT(*) FROM (
                    SELECT SUM(oi.revenue) AS monthly_revenue
                    FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                    WHERE strftime('%Y', o.invoice_date) = '2010'
                    GROUP BY strftime('%Y-%m', o.invoice_date)
                ) AS cnt) % 2
                OFFSET (SELECT (COUNT(*) - 1) / 2 FROM (
                    SELECT SUM(oi.revenue) AS monthly_revenue
                    FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
                    WHERE strftime('%Y', o.invoice_date) = '2010'
                    GROUP BY strftime('%Y-%m', o.invoice_date)
                ) AS cnt)
            ) AS median_calc
        ) AS median_data
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1
        assert 'lowest_month' in result.columns
        assert 'lowest_revenue' in result.columns
        assert 'median_monthly_revenue' in result.columns


class TestEdgeCases:
    """Tests for edge cases and potential error scenarios"""

    def test_null_customer_handling(self, db_connection):
        """Handle NULL customer IDs gracefully"""
        sql = """
        SELECT COUNT(*) AS orders_with_customer
        FROM orders
        WHERE customer_id IS NOT NULL
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1

    def test_negative_quantities(self, db_connection):
        """Query should handle negative quantities (returns)"""
        sql = """
        SELECT
            SUM(CASE WHEN quantity > 0 THEN revenue ELSE 0 END) AS sales_revenue,
            SUM(CASE WHEN quantity < 0 THEN revenue ELSE 0 END) AS return_revenue
        FROM order_items
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 1

    def test_empty_result_handling(self, db_connection):
        """Query returning no results should not error"""
        sql = """
        SELECT * FROM orders
        WHERE strftime('%Y', invoice_date) = '1900'
        """
        result = execute_query(db_connection, sql)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
