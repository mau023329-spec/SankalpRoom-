"""
SankalpRoom - Ideas Module
Extended with all 7 AI features.
"""

import streamlit as st
from database.db import fetchone, fetchall, execute

VOTE_TYPES   = {"👍": "like", "🔥": "high_priority", "⏳": "do_later"}
STATUSES     = ["Open", "Selected", "In Progress", "Dropped"]
STATUS_COLOR = {
    "Open":        "#6366F1",
    "Selected":    "#22C55E",
    "In Progress": "#F59E0B",
    "Dropped":     "#475569",
}


# ── Core DB functions ─────────────────────────────────────────────

def create_idea(room_id, user_id, title, desc=""):
    return execute(
        "INSERT INTO ideas(room_id,user_id,title,description) VALUES(?,?,?,?)",
        (room_id, user_id, title, desc),
    )


def update_idea_status(idea_id: int, status: str, user_id: int, room_id: int):
    """
    Update idea status. Auto-locks + saves memory when → Selected.
    Auto-saves memory when → Dropped.
    """
    from ai.ai_features import lock_idea, save_memory_event

    # Fetch current idea before update
    current = fetchone("SELECT * FROM ideas WHERE id=?", (idea_id,))
    if not current:
        return

    execute("UPDATE ideas SET status=?,updated_at=NOW() WHERE id=?", (status, idea_id))

    if status == "Selected" and not current.get("is_locked"):
        lock_idea(
            idea_id,
            current["title"],
            current.get("description", ""),
            room_id,
        )

    if status == "Dropped":
        save_memory_event(
            room_id, "dropped", idea_id,
            f"Dropped: '{current['title']}'.",
        )


def update_idea_text(idea_id: int, title: str, description: str, user_id: int):
    """Update idea title/description and save version history first."""
    from ai.ai_features import save_idea_version

    current = fetchone("SELECT title, description FROM ideas WHERE id=?", (idea_id,))
    if current:
        save_idea_version(idea_id, current["title"], current.get("description",""), user_id)

    execute(
        "UPDATE ideas SET title=?,description=?,updated_at=NOW() WHERE id=?",
        (title, description, idea_id),
    )


def get_idea_votes(idea_id):
    rows = fetchall(
        "SELECT vote_type,COUNT(*) as cnt FROM votes WHERE idea_id=? GROUP BY vote_type",
        (idea_id,),
    )
    r = {v: 0 for v in VOTE_TYPES.values()}
    for row in rows:
        r[row["vote_type"]] = row["cnt"]
    return r


def cast_vote(idea_id, user_id, vtype):
    ex = fetchone(
        "SELECT id,vote_type FROM votes WHERE idea_id=? AND user_id=?",
        (idea_id, user_id),
    )
    if ex:
        if ex["vote_type"] == vtype:
            execute("DELETE FROM votes WHERE idea_id=? AND user_id=?", (idea_id, user_id))
        else:
            execute(
                "UPDATE votes SET vote_type=? WHERE idea_id=? AND user_id=?",
                (vtype, idea_id, user_id),
            )
    else:
        execute(
            "INSERT INTO votes(idea_id,user_id,vote_type) VALUES(?,?,?)",
            (idea_id, user_id, vtype),
        )


def get_user_vote(idea_id, user_id):
    r = fetchone(
        "SELECT vote_type FROM votes WHERE idea_id=? AND user_id=?",
        (idea_id, user_id),
    )
    return r["vote_type"] if r else None


def get_room_ideas(room_id):
    ideas = fetchall(
        """SELECT i.*, u.name as author_name, u.avatar_color as author_color
           FROM ideas i JOIN users u ON i.user_id = u.id
           WHERE i.room_id = ? ORDER BY i.created_at DESC""",
        (room_id,),
    )
    for i in ideas:
        i["votes"]      = get_idea_votes(i["id"])
        i["vote_count"] = sum(i["votes"].values())
    return ideas


# ── Main panel ────────────────────────────────────────────────────

