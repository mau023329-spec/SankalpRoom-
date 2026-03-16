"""
SankalpRoom - Authentication Module

CHANGE 2: Profile photo stored as base64 in DB. update_profile_photo() saves it.
CHANGE 3: update_username() lets users rename themselves.
CHANGE 7: Login state is persisted via a session token stored in the DB AND in
          st.query_params so a hard browser refresh does NOT log the user out.
          Token is set in the URL (?token=...) on login and validated on every load.
"""

import base64
import hashlib
import secrets
import streamlit as st
from database.db import fetchone, execute


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Register / Login ──────────────────────────────────────────────────────────

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


# ── CHANGE 3: Update username ─────────────────────────────────────────────────

def update_username(user_id: int, new_name: str) -> tuple:
    """Allow a user to change their display name."""
    new_name = new_name.strip()
    if not new_name:
        return False, "Name cannot be empty."
    if len(new_name) > 60:
        return False, "Name is too long (max 60 characters)."
    execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    # Refresh session name immediately
    st.session_state["user_name"] = new_name
    return True, None


# ── CHANGE 2: Profile photo ───────────────────────────────────────────────────

def update_profile_photo(user_id: int, uploaded_file) -> tuple:
    """
    Save an uploaded profile photo as a base64 string in the users table.
    The column is  profile_photo TEXT  (added in the DB schema below).
    """
    if uploaded_file is None:
        return False, "No file provided."
    raw   = uploaded_file.read()
    if len(raw) > 2 * 1024 * 1024:   # 2 MB cap
        return False, "Image too large — max 2 MB."
    mime  = uploaded_file.type or "image/png"
    b64   = base64.b64encode(raw).decode()
    data_uri = f"data:{mime};base64,{b64}"
    execute("UPDATE users SET profile_photo = ? WHERE id = ?", (data_uri, user_id))
    st.session_state["user_photo"] = data_uri
    return True, None


def get_profile_photo(user_id: int) -> str:
    """Return the data-URI for a user's profile photo, or empty string."""
    row = fetchone("SELECT profile_photo FROM users WHERE id = ?", (user_id,))
    return (row or {}).get("profile_photo") or ""


# ── CHANGE 7: Session token (survive hard refresh) ────────────────────────────

def _create_session_token(user_id: int) -> str:
    """
    Generate a secure random token, store it in the DB, and return it.
    The token is placed in st.query_params so it survives a browser refresh.
    """
    token = secrets.token_urlsafe(32)
    execute(
        "INSERT INTO session_tokens (user_id, token) VALUES (?, ?)",
        (user_id, token),
    )
    return token


def _validate_session_token(token: str):
    """Return the user row if the token is valid, else None."""
    if not token:
        return None
    row = fetchone(
        "SELECT u.* FROM users u "
        "JOIN session_tokens st ON u.id = st.user_id "
        "WHERE st.token = ?",
        (token,),
    )
    return row


def _delete_session_token(token: str):
    if token:
        execute("DELETE FROM session_tokens WHERE token = ?", (token,))


# ── Session helpers ───────────────────────────────────────────────────────────

def set_session(user: dict, create_token: bool = True):
    st.session_state["user_id"]    = user["id"]
    st.session_state["user_name"]  = user["name"]
    st.session_state["user_email"] = user.get("email", "")
    st.session_state["user_color"] = user.get("avatar_color", "#E8A838")
    # CHANGE 2: load profile photo into session
    st.session_state["user_photo"] = user.get("profile_photo") or ""
    # CHANGE 7: create and store token in URL
    if create_token:
        token = _create_session_token(user["id"])
        st.session_state["_session_token"] = token
        try:
            st.query_params["token"] = token
        except Exception:
            pass   # query_params not writable in older Streamlit — silently skip


def logout():
    # CHANGE 7: delete token from DB on explicit logout
    token = st.session_state.get("_session_token")
    _delete_session_token(token)
    for key in [
        "user_id","user_name","user_email","user_color","user_photo",
        "current_room","current_subgroup","_session_token",
    ]:
        st.session_state.pop(key, None)
    # Remove token from URL
    try:
        st.query_params.clear()
    except Exception:
        pass


def is_logged_in() -> bool:
    """
    CHANGE 7: First check session_state (fast path).
    If not present (e.g. after hard refresh), check the ?token= query param
    and restore the session from DB if valid.
    """
    if "user_id" in st.session_state:
        return True

    # Try to restore from URL token
    try:
        token = st.query_params.get("token", "")
    except Exception:
        token = ""

    if token:
        user = _validate_session_token(token)
        if user:
            set_session(user, create_token=False)   # don't create a new token
            st.session_state["_session_token"] = token
            return True

    return False


