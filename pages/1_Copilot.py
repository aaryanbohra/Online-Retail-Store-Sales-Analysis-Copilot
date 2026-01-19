import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import html
import logging
from utils.llm_client import LLMClient
from utils.sql_validator import SQLValidator
from utils.chart_selector import ChartSelector
from utils.theme import (
    init_theme, get_theme_colors,
    get_global_css, get_card_css, get_section_css,
    get_plotly_theme, apply_plotly_theme
)
from config import DATABASE_PATH, MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 500

init_theme()
st.markdown(get_global_css(), unsafe_allow_html=True)
st.markdown(get_card_css(), unsafe_allow_html=True)
st.markdown(get_section_css(), unsafe_allow_html=True)

c = get_theme_colors()
PLOTLY_THEME = get_plotly_theme()

st.markdown(f"""
<style>
    .query-container {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    .query-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {c['accent_primary']}, {c['accent_secondary']}, {c['accent_tertiary']});
    }}

    .query-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: {c['accent_primary']};
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .query-label::before {{
        content: '';
        width: 6px;
        height: 6px;
        background: {c['accent_primary']};
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }}

    .results-header {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    .results-badge {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: {c['success']};
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}

    .results-badge::before {{
        content: '';
        width: 6px;
        height: 6px;
        background: {c['success']};
        border-radius: 50%;
    }}

    .viz-container {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .viz-container:hover {{
        border-color: {c['border_hover']};
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }}

    .insight-container {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-left: 3px solid {c['accent_primary']};
        border-radius: 0 20px 20px 0;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }}

    .insight-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at top left, {c['accent_glow']} 0%, transparent 50%);
        pointer-events: none;
    }}

    .insight-text {{
        color: {c['text_secondary']};
        font-size: 0.95rem;
        line-height: 1.8;
        position: relative;
        z-index: 1;
    }}

    .empty-state {{
        text-align: center;
        padding: 5rem 2rem;
        animation: fadeIn 0.8s ease forwards;
    }}

    .empty-state-icon {{
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.3;
        animation: pulse 3s ease-in-out infinite;
    }}

    .empty-state-title {{
        font-family: 'Sora', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: {c['text_tertiary']};
        margin-bottom: 0.75rem;
    }}

    .empty-state-text {{
        font-size: 1rem;
        color: {c['text_muted']};
    }}

    .history-item {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: {c['text_secondary']};
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }}

    .history-item:hover {{
        border-color: {c['border_hover']};
        transform: translateX(4px);
    }}

    .history-rows {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: {c['text_muted']};
    }}

    .page-header {{
        margin-bottom: 2.5rem;
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    .page-title {{
        font-family: 'Sora', sans-serif;
        font-size: 2.75rem;
        font-weight: 700;
        color: {c['text_primary']};
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }}

    .page-title-icon {{
        font-size: 2.25rem;
        background: linear-gradient(135deg, {c['accent_primary']}, {c['accent_secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .page-subtitle {{
        color: {c['text_tertiary']};
        font-size: 1.05rem;
        font-weight: 400;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
</style>
""", unsafe_allow_html=True)

if 'llm_client' not in st.session_state:
    try:
        st.session_state.llm_client = LLMClient()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Add your ANTHROPIC_API_KEY to .env file")
        st.stop()

if 'query_history' not in st.session_state:
    st.session_state.query_history = []


def execute_sql(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"SQL execution error: {str(e)}")
        return None
    finally:
        conn.close()


def enrich_product_labels(df: pd.DataFrame) -> pd.DataFrame:
    cols_lower = [c.lower() for c in df.columns]

    if 'stock_code' in cols_lower and 'description' in cols_lower:
        desc_col = df.columns[cols_lower.index('description')]
        new_cols = [desc_col] + [col for col in df.columns if col != desc_col]
        return df[new_cols]

    if 'stock_code' in cols_lower and 'description' not in cols_lower:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            sc_col = df.columns[cols_lower.index('stock_code')]
            codes = df[sc_col].astype(str).unique().tolist()
            if not codes:
                conn.close()
                return df

            placeholders = ','.join(['?'] * len(codes))
            q = f"""
                SELECT stock_code, description, COUNT(*) AS cnt
                FROM order_items
                WHERE stock_code IN ({placeholders})
                GROUP BY stock_code, description
            """
            m = pd.read_sql_query(q, conn, params=codes)
            mode = m.sort_values(['stock_code', 'cnt'], ascending=[True, False]) \
                    .drop_duplicates('stock_code')[['stock_code', 'description']]
            conn.close()

            merged = df.merge(mode.rename(columns={'description': 'product'}), left_on=sc_col, right_on='stock_code', how='left')
            if 'stock_code' in merged.columns and sc_col != 'stock_code':
                merged = merged.drop(columns=['stock_code'])
            if 'product' in merged.columns:
                new_cols = ['product'] + [col for col in merged.columns if col != 'product']
                merged = merged[new_cols].rename(columns={'product': 'description'})
            return merged
        except Exception as e:
            logger.warning(f"Failed to enrich product labels: {e}")
            return df

    return df


