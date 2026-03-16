"""
SankalpRoom - Authentication Module

CHANGE 2: Profile photo stored as base64 in DB.
CHANGE 3: update_username() lets users rename themselves.
CHANGE 7: Login state persisted via session token in DB + st.query_params.
CHANGE 9: Email is now optional at signup.
          Login accepts either email OR username + password.
          Usernames must be unique so they can be used as a login identifier.
"""

import base64
import hashlib
import secrets
import streamlit as st
from database.db import fetchone, execute


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Register ──────────────────────────────────────────────────────────────────

def register_user(name: str, password: str, email: str = ""):
    """
    CHANGE 9: email is now optional.
    - name (username) is always required and must be unique.
    - If email is provided it must also be unique.
    """
    name = name.strip()
    email = email.strip().lower()

    # Username must be unique (we use it as a login identifier)
    if fetchone("SELECT id FROM users WHERE LOWER(name) = LOWER(?)", (name,)):
        return None, "Username already taken — choose another."

    # Email uniqueness check only when an email is actually provided
    if email:
        if fetchone("SELECT id FROM users WHERE LOWER(email) = ?", (email,)):
            return None, "Email already registered."

    colors = ["#E8A838","#E86F3A","#6366F1","#22C55E","#EC4899","#06B6D4","#8B5CF6"]
    # Store NULL when no email given so the unique constraint doesn't block
    # multiple no-email accounts
    user_id = execute(
        "INSERT INTO users (name, email, password_hash, avatar_color) VALUES (?, ?, ?, ?)",
        (name, email if email else None, hash_password(password), secrets.choice(colors)),
    )
    return user_id, None


# ── Login ─────────────────────────────────────────────────────────────────────

def login_user(identifier: str, password: str):
    """
    CHANGE 9: identifier can be either email or username.
    Tries email first, then falls back to username match.
    """
    identifier = identifier.strip()
    pw_hash    = hash_password(password)

    # Try as email first (only if it looks like an email)
    if "@" in identifier:
        user = fetchone(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?) AND password_hash = ?",
            (identifier, pw_hash),
        )
        if user:
            return user, None

    # Try as username (case-insensitive)
    user = fetchone(
        "SELECT * FROM users WHERE LOWER(name) = LOWER(?) AND password_hash = ?",
        (identifier, pw_hash),
    )
    if user:
        return user, None

    return None, "Invalid username / email or password."


def get_user(user_id: int):
    return fetchone("SELECT * FROM users WHERE id = ?", (user_id,))


# ── CHANGE 3: Update username ─────────────────────────────────────────────────

def update_username(user_id: int, new_name: str) -> tuple:
    """Allow a user to change their display name. New name must be unique."""
    new_name = new_name.strip()
    if not new_name:
        return False, "Name cannot be empty."
    if len(new_name) > 60:
        return False, "Name is too long (max 60 characters)."
    # Make sure no one else already has this name
    existing = fetchone(
        "SELECT id FROM users WHERE LOWER(name) = LOWER(?) AND id != ?",
        (new_name, user_id),
    )
    if existing:
        return False, "Username already taken — choose another."
    execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    st.session_state["user_name"] = new_name
    return True, None


# ── CHANGE 2: Profile photo ───────────────────────────────────────────────────

def update_profile_photo(user_id: int, uploaded_file) -> tuple:
    if uploaded_file is None:
        return False, "No file provided."
    raw = uploaded_file.read()
    if len(raw) > 2 * 1024 * 1024:
        return False, "Image too large — max 2 MB."
    mime     = uploaded_file.type or "image/png"
    b64      = base64.b64encode(raw).decode()
    data_uri = f"data:{mime};base64,{b64}"
    execute("UPDATE users SET profile_photo = ? WHERE id = ?", (data_uri, user_id))
    st.session_state["user_photo"] = data_uri
    return True, None


def get_profile_photo(user_id: int) -> str:
    row = fetchone("SELECT profile_photo FROM users WHERE id = ?", (user_id,))
    return (row or {}).get("profile_photo") or ""


