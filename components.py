"""
SankalpRoom - UI Components
Reusable UI components and global styles.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Dark Background ── */
.stApp {
    background-color: #0F1115;
    color: #E2E8F0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13161E !important;
    border-right: 1px solid #1E2235;
}

[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #9CA3AF !important;
    text-align: left !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.75rem !important;
    transition: all 0.15s ease;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #1E2235 !important;
    border-color: #2D3148 !important;
    color: #E2E8F0 !important;
}

/* ── Headers ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: #E2E8F0 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #1A1D27 !important;
    border: 1px solid #2D3148 !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1A1D27 !important;
    border: 1px solid #2D3148 !important;
    color: #9CA3AF !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease !important;
    padding: 0.4rem 0.8rem !important;
}

.stButton > button:hover {
    background: #2D3148 !important;
    color: #E2E8F0 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5, #6D28D9) !important;
    border-color: #4F46E5 !important;
    color: white !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6D28D9, #4F46E5) !important;
    box-shadow: 0 0 20px rgba(79,70,229,0.4) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0.25rem;
    border-bottom: 1px solid #2D3148;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6B7280 !important;
    border-radius: 8px 8px 0 0 !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important;
}

.stTabs [aria-selected="true"] {
    background: #4F46E5 !important;
    color: white !important;
}

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: #1A1D27 !important;
    border: 1px solid #2D3148 !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
    padding: 0.75rem !important;
}

[data-testid="stChatInput"] textarea {
    background: #1A1D27 !important;
    border: 1px solid #2D3148 !important;
    color: #E2E8F0 !important;
    border-radius: 12px !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: #13161E !important;
    border: 1px solid #2D3148 !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
}

/* ── Info/Success/Warning ── */
.stAlert {
    border-radius: 10px !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: #1A1D27 !important;
    border: 1px solid #2D3148 !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr {
    border-color: #2D3148 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0F1115; }
::-webkit-scrollbar-thumb { background: #2D3148; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F46E5; }
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_topbar(user_name: str, room_name: str = None, subgroup_name: str = None):
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.5rem;
        background: #13161E;
        border-bottom: 1px solid #1E2235;
        margin-bottom: 1.5rem;
        border-radius: 0 0 12px 12px;
    ">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="
                font-family: 'Syne', sans-serif;
                font-size: 1.4rem;
                font-weight: 800;
                background: linear-gradient(135deg, #4F46E5, #8B5CF6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">⚡ SankalpRoom</span>
            {'<span style="color:#2D3148; font-size:1.2rem;">›</span>' if room_name else ''}
            {'<span style="color:#9CA3AF; font-size:0.9rem;">' + room_name + '</span>' if room_name else ''}
            {'<span style="color:#2D3148; font-size:1.2rem;">›</span>' if subgroup_name else ''}
            {'<span style="color:#8B5CF6; font-size:0.9rem;">' + subgroup_name + '</span>' if subgroup_name else ''}
        </div>
        <div style="
            display:flex; align-items:center; gap:0.75rem;
            color:#9CA3AF; font-size:0.85rem;
        ">
            <span>👤 {user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats: list):
    """Render metric cards. stats = [{'label': str, 'value': str, 'icon': str, 'color': str}]"""
    cols = st.columns(len(stats))
    for i, stat in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: #1A1D27;
                border: 1px solid #2D3148;
                border-top: 3px solid {stat.get('color','#4F46E5')};
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
            ">
                <div style="font-size:1.5rem;">{stat.get('icon','📊')}</div>
                <div style="
                    font-size:1.8rem;
                    font-weight:700;
                    font-family:'Syne',sans-serif;
                    color:{stat.get('color','#4F46E5')};
                ">{stat['value']}</div>
                <div style="color:#6B7280; font-size:0.78rem; margin-top:0.2rem;">{stat['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_member_avatars(members: list, max_show: int = 6):
    avatars = ""
    for i, m in enumerate(members[:max_show]):
        color = m.get("avatar_color", "#4F46E5")
        initials = "".join(w[0].upper() for w in m["name"].split()[:2])
        avatars += f"""<div title="{m['name']}" style="
            width:32px; height:32px; border-radius:50%;
            background: {color};
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.7rem; font-weight:700; color:white;
            border: 2px solid #0F1115;
            margin-right:-6px;
        ">{initials}</div>"""
    if len(members) > max_show:
        avatars += f"""<div style="
            width:32px; height:32px; border-radius:50%;
            background: #2D3148;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.65rem; color:#9CA3AF;
            border: 2px solid #0F1115;
            margin-right:-6px;
        ">+{len(members)-max_show}</div>"""
    st.markdown(f'<div style="display:flex; align-items:center;">{avatars}</div>', unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 1rem;
        color: #6B7280;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#9CA3AF; margin-bottom:0.5rem;">{title}</div>
        <div style="font-size:0.85rem;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, color: str = "#4F46E5"):
    st.markdown(f"""
    <span style="
        background: {color}22;
        color: {color};
        border: 1px solid {color}44;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-weight: 600;
    ">{text}</span>
    """, unsafe_allow_html=True)
