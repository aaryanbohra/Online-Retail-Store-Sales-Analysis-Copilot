"""Copilot Page - AI-powered natural language queries"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import html
import logging
from utils.llm_client import LLMClient
from utils.sql_validator import SQLValidator
from utils.chart_selector import ChartSelector
from config import DATABASE_PATH, MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security: Maximum allowed question length
MAX_QUESTION_LENGTH = 500

# Clean, minimal CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar dark theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: white !important;
        border-radius: 8px;
        transition: all 0.2s;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.15);
        border-color: rgba(255,255,255,0.3);
    }

    /* Main content area */
    .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    /* Input field */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }

    .stTextInput input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
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
    """Execute SQL query and return results as DataFrame"""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        st.error(f"SQL execution error: {str(e)}")
        return None
    finally:
        conn.close()

def enrich_product_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure product labels use description rather than stock codes when possible"""
    cols_lower = [c.lower() for c in df.columns]

    if 'stock_code' in cols_lower and 'description' in cols_lower:
        desc_col = df.columns[cols_lower.index('description')]
        new_cols = [desc_col] + [c for c in df.columns if c != desc_col]
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
                new_cols = ['product'] + [c for c in merged.columns if c != 'product']
                merged = merged[new_cols].rename(columns={'product': 'description'})
            return merged
        except Exception as e:
            logger.warning(f"Failed to enrich product labels: {e}")
            return df

    return df

def render_chart(df: pd.DataFrame, chart_type: str):
    """Render appropriate visualization"""

    # Theme colors
    primary_color = '#6366f1'

    if chart_type == 'kpi':
        value = df.iloc[0, 0]
        label = df.columns[0]

        if isinstance(value, (int, float)):
            if value >= 1000000:
                formatted = f"${value/1000000:,.1f}M"
            elif value >= 1000:
                formatted = f"${value:,.0f}"
            else:
                formatted = f"{value:,.2f}"
        else:
            formatted = str(value)

        # Use Streamlit metric with custom styling
        st.metric(label=label.replace('_', ' ').title(), value=formatted)

    elif chart_type == 'line':
        fig = px.line(
            df,
            x=df.columns[0],
            y=df.columns[1],
            markers=True
        )
        fig.update_traces(
            line=dict(color=primary_color, width=2.5),
            marker=dict(size=6, color=primary_color)
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == 'bar':
        fig = px.bar(
            df,
            x=df.columns[0],
            y=df.columns[1]
        )
        fig.update_traces(marker_color=primary_color)
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
        st.plotly_chart(fig, use_container_width=True)

    else:  # table
        st.dataframe(df, use_container_width=True, hide_index=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🤖 AI Copilot")
    st.caption("Natural Language to SQL")

    st.divider()

    # Example questions
    st.markdown("**Try an example:**")

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
        st.markdown(f"*{category}*")
        for q in questions:
            if st.button(q, key=q, use_container_width=True):
                st.session_state.current_question = q
                st.rerun()

    st.divider()

    # Settings
    st.markdown("**Settings**")
    st.session_state.show_sql = st.checkbox("Show Generated SQL", value=True)

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.llm_client = LLMClient()
        st.session_state.query_history = []
        if 'current_question' in st.session_state:
            del st.session_state.current_question
        st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")

# ===== MAIN CONTENT =====

# Header
st.title("🤖 AI Copilot")
st.markdown("Ask questions about your business data in natural language")

st.write("")

# Input
question = st.text_input(
    "Your question",
    value=st.session_state.get('current_question', ''),
    placeholder="e.g., What was revenue by country in 2011?",
    label_visibility="collapsed"
)

# Process question
if question:
    # Security: Validate input length to prevent abuse
    if len(question) > MAX_QUESTION_LENGTH:
        st.error(f"Question too long. Please limit to {MAX_QUESTION_LENGTH} characters.")
        st.stop()

    with st.spinner("Generating SQL..."):
        try:
            # Generate SQL
            context = st.session_state.llm_client.get_context()
            result = st.session_state.llm_client.generate_sql(question, context)

            sql = result['sql']

            # Validate SQL
            is_valid, validated_sql = SQLValidator.validate(sql)

            if not is_valid:
                st.error(f"SQL Validation Error: {validated_sql}")
                st.code(sql, language='sql')
            else:
                sql = validated_sql

                # Show SQL if enabled
                if st.session_state.show_sql:
                    with st.expander("🔍 Generated SQL Query", expanded=False):
                        st.code(sql, language='sql')

                # Execute query
                with st.spinner("Running query..."):
                    df = execute_sql(sql)

                if df is None or df.empty:
                    st.warning("No results found for your question.")
                else:
                    # Enrich product labels
                    df = enrich_product_labels(df)

                    # Results header
                    st.success(f"Found {len(df):,} results")

                    # Chart and insight in columns
                    chart_type = ChartSelector.select_chart_type(df, sql, question)

                    col1, col2 = st.columns([3, 2])

                    with col1:
                        st.subheader("📊 Visualization")
                        render_chart(df, chart_type)

                    with col2:
                        st.subheader("💡 Insight")
                        with st.spinner("Analyzing..."):
                            insight = st.session_state.llm_client.generate_insight(question, df, sql)
                        # Security: Escape HTML to prevent XSS attacks
                        safe_insight = html.escape(insight)
                        st.markdown(f"""
                        <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 1rem; border-radius: 0 8px 8px 0; color: #0c4a6e; line-height: 1.6;">
                            {safe_insight}
                        </div>
                        """, unsafe_allow_html=True)

                    # Raw data
                    with st.expander("📋 View Raw Data"):
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )

                    # Add to history
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
    # Empty state
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem; color: #6b7280;">
                <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</p>
                <p style="font-size: 1.1rem; font-weight: 500; margin-bottom: 0.25rem;">Ready to explore your data</p>
                <p style="font-size: 0.9rem;">Type a question above or select an example from the sidebar</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Query history
if st.session_state.query_history:
    st.markdown("---")
    st.subheader("📜 Recent Queries")

    for item in reversed(st.session_state.query_history[-5:]):
        with st.expander(f"{item['question']} ({item['rows']:,} rows)"):
            st.code(item['sql'], language='sql')
