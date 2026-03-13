"""
SankalpRoom - UI Components
Aesthetic: Warm dark — deep charcoal base, amber/gold accents, generous whitespace.
Font: Clash Display (headings) + Outfit (body)
Vibe: Premium product tool, not a dev dashboard.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
@import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}

/* ── App shell ── */
.stApp {
    background: #141414 !important;
    color: #D4D0C8;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0F0F0F !important;
    border-right: 1px solid #222 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #555 !important;
    text-align: left !important;
    border-radius: 6px !important;
    font-size: 0.83rem !important;
    font-weight: 400 !important;
    padding: 0.42rem 0.8rem !important;
    width: 100% !important;
    transition: all 0.12s !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1A1A1A !important;
    color: #D4D0C8 !important;
    border: none !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Clash Display', 'Outfit', sans-serif !important;
    color: #EEEADF !important;
    letter-spacing: -0.025em !important;
    font-weight: 600 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    color: #EEEADF !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 0.875rem !important;
    transition: border-color 0.15s !important;
    caret-color: #E8A838;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: #3A3A3A !important; }
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #E8A838 !important;
    box-shadow: 0 0 0 3px rgba(232,168,56,0.1) !important;
    outline: none !important;
}
.stTextInput > label, .stTextArea > label,
.stSelectbox > label, .stMultiSelect > label, .stDateInput > label {
    color: #444 !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
    color: #EEEADF !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #E8A838 !important;
    box-shadow: 0 0 0 3px rgba(232,168,56,0.1) !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    color: #888 !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.12s ease !important;
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: #222 !important;
    border-color: #333 !important;
    color: #EEEADF !important;
}
.stButton > button[kind="primary"] {
    background: #E8A838 !important;
    border-color: #E8A838 !important;
    color: #141414 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 16px rgba(232,168,56,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #F0B84A !important;
    border-color: #F0B84A !important;
    box-shadow: 0 4px 24px rgba(232,168,56,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #222 !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #444 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    margin-bottom: -1px !important;
    letter-spacing: 0.01em;
}
.stTabs [aria-selected="true"] {
    color: #E8A838 !important;
    border-bottom: 2px solid #E8A838 !important;
    font-weight: 600 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #888 !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: #181818 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    padding: 0.875rem 1rem !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatInput"] > div {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #E8A838 !important;
    box-shadow: 0 0 0 3px rgba(232,168,56,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #EEEADF !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: #181818 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    padding: 1.25rem !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; font-family: 'Outfit', sans-serif !important; font-size: 0.85rem !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #181818 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #555 !important;
    font-size: 0.82rem !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stExpander"] summary:hover { color: #888 !important; }

/* ── Date input ── */
.stDateInput > div > div > input {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    color: #EEEADF !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid #222 !important; margin: 0.75rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #E8A838; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #E8A838 !important; }

/* ── Gap fix ── */
[data-testid="stVerticalBlock"] { gap: 0.5rem; }
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Topbar ─────────────────────────────────────────────────────────────────────

def render_topbar(user_name: str, room_name: str = None, subgroup_name: str = None):
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    crumb = ""
    if room_name:
        crumb += f'<span style="color:#2A2A2A;margin:0 0.5rem;">/</span><span style="color:#666;font-size:0.82rem;">{room_name}</span>'
    if subgroup_name:
        crumb += f'<span style="color:#2A2A2A;margin:0 0.5rem;">/</span><span style="color:#E8A838;font-size:0.82rem;">{subgroup_name}</span>'

    st.markdown(f"""
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding: 0 2rem; height: 54px;
        background: #0F0F0F;
        border-bottom: 1px solid #1E1E1E;
        margin-bottom: 2rem;
    ">
        <div style="display:flex; align-items:center; font-family:'Outfit',sans-serif;">
            <span style="
                font-family:'Clash Display','Outfit',sans-serif;
                font-size:1rem; font-weight:700;
                color:#E8A838; letter-spacing:-0.02em;
                margin-right:0.25rem;
            ">sankalproom</span>
            {crumb}
        </div>
        <div style="display:flex; align-items:center; gap:0.625rem;">
            <div style="
                width:30px; height:30px; border-radius:8px;
                background:#E8A838;
                display:flex; align-items:center; justify-content:center;
                font-size:0.65rem; font-weight:700; color:#141414;
                font-family:'Clash Display','Outfit',sans-serif;
                letter-spacing:0.02em;
            ">{initials}</div>
            <span style="color:#444; font-size:0.8rem; font-family:'Outfit',sans-serif;">{user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Stat cards ──────────────────────────────────────────────────────────────────

def render_stat_cards(stats: list):
    cols = st.columns(len(stats))
    for i, s in enumerate(cols):
        st_data = stats[i]
        with s:
            st.markdown(f"""
            <div style="
                background: #181818;
                border: 1px solid #222;
                border-radius: 10px;
                padding: 1.1rem 1.25rem 1rem;
                margin-bottom: 1.25rem;
            ">
                <div style="
                    font-family:'Clash Display','Outfit',sans-serif;
                    font-size:1.75rem; font-weight:700; line-height:1;
                    color:{st_data.get('color','#E8A838')};
                    margin-bottom:0.35rem;
                    letter-spacing:-0.03em;
                ">{st_data['value']}</div>
                <div style="
                    color:#444; font-size:0.72rem; font-weight:500;
                    text-transform:uppercase; letter-spacing:0.08em;
                    font-family:'Outfit',sans-serif;
                ">{st_data['label']}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Member avatars ──────────────────────────────────────────────────────────────

def render_member_avatars(members: list, max_show: int = 8):
    avs = ""
    for m in members[:max_show]:
        c   = m.get("avatar_color", "#E8A838")
        ini = "".join(w[0].upper() for w in m["name"].split()[:2])
        avs += f"""<div title="{m['name']}" style="
            width:28px; height:28px; border-radius:6px;
            background:{c}; color:#141414;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.6rem; font-weight:700;
            border:2px solid #141414;
            margin-right:-6px;
            font-family:'Outfit',sans-serif;
        ">{ini}</div>"""
    if len(members) > max_show:
        avs += f"""<div style="
            width:28px; height:28px; border-radius:6px;
            background:#222; color:#555;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:0.6rem; font-weight:600;
            border:2px solid #141414;
            margin-right:-6px;
        ">+{len(members)-max_show}</div>"""
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:0.625rem;">{avs}</div>', unsafe_allow_html=True)


# ── Empty state ─────────────────────────────────────────────────────────────────

def render_empty_state(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div style="
        text-align:center; padding: 3rem 1rem;
        border: 1px dashed #222; border-radius: 10px; margin: 0.5rem 0;
    ">
        <div style="font-size:1.75rem; margin-bottom:0.75rem; opacity:0.3;">{icon}</div>
        <div style="
            font-family:'Clash Display','Outfit',sans-serif;
            font-size:0.88rem; font-weight:600;
            color:#333; margin-bottom:0.3rem;
        ">{title}</div>
        <div style="color:#2A2A2A; font-size:0.77rem;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Invite pill ─────────────────────────────────────────────────────────────────

def render_invite_pill(code: str):
    st.markdown(f"""
    <div style="
        display:inline-flex; align-items:center; gap:0.75rem;
        background:#181818; border:1px solid #2A2A2A;
        border-radius:8px; padding:0.5rem 1rem;
    ">
        <span style="
            color:#333; font-size:0.68rem; font-weight:600;
            text-transform:uppercase; letter-spacing:0.1em;
            font-family:'Outfit',sans-serif;
        ">invite</span>
        <span style="
            font-family:'Clash Display','Outfit',sans-serif;
            font-size:1rem; font-weight:700;
            color:#E8A838; letter-spacing:0.15em;
        ">{code}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Section header ──────────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <div style="
            font-family:'Clash Display','Outfit',sans-serif;
            font-size:0.95rem; font-weight:600;
            color:#EEEADF; letter-spacing:-0.01em;
        ">{title}</div>
        {'<div style="color:#3A3A3A;font-size:0.77rem;margin-top:0.2rem;font-family:Outfit,sans-serif;">'+subtitle+'</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


# ── Inline badge ────────────────────────────────────────────────────────────────

def render_badge(text: str, color: str = "#E8A838"):
    st.markdown(f"""
    <span style="
        background:{color}18; color:{color};
        border:1px solid {color}30;
        border-radius:4px; padding:2px 8px;
        font-size:0.68rem; font-weight:600;
        font-family:'Outfit',sans-serif;
        letter-spacing:0.05em; text-transform:uppercase;
    ">{text}</span>
    """, unsafe_allow_html=True)
