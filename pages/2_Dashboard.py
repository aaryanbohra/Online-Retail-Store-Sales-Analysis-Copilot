"""Dashboard Page - Interactive Analytics Dashboard for Online Retail Data"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from config import DATABASE_PATH

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0d1b2a 100%);
    }
    section[data-testid="stSidebar"] * { color: #e0e7ee !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        font-weight: 500;
        font-size: 0.85rem;
    }

    /* Main area */
    .block-container { padding-top: 1.5rem; max-width: 1400px; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    [data-testid="stMetric"] label { color: rgba(255,255,255,0.85) !important; font-weight: 500; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: white !important; font-weight: 700; }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] { color: rgba(255,255,255,0.9) !important; }

    /* Chart section titles */
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 0.5rem;
        padding-top: 0.5rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background: transparent; }

    /* Tab styling for dark theme */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    /* Dataframe styling for dark theme */
    .stDataFrame {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def load_data():
    """Load and cache the main dataset"""
    conn = sqlite3.connect(DATABASE_PATH)

    query = """
    SELECT
        o.invoice_id,
        o.invoice_date,
        o.country,
        o.customer_id,
        oi.stock_code,
        oi.description,
        oi.quantity,
        oi.unit_price,
        oi.revenue
    FROM orders o
    JOIN order_items oi ON o.invoice_id = oi.invoice_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    df['year'] = df['invoice_date'].dt.year
    df['month'] = df['invoice_date'].dt.to_period('M').astype(str)
    df['month_name'] = df['invoice_date'].dt.strftime('%b %Y')
    df['weekday'] = df['invoice_date'].dt.day_name()
    df['hour'] = df['invoice_date'].dt.hour

    return df


@st.cache_data(ttl=600)
def get_summary_stats(df):
    """Calculate summary statistics"""
    return {
        'total_revenue': df['revenue'].sum(),
        'total_orders': df['invoice_id'].nunique(),
        'total_customers': df['customer_id'].nunique(),
        'total_products': df['stock_code'].nunique(),
        'avg_order_value': df.groupby('invoice_id')['revenue'].sum().mean(),
        'total_countries': df['country'].nunique()
    }


def format_number(num, prefix=""):
    """Format large numbers for display"""
    if num >= 1_000_000:
        return f"{prefix}{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{prefix}{num/1_000:.1f}K"
    else:
        return f"{prefix}{num:.0f}"


