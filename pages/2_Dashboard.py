import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from config import DATABASE_PATH
from utils.theme import (
    init_theme, get_theme_colors,
    get_global_css, get_chart_title_css, get_plotly_theme, apply_plotly_theme
)

init_theme()
st.markdown(get_global_css(), unsafe_allow_html=True)
st.markdown(get_chart_title_css(), unsafe_allow_html=True)

c = get_theme_colors()
PLOTLY_THEME = get_plotly_theme()

st.markdown(f"""
<style>
    .filter-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: {c['text_tertiary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.25rem;
    }}

    .sidebar-stat {{
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid {c['border']};
    }}

    .sidebar-stat-label {{
        font-size: 0.8rem;
        color: {c['text_tertiary']};
    }}

    .sidebar-stat-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: {c['accent_primary']};
    }}

    .dashboard-header {{
        margin-bottom: 2rem;
    }}

    .dashboard-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {c['text_primary']};
        margin-bottom: 0.25rem;
    }}

    .dashboard-subtitle {{
        font-size: 0.95rem;
        color: {c['text_tertiary']};
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def load_data():
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
    return {
        'total_revenue': df['revenue'].sum(),
        'total_orders': df['invoice_id'].nunique(),
        'total_customers': df['customer_id'].nunique(),
        'total_products': df['stock_code'].nunique(),
        'avg_order_value': df.groupby('invoice_id')['revenue'].sum().mean(),
        'total_countries': df['country'].nunique()
    }


def format_number(num, prefix=""):
    if num >= 1_000_000:
        return f"{prefix}{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{prefix}{num/1_000:.1f}K"
    else:
        return f"{prefix}{num:.0f}"


def create_chart(fig, height=350):
    apply_plotly_theme(fig, height)
    return fig


df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown("### // DASHBOARD")
    st.markdown(f'<p style="color: {c["text_tertiary"]}; font-size: 0.75rem;">Interactive Analytics</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown(f'<p class="filter-label">Filter by Year</p>', unsafe_allow_html=True)
    years = sorted(df['year'].unique())
    selected_years = st.multiselect(
        "Years",
        options=years,
        default=[],
        placeholder="All years",
        label_visibility="collapsed"
    )

    st.markdown(f'<p class="filter-label">Filter by Country</p>', unsafe_allow_html=True)
    countries = sorted(df['country'].unique())
    selected_countries = st.multiselect(
        "Countries",
        options=countries,
        default=[],
        placeholder="All countries",
        label_visibility="collapsed"
    )

    st.markdown(f'<p class="filter-label">Top N Items</p>', unsafe_allow_html=True)
    top_n = st.slider("Top N", min_value=5, max_value=20, value=10, label_visibility="collapsed")

    st.divider()

    st.markdown("### // DATA RANGE")
    st.markdown(f"""
    <div class="sidebar-stat">
        <span class="sidebar-stat-label">From</span>
        <span class="sidebar-stat-value">{df['invoice_date'].min().strftime('%b %Y')}</span>
    </div>
    <div class="sidebar-stat">
        <span class="sidebar-stat-label">To</span>
        <span class="sidebar-stat-value">{df['invoice_date'].max().strftime('%b %Y')}</span>
    </div>
    <div class="sidebar-stat">
        <span class="sidebar-stat-label">Records</span>
        <span class="sidebar-stat-value">{len(df):,}</span>
    </div>
    """, unsafe_allow_html=True)

# Apply filters
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

stats = get_summary_stats(filtered_df)

# Header
st.markdown(f"""
<div class="dashboard-header">
    <h1 class="dashboard-title"><span style="color: {c['accent_primary']};">📊</span> Sales Dashboard</h1>
    <p class="dashboard-subtitle">Real-time insights from Online Retail II dataset</p>
</div>
""", unsafe_allow_html=True)

# KPI metrics
st.markdown('<p class="chart-section-title">Key Metrics</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Revenue", format_number(stats['total_revenue'], "£"))
with col2:
    st.metric("Orders", format_number(stats['total_orders']))
with col3:
    st.metric("Customers", format_number(stats['total_customers']))
with col4:
    st.metric("Avg Order Value", f"£{stats['avg_order_value']:.2f}")
with col5:
    st.metric("Countries", str(stats['total_countries']))

st.markdown("")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Revenue Trends", "Geographic", "Products", "Customers"])

# Tab 1: Revenue Trends
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<p class="chart-section-title">Monthly Revenue Trend</p>', unsafe_allow_html=True)

        monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
        monthly_revenue = monthly_revenue.sort_values('month')

        fig = px.area(
            monthly_revenue,
            x='month',
            y='revenue',
            color_discrete_sequence=[PLOTLY_THEME['primary_color']]
        )
        fig.update_traces(line=dict(width=2), fillcolor=c['accent_glow'])
        create_chart(fig)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-section-title">Revenue by Year</p>', unsafe_allow_html=True)

        yearly_revenue = filtered_df.groupby('year')['revenue'].sum().reset_index()

        fig = px.bar(
            yearly_revenue,
            x='year',
            y='revenue',
            color_discrete_sequence=[PLOTLY_THEME['secondary_color']]
        )
        create_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-section-title">Revenue by Day of Week</p>', unsafe_allow_html=True)

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_revenue = filtered_df.groupby('weekday')['revenue'].sum().reset_index()
        daily_revenue['weekday'] = pd.Categorical(daily_revenue['weekday'], categories=day_order, ordered=True)
        daily_revenue = daily_revenue.sort_values('weekday')

        fig = px.bar(
            daily_revenue,
            x='weekday',
            y='revenue',
            color='revenue',
            color_continuous_scale=PLOTLY_THEME['color_scale']
        )
        create_chart(fig, height=300)
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-section-title">Revenue by Hour of Day</p>', unsafe_allow_html=True)

        hourly_revenue = filtered_df.groupby('hour')['revenue'].sum().reset_index()

        fig = px.line(
            hourly_revenue,
            x='hour',
            y='revenue',
            markers=True,
            color_discrete_sequence=[PLOTLY_THEME['primary_color']]
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        create_chart(fig, height=300)
        fig.update_xaxes(dtick=2)
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Geographic
with tab2:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<p class="chart-section-title">Revenue by Country</p>', unsafe_allow_html=True)

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
            color_continuous_scale=PLOTLY_THEME['color_scale'],
            hover_data=['orders', 'customers']
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig.update_xaxes(showgrid=True, gridcolor=PLOTLY_THEME['grid_color'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-section-title">Revenue Distribution</p>', unsafe_allow_html=True)

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
            color_discrete_sequence=PLOTLY_THEME['color_sequence'],
            hole=0.4
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, font=dict(color=c['text_secondary']))
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_color='#0f172a')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="chart-section-title">Country Performance Summary</p>', unsafe_allow_html=True)

    country_summary = filtered_df.groupby('country').agg({
        'revenue': 'sum',
        'invoice_id': 'nunique',
        'customer_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    country_summary.columns = ['Country', 'Revenue', 'Orders', 'Customers', 'Units Sold']
    country_summary['Avg Order Value'] = country_summary['Revenue'] / country_summary['Orders']
    country_summary = country_summary.sort_values('Revenue', ascending=False).head(top_n)

    display_df = country_summary.copy()
    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['Avg Order Value'] = display_df['Avg Order Value'].apply(lambda x: f"£{x:.2f}")
    display_df['Units Sold'] = display_df['Units Sold'].apply(lambda x: f"{x:,}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# Tab 3: Products
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-section-title">Top Products by Revenue</p>', unsafe_allow_html=True)

        product_revenue = filtered_df.groupby('description')['revenue'].sum().reset_index()
        product_revenue = product_revenue.sort_values('revenue', ascending=False).head(top_n)
        product_revenue['description'] = product_revenue['description'].str[:40]

        fig = px.bar(
            product_revenue,
            y='description',
            x='revenue',
            orientation='h',
            color='revenue',
            color_continuous_scale=PLOTLY_THEME['color_scale']
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig.update_xaxes(showgrid=True, gridcolor=PLOTLY_THEME['grid_color'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-section-title">Top Products by Quantity</p>', unsafe_allow_html=True)

        product_qty = filtered_df.groupby('description')['quantity'].sum().reset_index()
        product_qty = product_qty.sort_values('quantity', ascending=False).head(top_n)
        product_qty['description'] = product_qty['description'].str[:40]

        fig = px.bar(
            product_qty,
            y='description',
            x='quantity',
            orientation='h',
            color='quantity',
            color_continuous_scale=[[0, '#064e3b'], [0.5, '#059669'], [1, '#34d399']]
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig.update_xaxes(showgrid=True, gridcolor=PLOTLY_THEME['grid_color'])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="chart-section-title">Revenue by Price Tier</p>', unsafe_allow_html=True)

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
            color_continuous_scale=[[0, '#064e3b'], [0.5, '#059669'], [1, '#34d399']],
            hover_data={'units_sold': ':,', 'products': True}
        )
        create_chart(fig, height=250)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<p class="chart-section-title">Units Sold by Price Tier</p>', unsafe_allow_html=True)
        fig = px.pie(
            price_summary,
            values='units_sold',
            names='price_tier',
            color_discrete_sequence=['#064e3b', '#047857', '#059669', '#10b981', '#34d399', '#6ee7b7'],
            hole=0.4
        )
        create_chart(fig, height=250)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color=c['text_secondary']))
        )
        fig.update_traces(textposition='inside', textinfo='percent', textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

# Tab 4: Customers
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="chart-section-title">Top Customers by Revenue</p>', unsafe_allow_html=True)

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
            color_continuous_scale=[[0, '#1e3a8a'], [0.5, '#3b82f6'], [1, '#93c5fd']],
            hover_data={'revenue_formatted': True, 'orders': True, 'revenue': False, 'customer_label': False},
            labels={'revenue_formatted': 'Revenue', 'orders': 'Orders'}
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(title="Orders", tickfont=dict(color=c['text_secondary']), title_font=dict(color=c['text_secondary'])),
            yaxis={'categoryorder': 'total ascending'}
        )
        fig.update_xaxes(showgrid=True, gridcolor=PLOTLY_THEME['grid_color'], type='log', dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="chart-section-title">Customer Order Frequency</p>', unsafe_allow_html=True)

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
            color_discrete_sequence=['#1e3a8a', '#1d4ed8', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'],
            hole=0.4
        )
        create_chart(fig, height=400)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color=c['text_secondary']))
        )
        fig.update_traces(textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="chart-section-title">Customer Value Segments</p>', unsafe_allow_html=True)

    clv = filtered_df.groupby('customer_id')['revenue'].sum().reset_index()

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
            color_continuous_scale=PLOTLY_THEME['color_scale'],
            hover_data={'total_revenue': ':,.0f', 'avg_revenue': ':,.0f'}
        )
        create_chart(fig, height=280)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = px.pie(
            clv_summary,
            values='total_revenue',
            names='segment',
            color_discrete_sequence=PLOTLY_THEME['color_sequence'],
            hole=0.4
        )
        create_chart(fig, height=280)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color=c['text_secondary']))
        )
        fig.update_traces(textposition='inside', textinfo='percent', textfont_color='#0f172a')
        st.plotly_chart(fig, use_container_width=True)

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
