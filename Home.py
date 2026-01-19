import streamlit as st
from utils.theme import (
    init_theme, get_theme_colors,
    get_global_css, get_hero_css, get_card_css,
    get_section_css, get_table_css
)

st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="//",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_theme()
st.markdown(get_global_css(), unsafe_allow_html=True)
st.markdown(get_hero_css(), unsafe_allow_html=True)
st.markdown(get_card_css(), unsafe_allow_html=True)
st.markdown(get_section_css(), unsafe_allow_html=True)
st.markdown(get_table_css(), unsafe_allow_html=True)

c = get_theme_colors()

with st.sidebar:
    st.markdown("### // NAVIGATION")
    st.markdown("")
    st.markdown(f"""
    <p style="color: {c['text_tertiary']}; font-size: 0.85rem; line-height: 1.8;">
    <span style="color: {c['accent_primary']};">01</span> &nbsp;Home<br>
    <span style="color: {c['accent_primary']};">02</span> &nbsp;AI Copilot<br>
    <span style="color: {c['accent_primary']};">03</span> &nbsp;Dashboard<br>
    <span style="color: {c['accent_primary']};">04</span> &nbsp;Dataset
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <p style="color: {c['text_tertiary']}; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">
    SYSTEM STATUS<br>
    <span style="color: {c['success']};">●</span> Database connected<br>
    <span style="color: {c['success']};">●</span> AI model ready
    </p>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">ANALYTICS PLATFORM v2.0</div>
    <h1 class="hero-title">
        Online Retail<br>
        <span class="accent">Sales Analysis</span>
    </h1>
    <p class="hero-subtitle">
        AI-powered business intelligence platform. Query your data with natural language,
        visualize trends, and uncover insights in real-time.
    </p>
    <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stat-grid">
    <div class="stat-card">
        <span class="stat-icon">&#x1F4CA;</span>
        <div class="stat-value">1M+</div>
        <div class="stat-label">Transactions</div>
    </div>
    <div class="stat-card">
        <span class="stat-icon">&#x1F4C5;</span>
        <div class="stat-value">2009-11</div>
        <div class="stat-label">Time Period</div>
    </div>
    <div class="stat-card">
        <span class="stat-icon">&#x1F30D;</span>
        <div class="stat-value">40+</div>
        <div class="stat-label">Countries</div>
    </div>
    <div class="stat-card">
        <span class="stat-icon">&#x1F4E6;</span>
        <div class="stat-value">4,000+</div>
        <div class="stat-label">Products</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

st.markdown(f"""
<div style="margin-bottom: 0.5rem;">
    <span class="section-title">PLATFORM CAPABILITIES</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">&#x26A1;</div>
        <div class="feature-title">AI Query Engine</div>
        <div class="feature-desc">
            Natural language to SQL translation powered by Claude AI.
            Ask questions in plain English and receive instant, accurate database queries.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">&#x1F4C8;</div>
        <div class="feature-title">Intelligent Visualization</div>
        <div class="feature-desc">
            Automatic chart type selection based on your data structure.
            Line charts for trends, bar charts for comparisons, KPIs for metrics.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">&#x1F3AF;</div>
        <div class="feature-title">Interactive Dashboard</div>
        <div class="feature-desc">
            Explore revenue patterns, geographic distribution, product performance,
            and customer analytics with real-time filtering.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">&#x1F4BE;</div>
        <div class="feature-title">Data Export</div>
        <div class="feature-desc">
            Download query results as CSV for further analysis.
            Full query history tracking for reference and auditing.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")
with st.expander("// VIEW DATASET SCHEMA", expanded=False):
    st.markdown(f"""
    <p style="color: {c['text_tertiary']}; font-size: 0.8rem; margin-bottom: 1rem;">
    Source: UCI Machine Learning Repository — Online Retail II Dataset
    </p>
    <div class="data-table-container">
        <table class="data-table">
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
                <td>5-digit product code uniquely assigned to each product.</td>
            </tr>
            <tr>
                <td><code>Description</code></td>
                <td>Product name and description.</td>
            </tr>
            <tr>
                <td><code>Quantity</code></td>
                <td>Quantity per transaction. Negative values indicate returns.</td>
            </tr>
            <tr>
                <td><code>InvoiceDate</code></td>
                <td>Transaction timestamp.</td>
            </tr>
            <tr>
                <td><code>UnitPrice</code></td>
                <td>Price per unit in GBP (£).</td>
            </tr>
            <tr>
                <td><code>CustomerID</code></td>
                <td>5-digit unique customer identifier.</td>
            </tr>
            <tr>
                <td><code>Country</code></td>
                <td>Customer's country of residence.</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown(f"""
<div class="getting-started">
    <h4>QUICK START</h4>
    <ol>
        <li>
            <strong>AI Copilot</strong> — Ask natural language questions:<br>
            <code>What was total revenue in 2011?</code><br>
            <code>Show monthly revenue trend</code><br>
            <code>Top 10 products by revenue</code>
        </li>
        <li style="margin-top: 1rem;">
            <strong>Dashboard</strong> — Explore pre-built analytics with filters for year, country, and more.
        </li>
        <li style="margin-top: 1rem;">
            <strong>Dataset</strong> — Browse and download the raw transaction data.
        </li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
<p class="footer-text">
    Built with Streamlit + Claude AI &nbsp;|&nbsp;
    Data: <a href="https://archive.ics.uci.edu/dataset/502/online+retail+ii">UCI Online Retail II</a>
</p>
""", unsafe_allow_html=True)
