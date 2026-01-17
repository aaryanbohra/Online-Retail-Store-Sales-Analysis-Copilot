"""Dataset Page - View and explore the original dataset"""

import streamlit as st
import sqlite3
import pandas as pd
from config import DATABASE_PATH

# Page config
st.set_page_config(page_title="Dataset Explorer", page_icon="📋", layout="wide")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* Main area */
    .block-container { padding-top: 1.5rem; max-width: 1400px; }

    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid rgba(129, 140, 248, 0.3);
    }

    .stats-number {
        font-size: 1.75rem;
        font-weight: 700;
        color: #818cf8;
    }

    .stats-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* Table section */
    .table-title {
        font-size: 1rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 0.5rem;
        padding-top: 0.5rem;
    }

    /* Schema card */
    .schema-card {
        background: rgba(30, 27, 75, 0.5);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid rgba(129, 140, 248, 0.2);
        margin-bottom: 0.5rem;
    }

    .schema-table {
        color: #818cf8;
        font-weight: 600;
        font-size: 1.1rem;
    }

    .schema-cols {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_table_stats():
    """Get statistics for each table"""
    conn = sqlite3.connect(DATABASE_PATH)

    stats = {}

    # Customers
    stats['customers'] = pd.read_sql_query("SELECT COUNT(*) as count FROM customers", conn).iloc[0, 0]

    # Orders
    stats['orders'] = pd.read_sql_query("SELECT COUNT(*) as count FROM orders", conn).iloc[0, 0]

    # Order items
    stats['order_items'] = pd.read_sql_query("SELECT COUNT(*) as count FROM order_items", conn).iloc[0, 0]

    # Date range
    dates = pd.read_sql_query("SELECT MIN(invoice_date) as min_date, MAX(invoice_date) as max_date FROM orders", conn)
    stats['min_date'] = dates.iloc[0, 0][:10]
    stats['max_date'] = dates.iloc[0, 1][:10]

    # Countries
    stats['countries'] = pd.read_sql_query("SELECT COUNT(DISTINCT country) as count FROM orders", conn).iloc[0, 0]

    # Products
    stats['products'] = pd.read_sql_query("SELECT COUNT(DISTINCT stock_code) as count FROM order_items", conn).iloc[0, 0]

    conn.close()
    return stats

@st.cache_data(ttl=600)
def load_sample_data(table: str, limit: int = 100):
    """Load sample data from a table"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {limit}", conn)
    conn.close()
    return df

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Dataset Explorer")
    st.caption("Browse the database tables")
    st.divider()

    st.markdown("**Tables**")
    st.markdown("- `customers` - Customer info")
    st.markdown("- `orders` - Order headers")
    st.markdown("- `order_items` - Order line items")

    st.divider()
    st.markdown("**Original Source**")
    st.caption("UCI Machine Learning Repository")
    st.caption("Online Retail II Dataset")

# Header
st.markdown("# 📋 Dataset Explorer")
st.markdown("Browse and explore the underlying database tables")

# Stats
stats = get_table_stats()

st.markdown("### Database Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['customers']:,}</div>
        <div class="stats-label">Customers</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['orders']:,}</div>
        <div class="stats-label">Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['order_items']:,}</div>
        <div class="stats-label">Order Items</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['countries']}</div>
        <div class="stats-label">Countries</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['products']:,}</div>
        <div class="stats-label">Products</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Schema overview
st.markdown("### Database Schema")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="schema-card">
        <div class="schema-table">customers</div>
        <div class="schema-cols">
            • customer_id (PK)<br>
            • country
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="schema-card">
        <div class="schema-table">orders</div>
        <div class="schema-cols">
            • invoice_id (PK)<br>
            • invoice_date<br>
            • customer_id (FK)<br>
            • country
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="schema-card">
        <div class="schema-table">order_items</div>
        <div class="schema-cols">
            • order_item_id (PK)<br>
            • invoice_id (FK)<br>
            • stock_code, description<br>
            • quantity, unit_price, revenue
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Table browser
st.markdown("### Browse Tables")

tab1, tab2, tab3 = st.tabs(["👥 Customers", "🧾 Orders", "📦 Order Items"])

with tab1:
    st.markdown('<p class="table-title">Customers Table</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        limit1 = st.selectbox("Rows", [50, 100, 500, 1000], index=1, key="cust_limit")

    df_customers = load_sample_data("customers", limit1)
    st.dataframe(df_customers, use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        df_customers.to_csv(index=False),
        "customers.csv",
        "text/csv"
    )

with tab2:
    st.markdown('<p class="table-title">Orders Table</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        limit2 = st.selectbox("Rows", [50, 100, 500, 1000], index=1, key="orders_limit")

    df_orders = load_sample_data("orders", limit2)
    st.dataframe(df_orders, use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        df_orders.to_csv(index=False),
        "orders.csv",
        "text/csv"
    )

with tab3:
    st.markdown('<p class="table-title">Order Items Table</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        limit3 = st.selectbox("Rows", [50, 100, 500, 1000], index=1, key="items_limit")

    df_items = load_sample_data("order_items", limit3)
    st.dataframe(df_items, use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        df_items.to_csv(index=False),
        "order_items.csv",
        "text/csv"
    )

# Original variables reference
st.markdown("---")
with st.expander("📖 Original Dataset Variables Reference"):
    st.markdown("""
    | Variable | Description |
    |----------|-------------|
    | **InvoiceNo** | 6-digit invoice number. Prefix `C` indicates a cancellation. |
    | **StockCode** | 5-digit product/item code uniquely assigned to each product. |
    | **Description** | Product name/description. |
    | **Quantity** | Quantity of each product per transaction. Negative = returns. |
    | **InvoiceDate** | Date and time when the transaction was generated. |
    | **UnitPrice** | Product price per unit in GBP (£). |
    | **CustomerID** | 5-digit unique customer identifier. |
    | **Country** | Country where the customer resides. |

    *Source: [UCI Machine Learning Repository - Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)*
    """)
