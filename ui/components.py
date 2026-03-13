"""
SankalpRoom - UI Components
Sharp editorial dark UI. Space Grotesk + Inter.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

.stApp {
    background: #080A0F !important;
    color: #CBD5E1;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0C0E14 !important;
    border-right: 1px solid #1C2030 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #64748B !important;
    text-align: left !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 0.75rem !important;
    width: 100% !important;
    transition: all 0.1s !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #131720 !important;
    color: #E2E8F0 !important;
    border-left: 2px solid #6366F1 !important;
    padding-left: calc(0.75rem - 2px) !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F1F5F9 !important;
    letter-spacing: -0.02em !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0F1218 !important;
    border: 1px solid #1E2533 !important;
    color: #E2E8F0 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 0.875rem !important;
    transition: border-color 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    outline: none !important;
}
.stTextInput > label, .stTextArea > label,
.stSelectbox > label, .stMultiSelect > label {
    color: #64748B !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0F1218 !important;
    border: 1px solid #1E2533 !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: #0F1218 !important;
    border: 1px solid #1E2533 !important;
    border-radius: 6px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #0F1218 !important;
    border: 1px solid #1E2533 !important;
    color: #94A3B8 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.12s ease !important;
}
.stButton > button:hover {
    background: #131720 !important;
    border-color: #2D3650 !important;
    color: #E2E8F0 !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: #6366F1 !important;
    border-color: #6366F1 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #4F52D9 !important;
    border-color: #4F52D9 !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1C2030 !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #475569 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #6366F1 !important;
    border-bottom: 2px solid #6366F1 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94A3B8 !important;
    background: transparent !important;
}

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: #0C0E14 !important;
    border: 1px solid #1C2030 !important;
    border-radius: 8px !important;
    padding: 0.875rem 1rem !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatInput"] > div {
    background: #0C0E14 !important;
    border: 1px solid #1C2030 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: #0C0E14 !important;
    border: 1px solid #1C2030 !important;
    border-radius: 8px !important;
    padding: 1.25rem !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0C0E14 !important;
    border: 1px solid #1C2030 !important;
    border-radius: 6px !important;
}
[data-testid="stExpander"] summary {
    color: #64748B !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stExpander"] summary:hover { color: #94A3B8 !important; }

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid #1C2030 !important; margin: 0.75rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1C2030; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #6366F1; }

[data-testid="stVerticalBlock"] { gap: 0.5rem; }

.stDateInput > div > div > input {
    background: #0F1218 !important;
    border: 1px solid #1E2533 !important;
    color: #E2E8F0 !important;
    border-radius: 6px !important;
}

.stSpinner > div { border-top-color: #6366F1 !important; }
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_topbar(user_name: str, room_name: str = None, subgroup_name: str = None):
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    crumb = ""
    if room_name:
        crumb += f'<span style="color:#2D3650;margin:0 0.4rem;">/</span><span style="color:#64748B;font-size:0.82rem;font-family:Inter,sans-serif;">{room_name}</span>'
    if subgroup_name:
        crumb += f'<span style="color:#2D3650;margin:0 0.4rem;">/</span><span style="color:#818CF8;font-size:0.82rem;font-family:Inter,sans-serif;">{subgroup_name}</span>'

    st.markdown(f"""
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding: 0 1.5rem; height: 52px;
        background: #080A0F;
        border-bottom: 1px solid #1C2030;
        margin-bottom: 1.75rem;
    ">
        <div style="display:flex; align-items:center;">
            <span style="
                font-family:'Space Grotesk',sans-serif;
                font-size:1.05rem; font-weight:700;
                color:#6366F1; letter-spacing:-0.02em;
                margin-right:0.25rem;
            ">⚡ sankalproom</span>
            {crumb}
        </div>
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <div style="
                width:30px; height:30px; border-radius:50%;
                background:linear-gradient(135deg,#6366F1,#8B5CF6);
                display:flex; align-items:center; justify-content:center;
                font-size:0.68rem; font-weight:700; color:white;
                font-family:'Space Grotesk',sans-serif;
            ">{initials}</div>
            <span style="color:#475569; font-size:0.8rem; font-family:'Inter',sans-serif;">{user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats: list):
    cols = st.columns(len(stats))
    for i, s in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background:#0C0E14; border:1px solid #1C2030;
                border-radius:8px; padding:1rem 1.25rem;
                margin-bottom:1rem; position:relative; overflow:hidden;
            ">
                <div style="
                    position:absolute; top:0; left:0; right:0; height:2px;
                    background:{s.get('color','#6366F1')}; opacity:0.8;
                "></div>
                <div style="
                    font-family:'Space Grotesk',sans-serif;
                    font-size:1.6rem; font-weight:700;
                    color:{s.get('color','#6366F1')};
                    line-height:1; margin-bottom:0.3rem;
                ">{s['value']}</div>
                <div style="
                    color:#475569; font-size:0.72rem; font-weight:500;
                    text-transform:uppercase; letter-spacing:0.06em;
                    font-family:'Inter',sans-serif;
                ">{s['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_member_avatars(members: list, max_show: int = 7):
    avs = ""
    for m in members[:max_show]:
        c   = m.get("avatar_color", "#6366F1")
        ini = "".join(w[0].upper() for w in m["name"].split()[:2])
        avs += f"""<div title="{m['name']}" style="
            width:28px; height:28px; border-radius:50%;
            background:{c}; color:white;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.62rem; font-weight:700;
            border:2px solid #080A0F;
            margin-right:-7px;
            font-family:'Space Grotesk',sans-serif;
        ">{ini}</div>"""
    if len(members) > max_show:
        avs += f"""<div style="
            width:28px; height:28px; border-radius:50%;
            background:#1C2030; color:#64748B;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.6rem; border:2px solid #080A0F; margin-right:-7px;
        ">+{len(members)-max_show}</div>"""
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:0.5rem;">{avs}</div>', unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div style="
        text-align:center; padding:3.5rem 1rem;
        border:1px dashed #1C2030; border-radius:8px; margin:1rem 0;
    ">
        <div style="font-size:2rem; margin-bottom:0.75rem; opacity:0.4;">{icon}</div>
        <div style="
            font-family:'Space Grotesk',sans-serif;
            font-size:0.9rem; font-weight:600;
            color:#334155; margin-bottom:0.35rem;
        ">{title}</div>
        <div style="color:#1E293B; font-size:0.78rem; font-family:'Inter',sans-serif;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, color: str = "#6366F1"):
    st.markdown(f"""
    <span style="
        background:{color}18; color:{color};
        border:1px solid {color}30; border-radius:4px;
        padding:2px 8px; font-size:0.7rem; font-weight:600;
        font-family:'Inter',sans-serif;
        letter-spacing:0.04em; text-transform:uppercase;
    ">{text}</span>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <div style="
            font-family:'Space Grotesk',sans-serif;
            font-size:1rem; font-weight:700;
            color:#F1F5F9; letter-spacing:-0.01em;
        ">{title}</div>
        {'<div style="color:#475569;font-size:0.78rem;margin-top:0.2rem;font-family:Inter,sans-serif;">'+subtitle+'</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_invite_pill(code: str):
    st.markdown(f"""
    <div style="
        display:inline-flex; align-items:center; gap:0.6rem;
        background:#0C0E14; border:1px solid #1C2030;
        border-radius:6px; padding:0.4rem 0.875rem;
    ">
        <span style="
            color:#334155; font-size:0.7rem; font-weight:600;
            text-transform:uppercase; letter-spacing:0.08em;
            font-family:'Inter',sans-serif;
        ">Invite</span>
        <span style="
            font-family:'Space Grotesk',sans-serif;
            font-size:0.95rem; font-weight:700;
            color:#6366F1; letter-spacing:0.12em;
        ">{code}</span>
    </div>
    """, unsafe_allow_html=True)