def format_cell_value(value, is_numeric=False):
    """Format cell values for display."""
    if pd.isna(value):
        return '<span class="null-value">—</span>'
    if isinstance(value, float):
        if abs(value) >= 1000000:
            return f'{value/1000000:,.2f}M'
        elif abs(value) >= 1000:
            return f'{value:,.2f}'
        else:
            return f'{value:.2f}'
    if isinstance(value, int):
        return f'{value:,}'
    return html.escape(str(value))


def render_styled_table(df: pd.DataFrame, max_rows: int = 15):
    """Render a beautifully styled HTML table."""
    display_df = df.head(max_rows)

    # Determine which columns are numeric
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    table_html = f'''
    <style>
        .styled-table-container {{
            background: {c['card_bg']};
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid {c['border']};
            margin: 0.5rem 0;
        }}
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'Sora', sans-serif;
        }}
        .styled-table thead {{
            background: linear-gradient(180deg, {c['bg_tertiary']} 0%, {c['bg_secondary']} 100%);
            position: sticky;
            top: 0;
        }}
        .styled-table th {{
            color: {c['accent_primary']};
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 1rem 1.25rem;
            text-align: left;
            border-bottom: 2px solid {c['accent_tertiary']};
            white-space: nowrap;
        }}
        .styled-table th.numeric {{
            text-align: right;
        }}
        .styled-table td {{
            padding: 0.875rem 1.25rem;
            color: {c['text_secondary']};
            font-size: 0.9rem;
            border-bottom: 1px solid {c['border_subtle']};
            transition: all 0.15s ease;
        }}
        .styled-table td.numeric {{
            text-align: right;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            color: {c['text_primary']};
        }}
        .styled-table tbody tr {{
            background: {c['bg_secondary']};
        }}
        .styled-table tbody tr:nth-child(even) {{
            background: rgba(30, 41, 59, 0.6);
        }}
        .styled-table tbody tr:hover {{
            background: {c['accent_glow']};
        }}
        .styled-table tbody tr:hover td {{
            color: {c['text_primary']};
        }}
        .styled-table tbody tr:hover td.numeric {{
            color: {c['accent_secondary']};
        }}
        .styled-table .null-value {{
            color: {c['text_muted']};
            font-style: italic;
        }}
        .styled-table .row-number {{
            color: {c['text_muted']};
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            width: 50px;
            text-align: center;
            padding-right: 0;
        }}
        .table-footer {{
            background: {c['bg_secondary']};
            padding: 0.75rem 1.25rem;
            color: {c['text_muted']};
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            border-top: 1px solid {c['border']};
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .table-footer .showing {{
            color: {c['text_tertiary']};
        }}
        .table-footer .total {{
            color: {c['accent_primary']};
        }}
    </style>
    <div class="styled-table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th class="row-number">#</th>
    '''

    # Headers
    for col in display_df.columns:
        is_numeric = col in numeric_cols
        align_class = 'numeric' if is_numeric else ''
        col_display = col.replace('_', ' ').title()
        table_html += f'<th class="{align_class}">{html.escape(col_display)}</th>'

    table_html += '</tr></thead><tbody>'

    # Rows
    for idx, (_, row) in enumerate(display_df.iterrows(), 1):
        table_html += f'<tr><td class="row-number">{idx}</td>'
        for col in display_df.columns:
            is_numeric = col in numeric_cols
            align_class = 'numeric' if is_numeric else ''
            formatted = format_cell_value(row[col], is_numeric)
            table_html += f'<td class="{align_class}">{formatted}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table>'

    # Footer with row count
    if len(df) > max_rows:
        table_html += f'''
        <div class="table-footer">
            <span class="showing">Showing {max_rows} of <span class="total">{len(df):,}</span> rows</span>
            <span>Scroll in raw data view for more</span>
        </div>
        '''
    else:
        table_html += f'''
        <div class="table-footer">
            <span class="showing"><span class="total">{len(df):,}</span> rows</span>
        </div>
        '''

    table_html += '</div>'
    st.markdown(table_html, unsafe_allow_html=True)


def render_chart(df: pd.DataFrame, chart_type: str):
    if chart_type == 'kpi':
        value = df.iloc[0, 0]
        label = df.columns[0]

        if isinstance(value, (int, float)):
            if value >= 1000000:
                formatted = f"{value/1000000:,.1f}M"
            elif value >= 1000:
                formatted = f"{value:,.0f}"
            else:
                formatted = f"{value:,.2f}"
        else:
            formatted = str(value)

        st.metric(label=label.replace('_', ' ').title(), value=formatted)

    elif chart_type == 'line':
        fig = px.line(df, x=df.columns[0], y=df.columns[1], markers=True)
        fig.update_traces(
            line=dict(color=PLOTLY_THEME['primary_color'], width=3),
            marker=dict(size=8, color=PLOTLY_THEME['primary_color'])
        )
        apply_plotly_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == 'bar':
        fig = px.bar(df, x=df.columns[0], y=df.columns[1])
        fig.update_traces(marker_color=PLOTLY_THEME['primary_color'], marker_line_width=0)
        apply_plotly_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

    else:
        render_styled_table(df)


