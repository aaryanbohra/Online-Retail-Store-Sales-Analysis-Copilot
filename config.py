"""Configuration settings for the analytics copilot"""

import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit Cloud or local .env"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # Fall back to environment variable (for local development)
    return os.getenv(key, default)

ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")
MODEL = get_secret("MODEL", "claude-3-haiku-20240307")

MAX_TOKENS = 4000

# Database settings
DATABASE_PATH = "analytics.db"

# SQL Safety settings
FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "ALTER", 
    "INSERT", "TRUNCATE", "CREATE", "REPLACE"
]

# Query limits
DEFAULT_LIMIT = 100
MAX_ROWS_FOR_CHART = 50

# Schema definition
SCHEMA = """
TABLE customers (
  customer_id TEXT PRIMARY KEY,
  country TEXT
)

TABLE orders (
  invoice_id TEXT PRIMARY KEY,
  invoice_date TIMESTAMP,
  customer_id TEXT,
  country TEXT
  -- NOTE: This table has NO revenue, quantity, or product data
)

TABLE order_items (
  order_item_id INTEGER PRIMARY KEY,
  invoice_id TEXT,  -- Foreign key to orders.invoice_id
  stock_code TEXT,
  description TEXT,
  quantity INTEGER,
  unit_price REAL,
  revenue REAL
  -- NOTE: This table has ALL revenue and product data
)

Key relationships:
- order_items.invoice_id → orders.invoice_id (JOIN on this)
- orders.customer_id → customers.customer_id (JOIN on this)

CRITICAL column locations:
- revenue, quantity, unit_price, stock_code, description → order_items table ONLY
- invoice_date → orders table ONLY
- customer_id → both customers and orders tables
- country → both customers and orders tables
"""

# System Prompts
SQL_SYSTEM_PROMPT = """You are an expert SQL assistant.
Your task is to generate a valid SQLite query to answer the user's question.
Use the following schema:
{schema}

Rules:
1. Return ONLY the SQL query. No markdown, no explanations, no comments.
2. Use SQLite syntax only. SQLite supports window functions like ROW_NUMBER(), RANK(), and DENSE_RANK().
3. Do not use forbidden keywords.
4. If the question cannot be answered with the given schema, return SELECT 'Error: Cannot answer question with available data';
5. For product-related questions, prefer using the product name (description) as the label in the SELECT output rather than stock codes. When aggregating by product, group by description unless the question explicitly requests stock codes.
6. For queries requiring "top N per group", use window functions with a subquery. Prefer subqueries over CTEs for simplicity.
7. Always use strftime() for date formatting and filtering in SQLite.
8. Ensure the query is complete and valid - check for proper syntax including all parentheses and keywords.
9. CRITICAL: Always reference revenue from order_items table (e.g., order_items.revenue or oi.revenue). Never use orders.revenue as it does not exist.
10. CRITICAL: Always reference invoice_date from orders table (e.g., orders.invoice_date or o.invoice_date). Never use order_items.invoice_date as it does not exist.
11. CRITICAL for time granularity:
    - "trend over/during/in [month]" or "daily trend in [month]" = GROUP BY day (strftime('%Y-%m-%d')) to show daily data within that month
    - "monthly trend" or "trend by month" = GROUP BY month (strftime('%Y-%m')) to show month-by-month data
    - "trend over/during/in [year]" = GROUP BY month to show monthly data within that year
    - Always match the granularity to what makes sense for visualization (multiple data points for trends)

Common query patterns:

- Daily revenue trend within a specific month (e.g., January 2011):
  SELECT strftime('%Y-%m-%d', o.invoice_date) AS date, SUM(oi.revenue) AS daily_revenue
  FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
  WHERE strftime('%Y-%m', o.invoice_date) = '2011-01'
  GROUP BY date ORDER BY date

- Revenue by date:
  SELECT ... FROM order_items oi JOIN orders o ON oi.invoice_id = o.invoice_id
  WHERE strftime('%Y', o.invoice_date) = 'YYYY'

- Revenue by country:
  SELECT o.country, SUM(oi.revenue) FROM order_items oi
  JOIN orders o ON oi.invoice_id = o.invoice_id GROUP BY o.country

- Top N per group (e.g., highest month per year):
  SELECT year, month, revenue FROM (
    SELECT year, month, revenue, ROW_NUMBER() OVER (PARTITION BY year ORDER BY revenue DESC) as rn
    FROM (
      SELECT strftime('%Y', o.invoice_date) AS year,
             strftime('%Y-%m', o.invoice_date) AS month,
             SUM(oi.revenue) AS revenue
      FROM order_items oi
      JOIN orders o ON oi.invoice_id = o.invoice_id
      GROUP BY year, month
    )
  ) WHERE rn = 1

- Average monthly revenue per year:
  SELECT year, AVG(monthly_revenue) as avg_monthly_revenue FROM (
    SELECT strftime('%Y', o.invoice_date) AS year,
           strftime('%Y-%m', o.invoice_date) AS month,
           SUM(oi.revenue) AS monthly_revenue
    FROM order_items oi
    JOIN orders o ON oi.invoice_id = o.invoice_id
    GROUP BY year, month
  ) GROUP BY year

IMPORTANT RULES FOR SUBQUERIES:
- Window functions (ROW_NUMBER, RANK, etc.) must be inside a subquery. Never use WINDOW keyword standalone.
- In outer queries, only reference columns that exist in the subquery's SELECT clause (the aliased columns).
- Table aliases (like o, oi) are NOT available outside their subquery - use the column aliases instead.
"""

INSIGHT_SYSTEM_PROMPT = """You are a business data analyst providing brief insights.

Rules:
1. Keep your response to 2-4 sentences maximum
2. Focus on the key finding or trend
3. Use plain numbers (e.g., "1.1M" or "1,132,408") - never use $ symbols or currency formatting
4. Be specific - mention actual values from the data
5. If there's a clear trend or outlier, highlight it
6. No bullet points, no headers, no markdown formatting
"""
