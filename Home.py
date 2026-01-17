"""
Analytics Copilot - Home Page
Multi-page Streamlit application for sales analytics
"""

import streamlit as st

st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Main content styling */
    .main-header {
        font-size: 5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818cf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.25rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    .feature-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(129, 140, 248, 0.3);
    }

    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #818cf8;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #cbd5e1;
        font-size: 0.95rem;
    }

    .stat-box {
        background: rgba(30, 27, 75, 0.5);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(129, 140, 248, 0.2);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #818cf8;
    }

    .stat-label {
        color: #94a3b8;
        font-size: 0.85rem;
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }

    .data-table th {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        color: #a5b4fc;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #4f46e5;
    }

    .data-table td {
        padding: 0.6rem 1rem;
        border-bottom: 1px solid rgba(129, 140, 248, 0.15);
        color: #cbd5e1;
    }

    .data-table tr:hover {
        background: rgba(129, 140, 248, 0.08);
    }

    .data-table code {
        background: rgba(129, 140, 248, 0.2);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #a5b4fc;
    }

    .source-note {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.5rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    st.markdown("Use the sidebar to navigate between pages:")
    st.markdown("- **Home**: Overview and getting started")
    st.markdown("- **Copilot**: Ask questions in natural language")
    st.markdown("- **Dashboard**: Interactive visual analytics")

# Main content
st.markdown("""
<h1 style="font-size: 3.5rem; font-weight: 700; background: linear-gradient(90deg, #818cf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">
    Online Retail Store Sales Analysis
</h1>
""", unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered business intelligence for your sales data</p>', unsafe_allow_html=True)

# Dataset overview
st.markdown("---")
st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">1M+</div>
        <div class="stat-label">Transactions</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">2009-2011</div>
        <div class="stat-label">Time Period</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">40+</div>
        <div class="stat-label">Countries</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">4,000+</div>
        <div class="stat-label">Products</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Original Dataset Schema
with st.expander("📋 Original Dataset Variables", expanded=False):
    st.markdown("""
    <p class="source-note">Source: UCI Machine Learning Repository - Online Retail II Dataset</p>
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
            <td>Product price per unit in GBP (£).</td>
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
    """, unsafe_allow_html=True)

# Feature cards
st.subheader("Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🤖 AI Copilot</div>
        <div class="feature-desc">
            Ask questions in natural language and get instant SQL queries,
            visualizations, and AI-generated insights. No SQL knowledge required.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📈 Smart Visualizations</div>
        <div class="feature-desc">
            Automatic chart selection based on your data - line charts for trends,
            bar charts for comparisons, and KPI cards for single metrics.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Interactive Dashboard</div>
        <div class="feature-desc">
            Explore revenue trends, geographic distribution, product performance,
            and customer analytics with interactive filters and drill-downs.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💾 Export & Share</div>
        <div class="feature-desc">
            Download query results as CSV files for further analysis in Excel
            or other tools. Track your query history for reference.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Getting started
st.markdown("---")
st.subheader("Getting Started")

st.markdown("""
**1. Try the AI Copilot** - Navigate to the Copilot page and ask questions like:
- "What was total revenue in 2011?"
- "Show monthly revenue trend"
- "Top 10 products by revenue"
- "Which country has the highest sales?"

**2. Explore the Dashboard** - Use the Dashboard page for pre-built analytics:
- Filter by year and country
- View revenue trends over time
- Analyze geographic distribution
- Discover top products and customers
""")

# Footer
st.markdown("---")
st.markdown(
    '<p style="color: #64748b; font-size: 0.85rem;">Built with Streamlit and Claude AI | '
    'Data: UCI Online Retail II Dataset</p>',
    unsafe_allow_html=True
)
