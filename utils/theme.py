"""Theme system for the analytics application"""

import streamlit as st

THEME_COLORS = {
    'bg_primary': '#0f172a',
    'bg_secondary': '#1e293b',
    'bg_tertiary': '#334155',
    'bg_card': '#1e293b',
    'bg_card_hover': '#273548',
    'accent_primary': '#f59e0b',
    'accent_secondary': '#fbbf24',
    'accent_tertiary': '#d97706',
    'accent_glow': 'rgba(245, 158, 11, 0.12)',
    'accent_glow_strong': 'rgba(245, 158, 11, 0.2)',
    'text_primary': '#f1f5f9',
    'text_secondary': '#cbd5e1',
    'text_tertiary': '#94a3b8',
    'text_muted': '#64748b',
    'border': 'rgba(148, 163, 184, 0.15)',
    'border_hover': 'rgba(245, 158, 11, 0.4)',
    'border_subtle': 'rgba(255, 255, 255, 0.08)',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'info': '#06b6d4',
    'card_bg': 'rgba(30, 41, 59, 0.9)',
    'sidebar_bg': '#0f172a',
    'sidebar_text': '#e2e8f0',
    'sidebar_text_muted': '#94a3b8',
    'sidebar_border': 'rgba(148, 163, 184, 0.15)',
    'sidebar_accent': '#fbbf24',
    'glass': 'rgba(255, 255, 255, 0.04)',
    'grain_opacity': '0.025',
    'shadow_sm': '0 1px 3px rgba(0, 0, 0, 0.25)',
    'shadow_md': '0 4px 12px rgba(0, 0, 0, 0.3)',
    'shadow_lg': '0 12px 40px rgba(0, 0, 0, 0.4)',
}


def get_theme_colors():
    return THEME_COLORS


def init_theme():
    pass


def render_theme_toggle():
    pass