# ── Auth page ─────────────────────────────────────────────────────────────────

def render_auth_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    *, *::before, *::after { box-sizing: border-box; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #080A0F !important; color: #CBD5E1; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top:0 !important; padding-left:1rem !important; padding-right:1rem !important; max-width:100% !important; }

    .stTextInput > div > div > input {
        background:#0F1218 !important; border:1px solid #1E2533 !important;
        color:#E2E8F0 !important; border-radius:8px !important;
        font-family:'Inter',sans-serif !important;
        font-size:16px !important;
        padding:0.75rem 1rem !important; min-height:48px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color:#6366F1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important;
    }
    .stTextInput > label {
        color:#64748B !important; font-size:0.72rem !important; font-weight:600 !important;
        text-transform:uppercase !important; letter-spacing:0.06em !important;
    }
    .stButton > button {
        background:#0F1218 !important; border:1px solid #1E2533 !important;
        color:#94A3B8 !important; border-radius:8px !important;
        font-family:'Inter',sans-serif !important; font-weight:500 !important;
        min-height:48px !important; font-size:0.9rem !important; width:100% !important;
    }
    .stButton > button[kind="primary"] {
        background:#6366F1 !important; border-color:#6366F1 !important;
        color:#fff !important; font-weight:600 !important;
        box-shadow:0 2px 16px rgba(99,102,241,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover { background:#4F52D9 !important; }

    .stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:1px solid #1C2030 !important; }
    .stTabs [data-baseweb="tab"] {
        background:transparent !important; color:#475569 !important;
        font-family:'Inter',sans-serif !important; font-size:0.85rem !important;
        font-weight:500 !important; padding:0.7rem 1.25rem !important;
        min-height:44px !important; border-bottom:2px solid transparent !important;
        border-radius:0 !important; margin-bottom:-1px !important;
    }
    .stTabs [aria-selected="true"] {
        color:#6366F1 !important; border-bottom:2px solid #6366F1 !important;
        font-weight:600 !important; background:transparent !important;
    }
    .stAlert { border-radius:8px !important; font-family:'Inter',sans-serif !important; }

    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction:column !important; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { width:100% !important; min-width:100% !important; }
        .auth-brand { display:none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('''
        <div class="auth-brand" style="min-height:60vh;background:#0C0E14;
            border-right:1px solid #1C2030;display:flex;flex-direction:column;
            justify-content:center;padding:3rem 2.5rem;">
            <div style="margin-bottom:2.5rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;
                    font-weight:600;color:#6366F1;letter-spacing:0.15em;
                    text-transform:uppercase;margin-bottom:1.5rem;">⚡ SankalpRoom</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;
                    font-weight:700;color:#F1F5F9;letter-spacing:-0.04em;
                    line-height:1.1;margin-bottom:1rem;">Where ideas<br>become action.</div>
                <div style="color:#475569;font-size:0.875rem;line-height:1.7;
                    font-family:'Inter',sans-serif;max-width:300px;">
                    Discuss as a team, vote on what matters,
                    then execute in focused subgroups.
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.875rem;">
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;margin-top:2px;">💡</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;margin-bottom:0.1rem;">Brainstorm together</div>
                        <div style="font-size:0.75rem;color:#334155;">Submit ideas, vote with 👍🔥⏳, surface what matters.</div>
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;margin-top:2px;">🤖</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;margin-bottom:0.1rem;">AI that actually helps</div>
                        <div style="font-size:0.75rem;color:#334155;">Groq-powered analysis, clustering, task breakdown.</div>
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;margin-top:2px;">⚙️</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;margin-bottom:0.1rem;">Execute in subgroups</div>
                        <div style="font-size:0.75rem;color:#334155;">Kanban boards, task ownership, deadlines.</div>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with right:
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        _, form_col, _ = st.columns([1, 10, 1])
        with form_col:
            st.markdown("""
            <div style="margin-bottom:1.5rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;
                    font-weight:700;color:#F1F5F9;letter-spacing:-0.025em;margin-bottom:0.3rem;">
                    Get started</div>
                <div style="color:#475569;font-size:0.82rem;font-family:'Inter',sans-serif;">
                    Sign in or create your account.</div>
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
