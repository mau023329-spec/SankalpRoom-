"""
SankalpRoom - Authentication Module
"""

import hashlib
import secrets
import streamlit as st
from database.db import fetchone, execute


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str):
    if fetchone("SELECT id FROM users WHERE email = ?", (email,)):
        return None, "Email already registered."
    colors = ["#E8A838","#E86F3A","#6366F1","#22C55E","#EC4899","#06B6D4","#8B5CF6"]
    user_id = execute(
        "INSERT INTO users (name, email, password_hash, avatar_color) VALUES (?, ?, ?, ?)",
        (name, email, hash_password(password), secrets.choice(colors)),
    )
    return user_id, None


def login_user(email: str, password: str):
    user = fetchone(
        "SELECT * FROM users WHERE email = ? AND password_hash = ?",
        (email, hash_password(password)),
    )
    return (user, None) if user else (None, "Invalid email or password.")


def get_user(user_id: int):
    return fetchone("SELECT * FROM users WHERE id = ?", (user_id,))


def logout():
    for key in ["user_id","user_name","user_email","user_color","current_room","current_subgroup"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return "user_id" in st.session_state


def set_session(user: dict):
    st.session_state["user_id"]    = user["id"]
    st.session_state["user_name"]  = user["name"]
    st.session_state["user_email"] = user.get("email", "")
    st.session_state["user_color"] = user.get("avatar_color", "#E8A838")


def render_auth_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    @import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap');

    .stApp { background: #0F0F0F !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0 !important; max-width: 100% !important; }

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; -webkit-font-smoothing: antialiased; }
    h1,h2,h3 { font-family: 'Clash Display','Outfit',sans-serif !important; color: #EEEADF !important; letter-spacing: -0.025em !important; }

    .stTextInput > div > div > input {
        background: #1A1A1A !important; border: 1px solid #2A2A2A !important;
        color: #EEEADF !important; border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important; caret-color: #E8A838;
    }
    .stTextInput > div > div > input:focus {
        border-color: #E8A838 !important; box-shadow: 0 0 0 3px rgba(232,168,56,0.12) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #333 !important; }
    .stTextInput > label { color: #444 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

    .stButton > button {
        background: #1A1A1A !important; border: 1px solid #2A2A2A !important;
        color: #888 !important; border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important; font-weight: 500 !important;
    }
    .stButton > button[kind="primary"] {
        background: #E8A838 !important; border-color: #E8A838 !important;
        color: #141414 !important; font-weight: 700 !important;
        box-shadow: 0 2px 20px rgba(232,168,56,0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #F0B84A !important; box-shadow: 0 4px 28px rgba(232,168,56,0.4) !important;
        transform: translateY(-1px) !important;
    }
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #222 !important; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; color: #444 !important; font-family: 'Outfit',sans-serif !important; font-size: 0.82rem !important; border-bottom: 2px solid transparent !important; border-radius: 0 !important; margin-bottom: -1px !important; }
    .stTabs [aria-selected="true"] { color: #E8A838 !important; border-bottom: 2px solid #E8A838 !important; font-weight: 600 !important; background: transparent !important; }
    .stAlert { border-radius: 8px !important; }
    ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

    # Full-height two-column layout
    left, right = st.columns([1, 1])

    with left:
        st.markdown("""
        <div style="
            height: 100vh; min-height: 600px;
            background: #0A0A0A;
            border-right: 1px solid #1A1A1A;
            display: flex; flex-direction: column;
            justify-content: center;
            padding: 4rem 3.5rem;
        ">
            <div style="margin-bottom:3rem;">
                <div style="
                    font-family:'Clash Display','Outfit',sans-serif;
                    font-size:0.75rem; font-weight:600;
                    color:#E8A838; letter-spacing:0.15em;
                    text-transform:uppercase;
                    margin-bottom:1.5rem;
                ">⚡ sankalproom</div>
                <div style="
                    font-family:'Clash Display','Outfit',sans-serif;
                    font-size:2.8rem; font-weight:700;
                    color:#EEEADF; letter-spacing:-0.04em;
                    line-height:1.05;
                    margin-bottom:1.25rem;
                ">Where ideas<br>become action.</div>
                <div style="
                    color:#444; font-size:0.9rem; line-height:1.7;
                    font-family:'Outfit',sans-serif; max-width:320px;
                ">
                    Brainstorm as a team, vote on what matters,<br>
                    then execute in focused subgroups.
                </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:0.875rem;">
                <div style="display:flex; align-items:flex-start; gap:0.875rem;">
                    <div style="width:28px;height:28px;border-radius:6px;background:#1A1A1A;border:1px solid #222;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.75rem;">💡</span>
                    </div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#888;margin-bottom:0.1rem;">Brainstorm together</div>
                        <div style="font-size:0.76rem;color:#333;">Submit ideas, vote with 👍🔥⏳, surface what matters.</div>
                    </div>
                </div>
                <div style="display:flex; align-items:flex-start; gap:0.875rem;">
                    <div style="width:28px;height:28px;border-radius:6px;background:#1A1A1A;border:1px solid #222;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.75rem;">🤖</span>
                    </div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#888;margin-bottom:0.1rem;">AI that actually helps</div>
                        <div style="font-size:0.76rem;color:#333;">Groq-powered analysis, clustering, task breakdown.</div>
                    </div>
                </div>
                <div style="display:flex; align-items:flex-start; gap:0.875rem;">
                    <div style="width:28px;height:28px;border-radius:6px;background:#1A1A1A;border:1px solid #222;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.75rem;">⚙️</span>
                    </div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#888;margin-bottom:0.1rem;">Execute in subgroups</div>
                        <div style="font-size:0.76rem;color:#333;">Kanban boards, task ownership, deadlines.</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div style="height:2.5rem;"></div>
        """, unsafe_allow_html=True)

        _, form_col, _ = st.columns([1, 6, 1])
        with form_col:
            st.markdown("""
            <div style="margin-bottom:1.75rem;">
                <div style="font-family:'Clash Display','Outfit',sans-serif;font-size:1.4rem;font-weight:700;color:#EEEADF;letter-spacing:-0.025em;margin-bottom:0.3rem;">Get started</div>
                <div style="color:#444;font-size:0.82rem;">Sign in or create your account below.</div>
            </div>
            """, unsafe_allow_html=True)

            tab_in, tab_up = st.tabs(["Sign in", "Create account"])

            with tab_in:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                with st.form("lf"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    pw    = st.text_input("Password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
                    if st.form_submit_button("Sign in →", type="primary", use_container_width=True):
                        if not email or not pw:
                            st.error("Fill in all fields.")
                        else:
                            user, err = login_user(email, pw)
                            if err: st.error(err)
                            else: set_session(user); st.rerun()

            with tab_up:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                with st.form("rf"):
                    name   = st.text_input("Full name", placeholder="Alex Johnson")
                    email2 = st.text_input("Email", placeholder="you@example.com")
                    pw2    = st.text_input("Password", type="password", placeholder="Min 6 characters")
                    pw2c   = st.text_input("Confirm password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
                    if st.form_submit_button("Create account →", type="primary", use_container_width=True):
                        if not all([name, email2, pw2, pw2c]):
                            st.error("Fill in all fields.")
                        elif pw2 != pw2c:
                            st.error("Passwords don't match.")
                        elif len(pw2) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            uid, err = register_user(name, email2, pw2)
                            if err: st.error(err)
                            else:
                                user, _ = login_user(email2, pw2)
                                set_session(user)
                                st.rerun()