def render_ideas_panel(room_id: int, user_id: int):
    import html as _h
    from ai.ai_features import (
        compute_decision_score, save_decision_score,
        render_decision_score, render_lock_badge,
        render_version_history, render_alignment_check,
        render_heatmap_badge,
    )

    # ── Header ──────────────────────────────────────────────────
    col_h, col_btn = st.columns([3, 1])
    with col_h:
        st.markdown(
            '<div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;font-weight:700;'
            'color:#F1F5F9;margin-bottom:0.25rem;">💡 Ideas Board</div>'
            '<div style="color:#475569;font-size:0.76rem;font-family:Inter,sans-serif;">'
            'Submit, vote, and track ideas</div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("＋ Add idea", type="primary", use_container_width=True, key="add_idea_btn"):
            st.session_state["show_idea_form"] = not st.session_state.get("show_idea_form", False)

    if st.session_state.get("show_idea_form"):
        with st.form("nif", border=True):
            t = st.text_input("Idea title", placeholder="What's your idea?")
            d = st.text_area("Details (optional)", height=68)
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Submit", type="primary", use_container_width=True):
                    if t:
                        create_idea(room_id, user_id, t, d)
                        st.session_state["show_idea_form"] = False
                        st.rerun()
            with c2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_idea_form"] = False
                    st.rerun()

    # ── Filter + Sort ────────────────────────────────────────────
    fc, sc = st.columns([3, 1])
    with fc:
        sf = st.multiselect(
            "STATUS FILTER", STATUSES,
            default=["Open", "Selected", "In Progress"],
            label_visibility="collapsed",
            placeholder="Filter by status…",
        )
    with sc:
        sort = st.selectbox("SORT", ["Newest", "Most voted", "Highest impact"], label_visibility="collapsed")

    ideas    = get_room_ideas(room_id)
    filtered = [i for i in ideas if i["status"] in (sf or STATUSES)]

    if sort == "Most voted":
        filtered.sort(key=lambda x: x["vote_count"], reverse=True)
    elif sort == "Highest impact":
        filtered.sort(key=lambda x: (x.get("impact_score") or 0), reverse=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:3rem 1rem;border:1px dashed #1C2030;'
            'border-radius:10px;margin:0.75rem 0;">'
            '<div style="font-size:2rem;margin-bottom:0.75rem;opacity:0.35;">💡</div>'
            '<div style="color:#334155;font-size:0.82rem;font-family:Inter,sans-serif;">'
            'No ideas yet. Be the first to submit one.</div></div>',
            unsafe_allow_html=True,
        )
        return

    for idea in filtered:
        _render_idea_card(idea, user_id, room_id)


def _render_idea_card(idea: dict, user_id: int, room_id: int):
    import html as _h
    from ai.ai_features import (
        compute_decision_score, save_decision_score,
        render_decision_score, render_lock_badge,
        render_version_history, render_alignment_check,
        render_heatmap_badge,
    )

    status = idea.get("status", "Open")
    color  = STATUS_COLOR.get(status, "#6366F1")
    votes  = idea.get("votes", {})
    uv     = get_user_vote(idea["id"], user_id)
    is_locked = bool(idea.get("is_locked"))

    # ── Card container ──────────────────────────────────────────
    st.markdown(
        f'<div style="background:#0C0E14;border:1px solid #1C2030;border-radius:10px;'
        f'padding:1rem 1.1rem 0.875rem;margin-bottom:0.5rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.35rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'color:#E2E8F0;flex:1;margin-right:0.75rem;">{_h.escape(idea["title"])}</div>'
        f'<span style="color:{color};font-size:0.65rem;font-weight:600;font-family:Inter,sans-serif;'
        f'background:{color}12;border:1px solid {color}25;border-radius:4px;padding:2px 8px;'
        f'text-transform:uppercase;white-space:nowrap;">{status}</span>'
        f'</div>'
        + (f'<div style="color:#475569;font-size:0.76rem;font-family:Inter,sans-serif;margin-bottom:0.35rem;">'
           f'{_h.escape(idea.get("description",""))}</div>' if idea.get("description") else "")
        + f'<div style="color:#334155;font-size:0.68rem;font-family:Inter,sans-serif;">'
        f'{_h.escape(idea.get("author_name","?"))} · {str(idea.get("created_at",""))[:10]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Heatmap badge ────────────────────────────────────────────
    render_heatmap_badge(idea)

    # ── AI Decision Score ────────────────────────────────────────
    render_decision_score(idea)

    # ── Lock badge ───────────────────────────────────────────────
    render_lock_badge(idea)

    # ── Vote buttons + status selector ──────────────────────────
    if not is_locked:
        vc = st.columns([1, 1, 1, 2])
        for j, (emoji, vtype) in enumerate(VOTE_TYPES.items()):
            cnt   = votes.get(vtype, 0)
            voted = uv == vtype
            with vc[j]:
                if st.button(
                    f"{emoji} {cnt}{'✓' if voted else ''}",
                    key=f"v_{idea['id']}_{vtype}",
                    use_container_width=True,
                ):
                    cast_vote(idea["id"], user_id, vtype)
                    st.rerun()
        with vc[3]:
            ns = st.selectbox(
                "", STATUSES,
                index=STATUSES.index(status),
                key=f"s_{idea['id']}",
                label_visibility="collapsed",
            )
            if ns != status:
                update_idea_status(idea["id"], ns, user_id, room_id)
                st.rerun()
    else:
        # Locked ideas — show votes read-only, no status change
        vote_summary = " · ".join(
            f"{e} {votes.get(v,0)}"
            for e, v in VOTE_TYPES.items()
        )
        st.markdown(
            f'<div style="color:#334155;font-size:0.75rem;font-family:Inter,sans-serif;'
            f'padding:0.25rem 0;">{vote_summary}</div>',
            unsafe_allow_html=True,
        )

    # ── Expandable: AI tools ─────────────────────────────────────
    with st.expander("🤖 AI Tools", expanded=False):
        tab_score, tab_align, tab_hist = st.tabs(["Score", "Alignment", "History"])

        with tab_score:
            if idea.get("impact_score") is None:
                if st.button("⚡ Generate AI Score", key=f"score_{idea['id']}", use_container_width=True):
                    with st.spinner("Scoring…"):
                        result = compute_decision_score(idea["title"], idea.get("description",""))
                    save_decision_score(idea["id"], result["impact"], result["effort"], result["recommendation"])
                    st.rerun()
            else:
                st.markdown(f"**Reason:** {idea.get('ai_score_rec','')}")
                if st.button("♻️ Re-score", key=f"rescore_{idea['id']}", use_container_width=True):
                    with st.spinner("Re-scoring…"):
                        result = compute_decision_score(idea["title"], idea.get("description",""))
                    save_decision_score(idea["id"], result["impact"], result["effort"], result["recommendation"])
                    st.rerun()

        with tab_align:
            render_alignment_check(idea, room_id)

        with tab_hist:
            render_version_history(idea)

            # Edit idea (saves version first)
            if not is_locked:
                with st.form(f"edit_idea_{idea['id']}", border=False):
                    new_title = st.text_input("Title", value=idea["title"])
                    new_desc  = st.text_area("Description", value=idea.get("description",""), height=64)
                    if st.form_submit_button("Save changes", type="primary", use_container_width=True):
                        if new_title:
                            update_idea_text(idea["id"], new_title, new_desc, user_id)
                            st.success("Saved!")
                            st.rerun()
