"""
SankalpRoom - Authentication Module
Session persistence via URL query param ?t=TOKEN + DB validation.
- On login: token written to DB + set in st.query_params (stays in URL)
- On refresh: token is still in URL → validated against DB → session restored
- On logout: token deleted from DB + removed from URL
No extra packages. Works on Streamlit Cloud.
"""

import hashlib
import secrets as _secrets
import streamlit as st
from database.db import fetchone, execute


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


# ══════════════════════════════════════════════════════════════════
# USER CRUD
# ══════════════════════════════════════════════════════════════════

def register_user(name: str, email: str, password: str):
    email = (email or "").strip()
    if email and fetchone("SELECT id FROM users WHERE email=?", (email,)):
        return None, "Email already registered."
    if fetchone("SELECT id FROM users WHERE name=?", (name.strip(),)):
        return None, "That display name is already taken."
    colors = ["#E8A838","#E86F3A","#6366F1","#22C55E","#EC4899","#06B6D4","#8B5CF6"]
    uid = execute(
        "INSERT INTO users (name,email,password_hash,avatar_color) VALUES (?,?,?,?)",
        (name.strip(), email or None, hash_password(password), _secrets.choice(colors)),
    )
    return uid, None


def login_user(identifier: str, password: str):
    """Login by email OR display name."""
    identifier = (identifier or "").strip()
    ph = hash_password(password)
    user = (
        fetchone("SELECT * FROM users WHERE email=? AND password_hash=?", (identifier, ph))
        or fetchone("SELECT * FROM users WHERE name=? AND password_hash=?", (identifier, ph))
    )
    return (user, None) if user else (None, "Invalid email/username or password.")


def get_user(user_id: int):
    return fetchone("SELECT * FROM users WHERE id=?", (user_id,))


# ══════════════════════════════════════════════════════════════════
# TOKEN DB
# ══════════════════════════════════════════════════════════════════

def _create_token(user_id: int) -> str:
    token = _secrets.token_urlsafe(32)
    try:
        execute("DELETE FROM session_tokens WHERE user_id=?", (user_id,))
    except Exception:
        pass
    execute(
        "INSERT INTO session_tokens (user_id, token) VALUES (?,?)",
        (user_id, token),
    )
    return token


def _validate_token(token: str):
    if not token or len(token) < 10:
        return None
    return fetchone("""
        SELECT u.* FROM session_tokens st
        JOIN users u ON u.id = st.user_id
        WHERE st.token = ?
    """, (token,))


# ══════════════════════════════════════════════════════════════════
# SESSION API
# ══════════════════════════════════════════════════════════════════

def _populate_session(user: dict):
    st.session_state["user_id"]         = user["id"]
    st.session_state["user_name"]       = user["name"]
    st.session_state["user_email"]      = user.get("email", "") or ""
    st.session_state["user_color"]      = user.get("avatar_color", "#6366F1")
    st.session_state["user_avatar_url"] = user.get("avatar_url") or None


def set_session(user: dict):
    """Call after successful login/register."""
    _populate_session(user)
    token = _create_token(user["id"])
    # Store token in URL — survives page refresh
    try:
        st.query_params["t"] = token
    except Exception:
        pass


def is_logged_in() -> bool:
    return "user_id" in st.session_state


def try_restore_session() -> bool:
    """
    Call at the very top of every page load.
    Reads ?t= from URL, validates against DB, restores session if valid.
    Returns True if user is now logged in.
    """
    if is_logged_in():
        return True

    # Read token from URL query param (persists through refresh automatically)
    token = (st.query_params.get("t") or "").strip()
    if not token:
        return False

    user = _validate_token(token)
    if user:
        _populate_session(user)
        return True

    # Token invalid/expired — remove it from URL silently
    try:
        st.query_params.pop("t", None)
    except Exception:
        pass
    return False


def logout():
    user_id = st.session_state.get("user_id")
    if user_id:
        try:
            execute("DELETE FROM session_tokens WHERE user_id=?", (user_id,))
        except Exception:
            pass
    # Remove token from URL
    try:
        params = {k: v for k, v in st.query_params.items() if k != "t"}
        st.query_params.clear()
        for k, v in params.items():
            st.query_params[k] = v
    except Exception:
        pass
    for key in ["user_id","user_name","user_email","user_color",
                "user_avatar_url","current_room","current_subgroup"]:
        st.session_state.pop(key, None)


# ══════════════════════════════════════════════════════════════════
# AUTH PAGE UI
# ══════════════════════════════════════════════════════════════════