# ── CHANGE 7: Session token (survive hard refresh) ────────────────────────────

def _create_session_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    execute(
        "INSERT INTO session_tokens (user_id, token) VALUES (?, ?)",
        (user_id, token),
    )
    return token


def _validate_session_token(token: str):
    if not token:
        return None
    return fetchone(
        "SELECT u.* FROM users u "
        "JOIN session_tokens st ON u.id = st.user_id "
        "WHERE st.token = ?",
        (token,),
    )


def _delete_session_token(token: str):
    if token:
        execute("DELETE FROM session_tokens WHERE token = ?", (token,))


# ── Session helpers ───────────────────────────────────────────────────────────

def set_session(user: dict, create_token: bool = True):
    st.session_state["user_id"]    = user["id"]
    st.session_state["user_name"]  = user["name"]
    st.session_state["user_email"] = user.get("email") or ""
    st.session_state["user_color"] = user.get("avatar_color", "#E8A838")
    st.session_state["user_photo"] = user.get("profile_photo") or ""
    if create_token:
        token = _create_session_token(user["id"])
        st.session_state["_session_token"] = token
        try:
            st.query_params["token"] = token
        except Exception:
            pass


def logout():
    token = st.session_state.get("_session_token")
    _delete_session_token(token)
    for key in [
        "user_id","user_name","user_email","user_color","user_photo",
        "current_room","current_subgroup","_session_token",
    ]:
        st.session_state.pop(key, None)
    try:
        st.query_params.clear()
    except Exception:
        pass


def is_logged_in() -> bool:
    if "user_id" in st.session_state:
        return True
    try:
        token = st.query_params.get("token", "")
    except Exception:
        token = ""
    if token:
        user = _validate_session_token(token)
        if user:
            set_session(user, create_token=False)
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

            # ── SIGN IN ───────────────────────────────────────────────────────
            with tab_in:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                # CHANGE 9: label updated — accepts username OR email
                with st.form("lf"):
                    identifier = st.text_input(
                        "Username or Email",
                        placeholder="your_username  or  you@example.com",
                    )
                    pw = st.text_input("Password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
                    if st.form_submit_button("Sign in →", type="primary", use_container_width=True):
                        if not identifier or not pw:
                            st.error("Fill in all fields.")
                        else:
                            # CHANGE 9: login_user now accepts username or email
                            user, err = login_user(identifier, pw)
                            if err: st.error(err)
                            else: set_session(user); st.rerun()

            # ── CREATE ACCOUNT ────────────────────────────────────────────────
            with tab_up:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                # CHANGE 9: email is optional — clearly labelled
                with st.form("rf"):
                    name  = st.text_input("Username *", placeholder="e.g. alex_j  (required, used to log in)")
                    email2 = st.text_input(
                        "Email  (optional)",
                        placeholder="you@example.com  — leave blank if you prefer",
                    )
                    # Small note explaining email is optional
                    st.markdown(
                        '<div style="color:#475569;font-size:0.72rem;font-family:Inter,sans-serif;'
                        'margin-top:-0.5rem;margin-bottom:0.5rem;">'
                        '⚠️ No email = no password recovery. Remember your password!</div>',
                        unsafe_allow_html=True,
                    )
                    pw2  = st.text_input("Password *", type="password", placeholder="Min 6 characters")
                    pw2c = st.text_input("Confirm password *", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
                    if st.form_submit_button("Create account →", type="primary", use_container_width=True):
                        # CHANGE 9: only name and password are required
                        if not name or not pw2 or not pw2c:
                            st.error("Username and password are required.")
                        elif pw2 != pw2c:
                            st.error("Passwords don't match.")
                        elif len(pw2) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            uid, err = register_user(name, pw2, email=email2)
                            if err:
                                st.error(err)
                            else:
                                # Log in immediately after registering
                                user, _ = login_user(name, pw2)
                                set_session(user)
                                st.rerun()
