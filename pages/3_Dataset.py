import streamlit as st
import sqlite3
import pandas as pd
from config import DATABASE_PATH
from utils.theme import (
    init_theme, get_theme_colors,
    get_global_css, get_stat_card_css, get_data_table_css
)

st.set_page_config(page_title="Original Dataset", page_icon="//", layout="wide")

init_theme()
st.markdown(get_global_css(), unsafe_allow_html=True)
st.markdown(get_stat_card_css(), unsafe_allow_html=True)
st.markdown(get_data_table_css(), unsafe_allow_html=True)

c = get_theme_colors()

st.markdown(f"""
<style>
    .dataset-header {{
        margin-bottom: 2rem;
    }}

    .dataset-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {c['text_primary']};
        margin-bottom: 0.25rem;
    }}

    .dataset-subtitle {{
        font-size: 0.95rem;
        color: {c['text_tertiary']};
    }}

    .mini-stat-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin: 1.5rem 0 2rem 0;
    }}

    .mini-stat-card {{
        background: {c['card_bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}

    .mini-stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, {c['accent_primary']}, transparent);
    }}

    .mini-stat-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: {c['accent_secondary']};
        line-height: 1;
    }}

    .mini-stat-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: {c['text_tertiary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }}

    .section-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: {c['accent_primary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        padding-left: 0.75rem;
        border-left: 3px solid {c['accent_primary']};
    }}

    .schema-container {{
        background: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0 2rem 0;
    }}

    .schema-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .schema-table th {{
        background: {c['bg_primary']};
        color: {c['accent_primary']};
        padding: 1rem;
        text-align: left;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 2px solid {c['border_hover']};
    }}

    .schema-table td {{
        padding: 0.875rem 1rem;
        color: {c['text_secondary']};
        font-size: 0.9rem;
        border-bottom: 1px solid {c['border']};
    }}

    .schema-table tr:hover td {{
        background: {c['accent_glow']};
    }}

    .schema-table code {{
        background: {c['accent_glow']};
        color: {c['accent_secondary']};
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }}

    .browser-controls {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }}

    .footer-link {{
        color: {c['accent_primary']};
        text-decoration: none;
    }}

    .footer-link:hover {{
        text-decoration: underline;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def get_dataset_stats():
    conn = sqlite3.connect(DATABASE_PATH)

    stats = {}
    stats['records'] = pd.read_sql_query("SELECT COUNT(*) as count FROM order_items", conn).iloc[0, 0]

    dates = pd.read_sql_query("SELECT MIN(invoice_date) as min_date, MAX(invoice_date) as max_date FROM orders", conn)
    stats['min_date'] = dates.iloc[0, 0][:10]
    stats['max_date'] = dates.iloc[0, 1][:10]

    stats['countries'] = pd.read_sql_query("SELECT COUNT(DISTINCT country) as count FROM orders", conn).iloc[0, 0]
    stats['products'] = pd.read_sql_query("SELECT COUNT(DISTINCT stock_code) as count FROM order_items", conn).iloc[0, 0]
    stats['customers'] = pd.read_sql_query("SELECT COUNT(DISTINCT customer_id) as count FROM customers", conn).iloc[0, 0]

    conn.close()
    return stats


@st.cache_data(ttl=600)
def load_original_dataset(limit: int = 100):
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
    st.markdown("### // DATASET")
    st.markdown(f'<p style="color: {c["text_tertiary"]}; font-size: 0.75rem;">Original Format Browser</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### // VARIABLES")
    st.markdown(f"""
    <p style="color: {c['text_tertiary']}; font-size: 0.8rem; line-height: 1.8;">
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">InvoiceNo</code> Invoice number<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">StockCode</code> Product code<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">Description</code> Product name<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">Quantity</code> Items ordered<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">InvoiceDate</code> Transaction date<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">UnitPrice</code> Price per unit<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">CustomerID</code> Customer ID<br>
    <code style="color: {c['accent_secondary']}; background: {c['accent_glow']}; padding: 2px 6px; border-radius: 3px;">Country</code> Customer country
    </p>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### // SOURCE")
    st.markdown(f"""
    <p style="color: {c['text_tertiary']}; font-size: 0.75rem;">
    UCI Machine Learning Repository<br>
    Online Retail II Dataset
    </p>
    """, unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="dataset-header">
    <h1 class="dataset-title"><span style="color: {c['accent_primary']};">📋</span> Original Dataset</h1>
    <p class="dataset-subtitle">View the dataset in its original format as provided by UCI Machine Learning Repository</p>
</div>
""", unsafe_allow_html=True)

# Stats
stats = get_dataset_stats()

st.markdown('<p class="section-title">Dataset Overview</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="mini-stat-grid">
    <div class="mini-stat-card">
        <div class="mini-stat-value">{stats['records']:,}</div>
        <div class="mini-stat-label">Records</div>
    </div>
    <div class="mini-stat-card">
        <div class="mini-stat-value">{stats['customers']:,}</div>
        <div class="mini-stat-label">Customers</div>
    </div>
    <div class="mini-stat-card">
        <div class="mini-stat-value">{stats['products']:,}</div>
        <div class="mini-stat-label">Products</div>
    </div>
    <div class="mini-stat-card">
        <div class="mini-stat-value">{stats['countries']}</div>
        <div class="mini-stat-label">Countries</div>
    </div>
    <div class="mini-stat-card">
        <div class="mini-stat-value">{stats['min_date'][:4]}–{stats['max_date'][:4]}</div>
        <div class="mini-stat-label">Time Period</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Variable descriptions
st.markdown('<p class="section-title">Variable Descriptions</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="schema-container">
    <table class="schema-table">
        <tr>
            <th>Variable</th>
            <th>Description</th>
        </tr>
        <tr>
            <td><code>InvoiceNo</code></td>
            <td>6-digit invoice number. Prefix <code>C</code> indicates a cancellation.</td>
        </tr>
        <tr>
            <td><code>StockCode</code></td>
            <td>5-digit product/item code uniquely assigned to each product.</td>
        </tr>
        <tr>
            <td><code>Description</code></td>
            <td>Product name/description.</td>
        </tr>
        <tr>
            <td><code>Quantity</code></td>
            <td>Quantity of each product per transaction. Negative values indicate returns.</td>
        </tr>
        <tr>
            <td><code>InvoiceDate</code></td>
            <td>Date and time when the transaction was generated.</td>
        </tr>
        <tr>
            <td><code>UnitPrice</code></td>
            <td>Product price per unit in GBP.</td>
        </tr>
        <tr>
            <td><code>CustomerID</code></td>
            <td>5-digit unique customer identifier.</td>
        </tr>
        <tr>
            <td><code>Country</code></td>
            <td>Country where the customer resides.</td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

# Data browser
st.markdown('<p class="section-title">Browse Dataset</p>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col2:
    limit = st.selectbox("Rows to display", [50, 100, 500, 1000, 5000], index=1, label_visibility="collapsed")

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
st.markdown(f"""
<p style="color: {c['text_tertiary']}; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace;">
    Source: <a href="https://archive.ics.uci.edu/dataset/502/online+retail+ii" class="footer-link">UCI Machine Learning Repository — Online Retail II</a>
</p>
""", unsafe_allow_html=True)