def render_auth_page():
    params      = st.query_params
    invite_code = (params.get("invite", "") or "").strip().upper()
    if invite_code:
        st.session_state["pending_invite"] = invite_code

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    *, *::before, *::after { box-sizing: border-box; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #080A0F !important; color: #CBD5E1; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top:0 !important; padding-left:1rem !important;
        padding-right:1rem !important; max-width:100% !important;
    }
    .stTextInput > div > div > input {
        background:#0F1218 !important; border:1px solid #1E2533 !important;
        color:#E2E8F0 !important; border-radius:8px !important;
        font-family:'Inter',sans-serif !important; font-size:16px !important;
        padding:0.75rem 1rem !important; min-height:48px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color:#6366F1 !important;
        box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important;
    }
    .stTextInput > label {
        color:#64748B !important; font-size:0.72rem !important;
        font-weight:600 !important; text-transform:uppercase !important;
        letter-spacing:0.06em !important;
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
    .stTabs [data-baseweb="tab-list"] {
        background:transparent !important; border-bottom:1px solid #1C2030 !important;
    }
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
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width:100% !important; min-width:100% !important;
        }
        .auth-brand { display:none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    pending = st.session_state.get("pending_invite","")
    if pending:
        st.markdown(
            f'<div style="background:#6366F118;border:1px solid #6366F140;'
            f'border-radius:10px;padding:0.875rem 1.1rem;margin-bottom:1rem;'
            f'display:flex;align-items:center;gap:0.75rem;">'
            f'<span style="font-size:1.2rem;">🔗</span>'
            f'<div><div style="font-family:Space Grotesk,sans-serif;font-size:0.88rem;'
            f'font-weight:700;color:#F1F5F9;">You were invited to a room!</div>'
            f'<div style="font-size:0.75rem;color:#64748B;">Sign in or create an account to join.</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1, 1])

    with left:
        st.markdown('''
        <div class="auth-brand" style="min-height:60vh;background:#0C0E14;
            border-right:1px solid #1C2030;display:flex;flex-direction:column;
            justify-content:center;padding:3rem 2.5rem;">
            <div style="margin-bottom:2.5rem;">
                <div style="font-family:\'Space Grotesk\',sans-serif;font-size:0.75rem;
                    font-weight:600;letter-spacing:0.15em;text-transform:uppercase;
                    margin-bottom:1.5rem;background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">⚡ SankalpRoom</div>
                <div style="font-family:\'Space Grotesk\',sans-serif;font-size:2.2rem;
                    font-weight:700;color:#F1F5F9;letter-spacing:-0.04em;
                    line-height:1.1;margin-bottom:1rem;">Where ideas<br>become action.</div>
                <div style="color:#475569;font-size:0.875rem;line-height:1.7;max-width:300px;">
                    Discuss as a team, vote on what matters,
                    then execute in focused subgroups.
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.875rem;">
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;">💡</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;">Brainstorm together</div>
                        <div style="font-size:0.75rem;color:#334155;">Submit ideas, vote, surface what matters.</div>
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;">🤖</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;">AI that actually helps</div>
                        <div style="font-size:0.75rem;color:#334155;">Groq-powered analysis and task breakdown.</div>
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.875rem;">
                    <div style="width:30px;height:30px;border-radius:7px;background:#131720;
                        border:1px solid #1C2030;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;">⚙️</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#64748B;">Execute in subgroups</div>
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
                <div style="color:#475569;font-size:0.82rem;">Sign in or create your account.</div>
            </div>
            """, unsafe_allow_html=True)

            tab_in, tab_up = st.tabs(["Sign in", "Create account"])

            with tab_in:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                with st.form("lf"):
                    email = st.text_input("Email or display name",
                                          placeholder="you@example.com or YourName")
                    pw    = st.text_input("Password", type="password", placeholder="••••••••")
                    if st.form_submit_button("Sign in →", type="primary",
                                             use_container_width=True):
                        if not email or not pw:
                            st.error("Fill in all fields.")
                        else:
                            user, err = login_user(email, pw)
                            if err:
                                st.error(err)
                            else:
                                set_session(user)
                                st.rerun()

            with tab_up:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                with st.form("rf"):
                    name   = st.text_input("Full name *", placeholder="Alex Johnson")
                    email2 = st.text_input("Email (optional)", placeholder="you@example.com")
                    pw2    = st.text_input("Password *", type="password",
                                           placeholder="Min 6 characters")
                    pw2c   = st.text_input("Confirm password *", type="password",
                                           placeholder="••••••••")
                    st.markdown(
                        '<div style="color:#475569;font-size:0.72rem;margin-top:-0.25rem;">'
                        '* Required · Without email, log in using your display name.</div>',
                        unsafe_allow_html=True,
                    )
                    if st.form_submit_button("Create account →", type="primary",
                                             use_container_width=True):
                        if not all([name, pw2, pw2c]):
                            st.error("Name and password are required.")
                        elif pw2 != pw2c:
                            st.error("Passwords don't match.")
                        elif len(pw2) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            uid, err = register_user(name, email2, pw2)
                            if err:
                                st.error(err)
                            else:
                                login_id = email2.strip() if email2.strip() else name.strip()
                                user, _  = login_user(login_id, pw2)
                                set_session(user)
                                st.rerun()