def get_global_css():
    c = THEME_COLORS
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Sora:wght@300;400;500;600;700;800&display=swap');

    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        opacity: {c['grain_opacity']};
        z-index: 1000;
        pointer-events: none;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    }}

    :root {{
        --bg-primary: {c['bg_primary']};
        --bg-secondary: {c['bg_secondary']};
        --bg-tertiary: {c['bg_tertiary']};
        --bg-card: {c['bg_card']};
        --accent: {c['accent_primary']};
        --accent-bright: {c['accent_secondary']};
        --accent-deep: {c['accent_tertiary']};
        --accent-glow: {c['accent_glow']};
        --text-primary: {c['text_primary']};
        --text-secondary: {c['text_secondary']};
        --text-tertiary: {c['text_tertiary']};
        --border: {c['border']};
        --font-display: 'Sora', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 0% 0%, {c['accent_glow']} 0%, transparent 50%),
            radial-gradient(ellipse at 100% 100%, {c['accent_glow']} 0%, transparent 50%),
            linear-gradient(180deg, {c['bg_primary']} 0%, {c['bg_secondary']} 100%);
        background-attachment: fixed;
    }}

    * {{ font-family: var(--font-display); }}
    code, pre, .stCode {{ font-family: var(--font-mono) !important; }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    .animate-fade-in {{ animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
    .animate-delay-1 {{ animation-delay: 0.1s; opacity: 0; }}
    .animate-delay-2 {{ animation-delay: 0.2s; opacity: 0; }}
    .animate-delay-3 {{ animation-delay: 0.3s; opacity: 0; }}

    section[data-testid="stSidebar"] {{
        background: {c['sidebar_bg']};
        backdrop-filter: blur(20px);
        border-right: none;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
    }}
    section[data-testid="stSidebar"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, {c['sidebar_accent']}, {c['accent_primary']}, {c['sidebar_accent']});
        z-index: 10;
    }}
    section[data-testid="stSidebar"] > div {{
        padding-top: 2.5rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }}
    section[data-testid="stSidebar"] * {{ color: {c['sidebar_text']} !important; }}
    section[data-testid="stSidebar"] p {{ color: {c['sidebar_text_muted']} !important; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {c['sidebar_accent']} !important;
        font-family: var(--font-mono) !important;
        font-weight: 600;
        font-size: 0.7rem !important;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {c['sidebar_border']};
    }}
    section[data-testid="stSidebar"] .stButton button,
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] .stButton button p,
    section[data-testid="stSidebar"] .stButton button span {{
        background: linear-gradient(135deg, {c['accent_tertiary']} 0%, {c['accent_primary']} 100%) !important;
        border: none !important;
        color: #0d0d0d !important;
        border-radius: 10px !important;
        font-family: 'Sora', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 0 !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: left !important;
        padding: 0.875rem 1.25rem !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        line-height: 1.4 !important;
    }}
    section[data-testid="stSidebar"] .stButton button:hover,
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: linear-gradient(135deg, {c['accent_primary']} 0%, {c['accent_secondary']} 100%) !important;
        color: #000000 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.3) !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: {c['sidebar_border']} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover {{
        border-color: {c['sidebar_accent']} !important;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }}

    h1 {{
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        color: {c['text_primary']} !important;
        line-height: 1.1;
    }}
    h2, h3 {{
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        color: {c['text_primary']} !important;
        letter-spacing: -0.02em;
    }}

    .stTextInput > div > div > input {{
        background: {c['bg_card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
        color: {c['text_primary']} !important;
        font-size: 1rem !important;
        padding: 1rem 1.25rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {c['accent_primary']} !important;
        box-shadow: 0 0 0 3px {c['accent_glow']}, 0 0 30px {c['accent_glow']} !important;
    }}
    .stTextInput > div > div > input::placeholder {{ color: {c['text_muted']} !important; }}

    .stButton > button {{
        background: linear-gradient(135deg, {c['accent_tertiary']} 0%, {c['accent_primary']} 50%, {c['accent_secondary']} 100%) !important;
        background-size: 200% 200% !important;
        border: none !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 40px {c['accent_glow_strong']}, 0 0 60px {c['accent_glow']} !important;
    }}

    [data-testid="stMetric"] {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: {c['shadow_sm']};
    }}
    [data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; width: 3px; height: 100%;
        background: linear-gradient(180deg, {c['accent_secondary']}, {c['accent_primary']}, {c['accent_tertiary']});
        border-radius: 3px 0 0 3px;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        border-color: {c['border_hover']};
        box-shadow: {c['shadow_lg']}, 0 0 40px {c['accent_glow']};
    }}
    [data-testid="stMetric"] label {{
        color: {c['text_tertiary']} !important;
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {c['text_primary']} !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        background: linear-gradient(135deg, {c['text_primary']}, {c['accent_secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .streamlit-expanderHeader {{
        background: {c['bg_card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        color: {c['text_secondary']} !important;
        transition: all 0.3s ease !important;
    }}
    .streamlit-expanderHeader:hover {{
        border-color: {c['accent_primary']} !important;
        color: {c['accent_primary']} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {c['bg_card']};
        border-radius: 16px;
        padding: 6px;
        border: 1px solid {c['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 0.9rem;
        font-weight: 500;
        color: {c['text_tertiary']} !important;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {c['text_primary']} !important;
        background: {c['glass']};
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {c['accent_tertiary']}, {c['accent_primary']}) !important;
        color: #0f172a !important;
        box-shadow: 0 4px 20px {c['accent_glow_strong']};
    }}

    /* Enhanced DataFrame Styling */
    .stDataFrame {{
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid {c['border']} !important;
        background: {c['card_bg']} !important;
    }}
    .stDataFrame > div {{
        border-radius: 16px !important;
        overflow: hidden !important;
    }}
    .stDataFrame [data-testid="stDataFrameResizable"] {{
        border-radius: 16px !important;
        overflow: hidden !important;
        background: transparent !important;
    }}
    /* Header cells */
    .stDataFrame th,
    .stDataFrame [role="columnheader"] {{
        background: linear-gradient(180deg, {c['bg_tertiary']} 0%, {c['bg_secondary']} 100%) !important;
        color: {c['accent_primary']} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 1rem 1.25rem !important;
        border-bottom: 2px solid {c['accent_primary']} !important;
        white-space: nowrap !important;
    }}
    /* Data cells */
    .stDataFrame td,
    .stDataFrame [role="gridcell"] {{
        background: {c['bg_secondary']} !important;
        color: {c['text_secondary']} !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 0.875rem !important;
        padding: 0.875rem 1.25rem !important;
        border-bottom: 1px solid {c['border_subtle']} !important;
        transition: all 0.2s ease !important;
    }}
    /* Alternating rows */
    .stDataFrame tr:nth-child(even) td,
    .stDataFrame [role="row"]:nth-child(even) [role="gridcell"] {{
        background: rgba(30, 41, 59, 0.7) !important;
    }}
    /* Row hover */
    .stDataFrame tr:hover td,
    .stDataFrame [role="row"]:hover [role="gridcell"] {{
        background: {c['accent_glow']} !important;
        color: {c['text_primary']} !important;
    }}
    /* Numeric cells - right align */
    .stDataFrame td[data-type="number"],
    .stDataFrame [role="gridcell"]:has([data-testid="StyledLinkIconContainer"]) {{
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
    }}
    /* Remove default glare effects */
    .stDataFrame .glideDataEditor,
    .stDataFrame [class*="glide"] {{
        background: transparent !important;
    }}

    .stSelectbox [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div {{
        background: {c['bg_card']} !important;
        border-color: {c['border']} !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }}
    .stSelectbox [data-baseweb="select"] > div:hover {{
        border-color: {c['accent_primary']} !important;
    }}

    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {c['border']}, transparent);
        margin: 2.5rem 0;
    }}

    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {c['bg_secondary']}; }}
    ::-webkit-scrollbar-thumb {{ background: {c['border']}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {c['accent_primary']}; }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    .stCheckbox label span {{ color: {c['text_secondary']} !important; }}
</style>
"""


def get_hero_css():
    c = THEME_COLORS
    return f"""
<style>
    .hero-container {{ position: relative; padding: 4rem 0 3rem 0; margin-bottom: 2rem; }}
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {c['accent_glow']};
        border: 1px solid {c['border']};
        border-radius: 100px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        color: {c['accent_primary']};
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .hero-badge::before {{
        content: '';
        width: 6px; height: 6px;
        background: {c['accent_primary']};
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }}
    .hero-title {{
        font-family: 'Sora', sans-serif;
        font-size: clamp(3rem, 8vw, 5rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.05;
        color: {c['text_primary']};
        margin: 0 0 0.5rem 0;
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: 0.1s;
        opacity: 0;
    }}
    .hero-title .accent {{
        background: linear-gradient(135deg, {c['accent_primary']}, {c['accent_secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .hero-subtitle {{
        font-family: 'Sora', sans-serif;
        font-size: 1.15rem;
        color: {c['text_tertiary']};
        margin-top: 1rem;
        max-width: 500px;
        line-height: 1.6;
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: 0.2s;
        opacity: 0;
    }}
    .hero-line {{
        width: 60px; height: 4px;
        background: linear-gradient(90deg, {c['accent_primary']}, {c['accent_secondary']});
        border-radius: 2px;
        margin-top: 2rem;
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: 0.3s;
        opacity: 0;
    }}
</style>
"""


def get_card_css():
    c = THEME_COLORS
    return f"""
<style>
    .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; margin: 2rem 0; }}
    @media (max-width: 1200px) {{ .stat-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .stat-card {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 1.75rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        box-shadow: {c['shadow_sm']};
    }}
    .stat-card:nth-child(1) {{ animation-delay: 0.1s; opacity: 0; }}
    .stat-card:nth-child(2) {{ animation-delay: 0.15s; opacity: 0; }}
    .stat-card:nth-child(3) {{ animation-delay: 0.2s; opacity: 0; }}
    .stat-card:nth-child(4) {{ animation-delay: 0.25s; opacity: 0; }}
    .stat-card:hover {{
        transform: translateY(-8px);
        border-color: {c['border_hover']};
        box-shadow: {c['shadow_lg']}, 0 0 50px {c['accent_glow']};
    }}
    .stat-icon {{ font-size: 1.75rem; margin-bottom: 1rem; display: inline-block; transition: transform 0.3s ease; }}
    .stat-card:hover .stat-icon {{ transform: scale(1.1); }}
    .stat-value {{
        font-family: 'Sora', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {c['text_primary']}, {c['accent_secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }}
    .stat-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        color: {c['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 0.5rem;
    }}

    .feature-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin: 2rem 0; }}
    .feature-card {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        box-shadow: {c['shadow_sm']};
    }}
    .feature-card:nth-child(1) {{ animation-delay: 0.1s; opacity: 0; }}
    .feature-card:nth-child(2) {{ animation-delay: 0.15s; opacity: 0; }}
    .feature-card:nth-child(3) {{ animation-delay: 0.2s; opacity: 0; }}
    .feature-card:nth-child(4) {{ animation-delay: 0.25s; opacity: 0; }}
    .feature-card::before {{
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0; width: 3px;
        background: linear-gradient(180deg, {c['accent_secondary']}, {c['accent_primary']}, {c['accent_tertiary']});
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    .feature-card:hover {{
        transform: translateX(8px);
        border-color: {c['border_hover']};
        box-shadow: {c['shadow_md']};
    }}
    .feature-card:hover::before {{ opacity: 1; }}
    .feature-icon {{ font-size: 2.5rem; margin-bottom: 1.25rem; display: inline-block; transition: transform 0.3s ease; }}
    .feature-card:hover .feature-icon {{ transform: scale(1.1) rotate(-5deg); }}
    .feature-title {{ font-family: 'Sora', sans-serif; font-size: 1.2rem; font-weight: 600; color: {c['text_primary']}; margin-bottom: 0.75rem; }}
    .feature-desc {{ font-size: 0.95rem; color: {c['text_secondary']}; line-height: 1.7; }}
</style>
"""


def get_section_css():
    c = THEME_COLORS
    return f"""
<style>
    .section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; }}
    .section-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: {c['accent_primary']};
        text-transform: uppercase;
        letter-spacing: 0.15em;
        padding-left: 1rem;
        border-left: 3px solid {c['accent_primary']};
    }}
    .chart-section-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: {c['accent_primary']};
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
        padding-left: 1rem;
        border-left: 3px solid {c['accent_primary']};
    }}
    .insight-box {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-left: 3px solid {c['accent_primary']};
        padding: 1.5rem;
        border-radius: 0 16px 16px 0;
        color: {c['text_secondary']};
        font-size: 0.95rem;
        line-height: 1.8;
    }}
    .empty-state {{ text-align: center; padding: 5rem 2rem; }}
    .empty-state-icon {{ font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.3; }}
    .empty-state-title {{ font-size: 1.5rem; font-weight: 600; color: {c['text_tertiary']}; margin-bottom: 0.75rem; }}
    .empty-state-text {{ font-size: 1rem; color: {c['text_muted']}; }}
    .getting-started {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2.5rem 0;
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: 0.4s;
        opacity: 0;
    }}
    .getting-started h4 {{
        color: {c['text_primary']};
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .getting-started h4::before {{ content: '//'; color: {c['accent_primary']}; font-family: 'JetBrains Mono', monospace; }}
    .getting-started ol {{ color: {c['text_secondary']}; line-height: 2.2; padding-left: 1.5rem; }}
    .getting-started li {{ margin-bottom: 1rem; }}
    .getting-started li strong {{ color: {c['text_primary']}; }}
    .getting-started code {{
        background: {c['accent_glow']};
        color: {c['accent_primary']};
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }}
    .footer-text {{ color: {c['text_muted']}; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; }}
    .footer-text a {{ color: {c['accent_primary']}; text-decoration: none; }}
    .footer-text a:hover {{ color: {c['accent_secondary']}; }}
</style>
"""


def get_table_css():
    c = THEME_COLORS
    return f"""
<style>
    .data-table-container {{
        background: {c['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {c['border']};
        border-radius: 16px;
        overflow: hidden;
        margin: 1rem 0 2rem 0;
    }}
    .data-table {{ width: 100%; border-collapse: collapse; }}
    .data-table th {{
        background: {c['bg_secondary']};
        color: {c['accent_primary']};
        padding: 1rem 1.25rem;
        text-align: left;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border-bottom: 1px solid {c['border']};
    }}
    .data-table td {{
        padding: 1rem 1.25rem;
        color: {c['text_secondary']};
        font-size: 0.9rem;
        border-bottom: 1px solid {c['border_subtle']};
        transition: all 0.2s ease;
    }}
    .data-table tr:last-child td {{ border-bottom: none; }}
    .data-table tr:hover td {{ background: {c['accent_glow']}; color: {c['text_primary']}; }}
    .data-table code {{
        background: {c['accent_glow']};
        color: {c['accent_primary']};
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }}
</style>
"""


def get_plotly_theme():
    c = THEME_COLORS
    return {
        'bg_color': 'rgba(0,0,0,0)',
        'paper_color': 'rgba(0,0,0,0)',
        'font_color': c['text_secondary'],
        'grid_color': c['border_subtle'],
        'primary_color': c['accent_primary'],
        'secondary_color': c['accent_secondary'],
        'color_sequence': [
            c['accent_primary'], c['accent_secondary'], c['accent_tertiary'],
            '#ea580c', '#c2410c', '#9a3412'
        ],
        'color_scale': [
            [0, '#7c2d12'], [0.25, '#9a3412'], [0.5, c['accent_tertiary']],
            [0.75, c['accent_primary']], [1, c['accent_secondary']]
        ]
    }


def apply_plotly_theme(fig, height=350):
    theme = get_plotly_theme()
    c = THEME_COLORS
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor=theme['bg_color'],
        paper_bgcolor=theme['paper_color'],
        font_color=theme['font_color'],
        font_family='Sora',
        height=height,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=c['bg_card'],
            font_size=12,
            font_family='JetBrains Mono',
            bordercolor=c['accent_primary']
        )
    )
    fig.update_xaxes(color=theme['font_color'], showgrid=False, linecolor=c['border'], tickfont=dict(size=11))
    fig.update_yaxes(color=theme['font_color'], showgrid=True, gridcolor=theme['grid_color'], linecolor=c['border'], tickfont=dict(size=11))
    return fig


def get_chart_title_css():
    c = THEME_COLORS
    return f"""
<style>
    .chart-section-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: {c['accent_primary']};
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
        padding-left: 1rem;
        border-left: 3px solid {c['accent_primary']};
    }}
</style>
"""


# Aliases for compatibility
get_stat_card_css = get_card_css
get_data_table_css = get_table_css
