"""Dataset Page - View the original dataset in its original format"""

import streamlit as st
import sqlite3
import pandas as pd
from config import DATABASE_PATH

# Page config
st.set_page_config(page_title="Original Dataset", page_icon="📋", layout="wide")

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

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_dataset_stats():
    """Get statistics for the dataset"""
    conn = sqlite3.connect(DATABASE_PATH)

    stats = {}

    # Total records
    stats['records'] = pd.read_sql_query("SELECT COUNT(*) as count FROM order_items", conn).iloc[0, 0]

    # Date range
    dates = pd.read_sql_query("SELECT MIN(invoice_date) as min_date, MAX(invoice_date) as max_date FROM orders", conn)
    stats['min_date'] = dates.iloc[0, 0][:10]
    stats['max_date'] = dates.iloc[0, 1][:10]

    # Countries
    stats['countries'] = pd.read_sql_query("SELECT COUNT(DISTINCT country) as count FROM orders", conn).iloc[0, 0]

    # Products
    stats['products'] = pd.read_sql_query("SELECT COUNT(DISTINCT stock_code) as count FROM order_items", conn).iloc[0, 0]

    # Customers
    stats['customers'] = pd.read_sql_query("SELECT COUNT(DISTINCT customer_id) as count FROM customers", conn).iloc[0, 0]

    conn.close()
    return stats

@st.cache_data(ttl=600)
def load_original_dataset(limit: int = 100):
    """Load data in original dataset format by joining tables"""
    conn = sqlite3.connect(DATABASE_PATH)

    query = f"""
    SELECT
        o.invoice_id AS InvoiceNo,
        oi.stock_code AS StockCode,
        oi.description AS Description,
        oi.quantity AS Quantity,
        o.invoice_date AS InvoiceDate,
        oi.unit_price AS UnitPrice,
        o.customer_id AS CustomerID,
        o.country AS Country
    FROM order_items oi
    JOIN orders o ON oi.invoice_id = o.invoice_id
    ORDER BY o.invoice_date DESC
    LIMIT {limit}
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Original Dataset")
    st.caption("View the dataset in its original format")
    st.divider()

    st.markdown("**Variables**")
    st.markdown("- `InvoiceNo` - Invoice number")
    st.markdown("- `StockCode` - Product code")
    st.markdown("- `Description` - Product name")
    st.markdown("- `Quantity` - Items ordered")
    st.markdown("- `InvoiceDate` - Transaction date")
    st.markdown("- `UnitPrice` - Price per unit")
    st.markdown("- `CustomerID` - Customer ID")
    st.markdown("- `Country` - Customer country")

    st.divider()
    st.markdown("**Source**")
    st.caption("UCI Machine Learning Repository")
    st.caption("Online Retail II Dataset")

# Header
st.markdown("# 📋 Original Dataset")
st.markdown("View the dataset in its original format as provided by UCI Machine Learning Repository")

# Stats
stats = get_dataset_stats()

st.markdown("### Dataset Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['records']:,}</div>
        <div class="stats-label">Records</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['customers']:,}</div>
        <div class="stats-label">Customers</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['products']:,}</div>
        <div class="stats-label">Products</div>
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
        <div class="stats-number">{stats['min_date'][:4]}–{stats['max_date'][:4]}</div>
        <div class="stats-label">Time Period</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Variable descriptions
st.markdown("### Variable Descriptions")

st.markdown("""
| Variable | Description |
|----------|-------------|
| **InvoiceNo** | 6-digit invoice number. Prefix `C` indicates a cancellation. |
| **StockCode** | 5-digit product/item code uniquely assigned to each product. |
| **Description** | Product name/description. |
| **Quantity** | Quantity of each product per transaction. Negative values indicate returns. |
| **InvoiceDate** | Date and time when the transaction was generated. |
| **UnitPrice** | Product price per unit in GBP. |
| **CustomerID** | 5-digit unique customer identifier. |
| **Country** | Country where the customer resides. |
""")

st.markdown("")

# Data browser
st.markdown("### Browse Dataset")

col1, col2 = st.columns([3, 1])
with col2:
    limit = st.selectbox("Rows to display", [50, 100, 500, 1000, 5000], index=1)

df = load_original_dataset(limit)
st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "online_retail_dataset.csv",
    "text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    '<p style="color: #64748b; font-size: 0.85rem;">'
    'Source: <a href="https://archive.ics.uci.edu/dataset/502/online+retail+ii" style="color: #818cf8;">UCI Machine Learning Repository - Online Retail II</a>'
    '</p>',
    unsafe_allow_html=True
)