# Sidebar
with st.sidebar:
    st.markdown("### // AI COPILOT")
    st.markdown(f'<p style="color: {c["text_tertiary"]}; font-size: 0.75rem;">Natural Language to SQL</p>', unsafe_allow_html=True)

    st.divider()

    st.markdown(f'<span class="section-title">Example Queries</span>', unsafe_allow_html=True)

    examples = {
        "Basic": [
            "What was total revenue in 2011?",
            "How many unique customers do we have?"
        ],
        "Intermediate": [
            "Show monthly revenue trend in 2011",
            "Top 10 products by revenue",
            "Average order value by country"
        ],
        "Advanced": [
            "Which products have the highest return rate?",
            "Customer lifetime value by country",
            "Revenue growth month over month"
        ]
    }

    for category, questions in examples.items():
        st.markdown(f'<p style="color: {c["text_tertiary"]}; font-size: 0.7rem; margin-top: 1rem; letter-spacing: 0.1em;">{category.upper()}</p>', unsafe_allow_html=True)
        for q in questions:
            if st.button(q, key=q, use_container_width=True):
                st.session_state.current_question = q
                st.rerun()

    st.divider()

    st.markdown(f'<span class="section-title">Settings</span>', unsafe_allow_html=True)
    st.session_state.show_sql = st.checkbox("Show Generated SQL", value=True)

    if st.button("Clear History", use_container_width=True):
        st.session_state.llm_client = LLMClient()
        st.session_state.query_history = []
        if 'current_question' in st.session_state:
            del st.session_state.current_question
        st.rerun()

    st.divider()
    st.markdown(f'<p style="color: {c["text_muted"]}; font-size: 0.7rem; font-family: \'JetBrains Mono\', monospace;">MODEL: {MODEL}</p>', unsafe_allow_html=True)

# Main content
st.markdown(f"""
<div class="page-header">
    <div class="page-title">
        <span class="page-title-icon">&#x26A1;</span>
        AI Copilot
    </div>
    <p class="page-subtitle">
        Ask questions about your business data in natural language
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<p class="query-label">Enter your query</p>', unsafe_allow_html=True)
question = st.text_input(
    "Your question",
    value=st.session_state.get('current_question', ''),
    placeholder="e.g., What was revenue by country in 2011?",
    label_visibility="collapsed"
)

if question:
    if len(question) > MAX_QUESTION_LENGTH:
        st.error(f"Question too long. Please limit to {MAX_QUESTION_LENGTH} characters.")
        st.stop()

    with st.spinner("Generating SQL..."):
        try:
            context = st.session_state.llm_client.get_context()
            result = st.session_state.llm_client.generate_sql(question, context)
            sql = result['sql']

            is_valid, validated_sql = SQLValidator.validate(sql)

            if not is_valid:
                st.error(f"SQL Validation Error: {validated_sql}")
                st.code(sql, language='sql')
            else:
                sql = validated_sql

                if st.session_state.show_sql:
                    with st.expander("// Generated SQL Query", expanded=False):
                        st.code(sql, language='sql')

                with st.spinner("Running query..."):
                    df = execute_sql(sql)

                if df is None or df.empty:
                    st.warning("No results found for your question.")
                else:
                    df = enrich_product_labels(df)

                    st.markdown(f"""
                    <div class="results-header">
                        <span class="results-badge">{len(df):,} results</span>
                    </div>
                    """, unsafe_allow_html=True)

                    chart_type = ChartSelector.select_chart_type(df, sql, question)
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        st.markdown(f'<span class="section-title">Visualization</span>', unsafe_allow_html=True)
                        render_chart(df, chart_type)

                    with col2:
                        st.markdown(f'<span class="section-title">Insight</span>', unsafe_allow_html=True)
                        with st.spinner("Analyzing..."):
                            insight = st.session_state.llm_client.generate_insight(question, df, sql)
                        safe_insight = html.escape(insight)
                        st.markdown(f"""
                        <div class="insight-container">
                            <p class="insight-text">{safe_insight}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with st.expander("// View Raw Data"):
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )

                    st.session_state.llm_client.add_to_history(question, sql)
                    st.session_state.query_history.append({
                        "question": question,
                        "sql": sql,
                        "rows": len(df)
                    })

        except Exception as e:
            st.error(f"Error: {str(e)}")
            with st.expander("See error details"):
                st.exception(e)

else:
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">&#x2328;</div>
        <div class="empty-state-title">Ready to explore your data</div>
        <div class="empty-state-text">Type a question above or select an example from the sidebar</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.query_history:
    st.markdown("---")
    st.markdown(f'<span class="section-title">Recent Queries</span>', unsafe_allow_html=True)

    for item in reversed(st.session_state.query_history[-5:]):
        with st.expander(f"{item['question']} ({item['rows']:,} rows)"):
            st.code(item['sql'], language='sql')
