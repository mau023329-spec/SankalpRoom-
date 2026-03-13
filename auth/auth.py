"""
SankalpRoom - Authentication Module
Handles user registration, login, and session management.
"""

import hashlib
import secrets
import streamlit as st
from database.db import fetchone, execute


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str):
    existing = fetchone("SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        return None, "Email already registered."
    pw_hash = hash_password(password)
    avatar_colors = ["#4F46E5", "#8B5CF6", "#EC4899", "#06B6D4", "#22C55E", "#F59E0B"]
    color = secrets.choice(avatar_colors)
    user_id = execute(
        "INSERT INTO users (name, email, password_hash, avatar_color) VALUES (?, ?, ?, ?)",
        (name, email, pw_hash, color),
    )
    return user_id, None


def login_user(email: str, password: str):
    pw_hash = hash_password(password)
    user = fetchone(
        "SELECT * FROM users WHERE email = ? AND password_hash = ?",
        (email, pw_hash),
    )
    if not user:
        return None, "Invalid email or password."
    return user, None


def get_user(user_id: int):
    return fetchone("SELECT * FROM users WHERE id = ?", (user_id,))


def logout():
    for key in ["user_id", "user_name", "user_email", "user_color", "current_room", "current_subgroup"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return "user_id" in st.session_state


def set_session(user: dict):
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["name"]
    st.session_state["user_email"] = user["email"]
    st.session_state["user_color"] = user.get("avatar_color", "#4F46E5")


def render_auth_page():
    """Render the login/register page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    .auth-hero {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .auth-logo {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    .auth-tagline {
        font-family: 'DM Sans', sans-serif;
        color: #6B7280;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    </style>
    <div class="auth-hero">
        <div class="auth-logo">⚡ SankalpRoom</div>
        <div class="auth-tagline">Where ideas become decisions, and decisions become action.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        user, err = login_user(email, password)
                        if err:
                            st.error(err)
                        else:
                            set_session(user)
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()

        with tab_register:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Alex Johnson")
                email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="reg_pw")
                confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")
                if submitted:
                    if not all([name, email, password, confirm]):
                        st.error("Please fill in all fields.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        user_id, err = register_user(name, email, password)
                        if err:
                            st.error(err)
                        else:
                            user, _ = login_user(email, password)
                            set_session(user)
                            st.success("Account created! Welcome to SankalpRoom!")
                            st.rerun()
