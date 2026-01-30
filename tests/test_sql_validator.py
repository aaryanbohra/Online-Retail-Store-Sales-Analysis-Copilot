"""Unit tests for SQL Validator"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sql_validator import SQLValidator


class TestSQLValidatorSafety:
    """Tests for SQL safety checks"""

    def test_select_query_allowed(self):
        """Basic SELECT queries should be allowed"""
        sql = "SELECT * FROM orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is True
        assert error == ""

    def test_with_cte_allowed(self):
        """CTE (WITH) queries should be allowed"""
        sql = """WITH monthly AS (
            SELECT strftime('%Y-%m', invoice_date) AS month, SUM(revenue) AS total
            FROM order_items GROUP BY month
        ) SELECT * FROM monthly"""
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is True

    def test_drop_blocked(self):
        """DROP statements should be blocked"""
        sql = "DROP TABLE orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False
        assert "Forbidden" in error or "SELECT" in error  # May fail on "only SELECT" or "forbidden keyword"

    def test_delete_blocked(self):
        """DELETE statements should be blocked"""
        sql = "DELETE FROM orders WHERE 1=1"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False
        assert "Only SELECT queries" in error

    def test_update_blocked(self):
        """UPDATE statements should be blocked"""
        sql = "UPDATE orders SET country = 'USA'"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_insert_blocked(self):
        """INSERT statements should be blocked"""
        sql = "INSERT INTO orders VALUES (1, 2, 3)"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_union_injection_blocked(self):
        """UNION SELECT injection should be blocked"""
        sql = "SELECT * FROM orders UNION SELECT * FROM customers"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False
        assert "dangerous" in error.lower()

    def test_multiple_statements_blocked(self):
        """Multiple statements (stacked queries) should be blocked"""
        sql = "SELECT * FROM orders; DROP TABLE orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False
        # Could be blocked for multiple statements OR for containing DROP
        assert "Multiple" in error or "Forbidden" in error

    def test_trailing_semicolon_allowed(self):
        """Trailing semicolon should be allowed"""
        sql = "SELECT * FROM orders;"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is True

    def test_sql_comments_blocked(self):
        """SQL comments should be blocked (can bypass filters)"""
        sql = "SELECT * FROM orders -- this is a comment"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False
        assert "comment" in error.lower()

    def test_block_comments_blocked(self):
        """Block comments should be blocked"""
        sql = "SELECT * /* comment */ FROM orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_sleep_injection_blocked(self):
        """Time-based injection (SLEEP) should be blocked"""
        sql = "SELECT SLEEP(5) FROM orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_hex_encoding_blocked(self):
        """Hex-encoded values should be blocked"""
        sql = "SELECT * FROM orders WHERE id = 0x1234"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_char_function_blocked(self):
        """CHAR() function should be blocked (used to bypass filters)"""
        sql = "SELECT CHAR(65) FROM orders"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False

    def test_attach_database_blocked(self):
        """ATTACH DATABASE should be blocked"""
        sql = "ATTACH DATABASE 'evil.db' AS evil"
        is_safe, error = SQLValidator.is_safe(sql)
        assert is_safe is False


class TestSQLValidatorLimit:
    """Tests for LIMIT clause handling"""

    def test_adds_limit_to_simple_select(self):
        """Should add LIMIT to simple SELECT"""
        sql = "SELECT * FROM orders"
        result = SQLValidator.add_limit_if_needed(sql)
        assert "LIMIT" in result
        assert "100" in result

    def test_preserves_existing_limit(self):
        """Should not modify query with existing LIMIT"""
        sql = "SELECT * FROM orders LIMIT 10"
        result = SQLValidator.add_limit_if_needed(sql)
        assert result == sql

    def test_no_limit_for_aggregates(self):
        """Should not add LIMIT to aggregate queries"""
        sql = "SELECT COUNT(*) FROM orders"
        result = SQLValidator.add_limit_if_needed(sql)
        assert "LIMIT" not in result

    def test_no_limit_for_group_by(self):
        """Should not add LIMIT to GROUP BY queries"""
        sql = "SELECT country, COUNT(*) FROM orders GROUP BY country"
        result = SQLValidator.add_limit_if_needed(sql)
        assert "LIMIT" not in result

    def test_no_limit_for_sum(self):
        """Should not add LIMIT to SUM queries"""
        sql = "SELECT SUM(revenue) FROM order_items"
        result = SQLValidator.add_limit_if_needed(sql)
        assert "LIMIT" not in result

    def test_no_limit_for_avg(self):
        """Should not add LIMIT to AVG queries"""
        sql = "SELECT AVG(unit_price) FROM order_items"
        result = SQLValidator.add_limit_if_needed(sql)
        assert "LIMIT" not in result


class TestSQLValidatorValidate:
    """Tests for full validation pipeline"""

    def test_valid_query_passes(self):
        """Valid query should pass and return SQL"""
        sql = "SELECT * FROM orders"
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True
        assert "SELECT" in result
        assert "LIMIT" in result

    def test_invalid_query_fails(self):
        """Invalid query should fail with error message"""
        sql = "DROP TABLE orders"
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is False
        assert "Forbidden" in result or "Only SELECT" in result

    def test_aggregate_query_no_limit(self):
        """Aggregate queries should pass without LIMIT"""
        sql = "SELECT SUM(revenue) AS total FROM order_items"
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True
        assert "LIMIT" not in result


class TestComplexQueries:
    """Tests for complex query patterns used by the Copilot"""

    def test_subquery_allowed(self):
        """Subqueries should be allowed"""
        sql = """SELECT * FROM (
            SELECT country, SUM(revenue) as total
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            GROUP BY country
        ) AS subq WHERE total > 1000"""
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True

    def test_window_function_allowed(self):
        """Window functions should be allowed"""
        sql = """SELECT country, total,
            ROW_NUMBER() OVER (ORDER BY total DESC) as rank
        FROM (
            SELECT o.country, SUM(oi.revenue) as total
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            GROUP BY o.country
        )"""
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True

    def test_cross_join_allowed(self):
        """CROSS JOIN should be allowed"""
        sql = """SELECT a.val, b.avg_val FROM
            (SELECT 1 as val) AS a
            CROSS JOIN
            (SELECT 2 as avg_val) AS b"""
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True

    def test_cte_with_window_allowed(self):
        """CTE with window functions should be allowed"""
        sql = """WITH ranked AS (
            SELECT country, revenue,
                ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC) as rn
            FROM orders
        ) SELECT * FROM ranked WHERE rn <= 5"""
        is_valid, result = SQLValidator.validate(sql)
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