def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a styled metric"""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


# Load data
df = load_data()

# ===== SIDEBAR FILTERS =====
with st.sidebar:
    st.markdown("### 📊 Sales Dashboard")
    st.caption("Interactive Analytics")
    st.divider()

    # Year filter
    years = sorted(df['year'].unique())
    selected_years = st.multiselect(
        "Select Years",
        options=years,
        default=[],
        placeholder="All years"
    )

    # Country filter
    countries = sorted(df['country'].unique())
    selected_countries = st.multiselect(
        "Select Countries",
        options=countries,
        default=[],
        placeholder="All countries"
    )

    # Top N filter
    top_n = st.slider("Top N Items", min_value=5, max_value=20, value=10)

    st.divider()

    # Quick stats
    st.markdown("**Quick Stats**")
    st.caption(f"Data: {df['invoice_date'].min().strftime('%b %Y')} - {df['invoice_date'].max().strftime('%b %Y')}")
    st.caption(f"{len(df):,} transactions")

# Apply filters (empty selection means all)
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Calculate stats
stats = get_summary_stats(filtered_df)

# ===== HEADER =====
st.markdown("# 📊 Sales Analytics Dashboard")
st.markdown("Real-time insights from Online Retail II dataset")

# ===== KPI METRICS =====
st.markdown("### Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    create_metric_card("Total Revenue", format_number(stats['total_revenue'], "£"))
with col2:
    create_metric_card("Orders", format_number(stats['total_orders']))
with col3:
    create_metric_card("Customers", format_number(stats['total_customers']))
with col4:
    create_metric_card("Avg Order Value", f"£{stats['avg_order_value']:.2f}")
with col5:
    create_metric_card("Countries", str(stats['total_countries']))

st.markdown("")

# ===== TABS =====
tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Trends", "🌍 Geographic", "📦 Products", "👥 Customers"])

# ----- TAB 1: REVENUE TRENDS -----
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<p class="chart-title">📈 Monthly Revenue Trend</p>', unsafe_allow_html=True)

        monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
        monthly_revenue = monthly_revenue.sort_values('month')

        fig = px.area(
            monthly_revenue,
            x='month',
            y='revenue',
            color_discrete_sequence=['#667eea']
        )
        fig.update_traces(
            line=dict(width=2),
            fillcolor='rgba(102, 126, 234, 0.3)'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="",
            yaxis_title="Revenue (£)",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350,
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=False, tickangle=45, color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-title">📊 Revenue by Year</p>', unsafe_allow_html=True)

        yearly_revenue = filtered_df.groupby('year')['revenue'].sum().reset_index()

        fig = px.bar(
            yearly_revenue,
            x='year',
            y='revenue',
            color_discrete_sequence=['#764ba2']
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="",
            yaxis_title="Revenue (£)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350,
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=False, color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    # Second row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-title">📅 Revenue by Day of Week</p>', unsafe_allow_html=True)

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_revenue = filtered_df.groupby('weekday')['revenue'].sum().reset_index()
        daily_revenue['weekday'] = pd.Categorical(daily_revenue['weekday'], categories=day_order, ordered=True)
        daily_revenue = daily_revenue.sort_values('weekday')

        fig = px.bar(
            daily_revenue,
            x='weekday',
            y='revenue',
            color='revenue',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="",
            yaxis_title="Revenue (£)",
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            font_color='#94a3b8'
        )
        fig.update_xaxes(color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-title">🕐 Revenue by Hour of Day</p>', unsafe_allow_html=True)

        hourly_revenue = filtered_df.groupby('hour')['revenue'].sum().reset_index()

        fig = px.line(
            hourly_revenue,
            x='hour',
            y='revenue',
            markers=True,
            color_discrete_sequence=['#667eea']
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Hour",
            yaxis_title="Revenue (£)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=False, dtick=2, color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

# ----- TAB 2: GEOGRAPHIC -----
with tab2:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<p class="chart-title">🌍 Revenue by Country</p>', unsafe_allow_html=True)

        country_revenue = filtered_df.groupby('country').agg({
            'revenue': 'sum',
            'invoice_id': 'nunique',
            'customer_id': 'nunique'
        }).reset_index()
        country_revenue.columns = ['country', 'revenue', 'orders', 'customers']
        country_revenue = country_revenue.sort_values('revenue', ascending=False).head(top_n)

        fig = px.bar(
            country_revenue,
            y='country',
            x='revenue',
            orientation='h',
            color='revenue',
            color_continuous_scale='Purples',
            hover_data=['orders', 'customers']
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Revenue (£)",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        fig.update_yaxes(color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-title">🥧 Revenue Distribution</p>', unsafe_allow_html=True)

        # Top 5 + Others
        top_countries = country_revenue.head(5).copy()
        others_revenue = country_revenue.iloc[5:]['revenue'].sum() if len(country_revenue) > 5 else 0

        if others_revenue > 0:
            others_row = pd.DataFrame({'country': ['Others'], 'revenue': [others_revenue]})
            pie_data = pd.concat([top_countries[['country', 'revenue']], others_row])
        else:
            pie_data = top_countries[['country', 'revenue']]

        fig = px.pie(
            pie_data,
            values='revenue',
            names='country',
            color_discrete_sequence=px.colors.sequential.Purples_r,
            hole=0.4
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, font=dict(color='#94a3b8')),
            height=400,
            font_color='#94a3b8'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

    # Country comparison table
    st.markdown('<p class="chart-title">📋 Country Performance Summary</p>', unsafe_allow_html=True)

    country_summary = filtered_df.groupby('country').agg({
        'revenue': 'sum',
        'invoice_id': 'nunique',
        'customer_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    country_summary.columns = ['Country', 'Revenue', 'Orders', 'Customers', 'Units Sold']
    country_summary['Avg Order Value'] = country_summary['Revenue'] / country_summary['Orders']
    country_summary = country_summary.sort_values('Revenue', ascending=False).head(top_n)

    # Format for display
    display_df = country_summary.copy()
    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['Avg Order Value'] = display_df['Avg Order Value'].apply(lambda x: f"£{x:.2f}")
    display_df['Units Sold'] = display_df['Units Sold'].apply(lambda x: f"{x:,}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ----- TAB 3: PRODUCTS -----
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-title">🏆 Top Products by Revenue</p>', unsafe_allow_html=True)

        product_revenue = filtered_df.groupby('description')['revenue'].sum().reset_index()
        product_revenue = product_revenue.sort_values('revenue', ascending=False).head(top_n)
        product_revenue['description'] = product_revenue['description'].str[:40]

        fig = px.bar(
            product_revenue,
            y='description',
            x='revenue',
            orientation='h',
            color='revenue',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Revenue (£)",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        fig.update_yaxes(color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-title">📦 Top Products by Quantity</p>', unsafe_allow_html=True)

        product_qty = filtered_df.groupby('description')['quantity'].sum().reset_index()
        product_qty = product_qty.sort_values('quantity', ascending=False).head(top_n)
        product_qty['description'] = product_qty['description'].str[:40]

        fig = px.bar(
            product_qty,
            y='description',
            x='quantity',
            orientation='h',
            color='quantity',
            color_continuous_scale='Greens'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Units Sold",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        fig.update_yaxes(color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    # Product price tier analysis
    st.markdown('<p class="chart-title">💰 Revenue by Price Tier</p>', unsafe_allow_html=True)

    price_df = filtered_df[filtered_df['unit_price'] > 0].copy()
    price_bins = [0, 1, 2, 5, 10, 25, float('inf')]
    price_labels = ['Under £1', '£1-2', '£2-5', '£5-10', '£10-25', '£25+']
    price_df['price_tier'] = pd.cut(price_df['unit_price'], bins=price_bins, labels=price_labels)

    price_summary = price_df.groupby('price_tier', observed=True).agg({
        'revenue': 'sum',
        'stock_code': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    price_summary.columns = ['price_tier', 'revenue', 'products', 'units_sold']

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            price_summary,
            x='price_tier',
            y='revenue',
            color='products',
            color_continuous_scale='Greens',
            hover_data={'units_sold': ':,', 'products': True}
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Price Tier",
            yaxis_title="Revenue (£)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=250,
            font_color='#94a3b8',
            coloraxis_showscale=False
        )
        fig.update_xaxes(showgrid=False, color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = px.pie(
            price_summary,
            values='units_sold',
            names='price_tier',
            color_discrete_sequence=px.colors.sequential.Greens_r,
            hole=0.4
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color='#94a3b8')),
            height=250,
            font_color='#94a3b8',
            title=dict(text="Units Sold by Price Tier", font=dict(size=12, color='#a5b4fc'), x=0.5)
        )
        fig.update_traces(textposition='inside', textinfo='percent', textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

# ----- TAB 4: CUSTOMERS -----
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-title">👥 Top Customers by Revenue</p>', unsafe_allow_html=True)

        customer_revenue = filtered_df.groupby('customer_id').agg({
            'revenue': 'sum',
            'invoice_id': 'nunique'
        }).reset_index()
        customer_revenue.columns = ['customer_id', 'revenue', 'orders']
        customer_revenue = customer_revenue.sort_values('revenue', ascending=False).head(top_n)
        customer_revenue['customer_label'] = 'Customer ' + customer_revenue['customer_id'].astype(str)
        customer_revenue['revenue_formatted'] = customer_revenue['revenue'].apply(lambda x: f"£{x:,.0f}")

        fig = px.bar(
            customer_revenue,
            y='customer_label',
            x='revenue',
            orientation='h',
            color='orders',
            color_continuous_scale='Blues',
            hover_data={'revenue_formatted': True, 'orders': True, 'revenue': False, 'customer_label': False},
            labels={'revenue_formatted': 'Revenue', 'orders': 'Orders'}
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Revenue (£)",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(title="Orders", tickfont=dict(color='#94a3b8'), title_font=dict(color='#94a3b8')),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            font_color='#94a3b8'
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8', type='log', dtick=1)
        fig.update_yaxes(color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-title">🔄 Customer Order Frequency</p>', unsafe_allow_html=True)

        order_frequency = filtered_df.groupby('customer_id')['invoice_id'].nunique().reset_index()
        order_frequency.columns = ['customer_id', 'order_count']

        freq_bins = [0, 1, 2, 5, 10, 20, float('inf')]
        freq_labels = ['1 order', '2 orders', '3-5 orders', '6-10 orders', '11-20 orders', '20+ orders']
        order_frequency['frequency_group'] = pd.cut(order_frequency['order_count'], bins=freq_bins, labels=freq_labels)

        freq_summary = order_frequency['frequency_group'].value_counts().reset_index()
        freq_summary.columns = ['frequency_group', 'count']

        fig = px.pie(
            freq_summary,
            values='count',
            names='frequency_group',
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color='#94a3b8')),
            height=400,
            font_color='#94a3b8'
        )
        fig.update_traces(textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

    # Customer lifetime value segments
    st.markdown('<p class="chart-title">💎 Customer Value Segments</p>', unsafe_allow_html=True)

    clv = filtered_df.groupby('customer_id')['revenue'].sum().reset_index()

    # Create meaningful CLV segments
    clv_bins = [0, 100, 500, 1000, 2500, 5000, float('inf')]
    clv_labels = ['£0-100', '£100-500', '£500-1K', '£1K-2.5K', '£2.5K-5K', '£5K+']
    clv['segment'] = pd.cut(clv['revenue'], bins=clv_bins, labels=clv_labels)

    clv_summary = clv.groupby('segment', observed=True).agg({
        'customer_id': 'count',
        'revenue': 'sum'
    }).reset_index()
    clv_summary.columns = ['segment', 'customers', 'total_revenue']
    clv_summary['avg_revenue'] = clv_summary['total_revenue'] / clv_summary['customers']

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            clv_summary,
            x='segment',
            y='customers',
            color='avg_revenue',
            color_continuous_scale='Purples',
            hover_data={'total_revenue': ':,.0f', 'avg_revenue': ':,.0f'}
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Value Segment",
            yaxis_title="Number of Customers",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=280,
            font_color='#94a3b8',
            coloraxis_showscale=False
        )
        fig.update_xaxes(showgrid=False, color='#94a3b8')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.2)', color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = px.pie(
            clv_summary,
            values='total_revenue',
            names='segment',
            color_discrete_sequence=px.colors.sequential.Purples_r,
            hole=0.4
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color='#94a3b8')),
            height=280,
            font_color='#94a3b8'
        )
        fig.update_traces(textposition='inside', textinfo='percent', textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

    # Customer stats
    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_clv = clv['revenue'].mean()
        st.metric("Average CLV", f"£{avg_clv:,.2f}")
    with col2:
        median_clv = clv['revenue'].median()
        st.metric("Median CLV", f"£{median_clv:,.2f}")
    with col3:
        repeat_rate = (order_frequency['order_count'] > 1).mean() * 100
        st.metric("Repeat Purchase Rate", f"{repeat_rate:.1f}%")
