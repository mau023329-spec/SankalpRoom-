"""
SankalpRoom - Ideas Module
"""

import streamlit as st
from database.db import fetchone, fetchall, execute

VOTE_TYPES   = {"👍": "like", "🔥": "high_priority", "⏳": "do_later"}
STATUSES     = ["Open", "Selected", "In Progress", "Dropped"]
STATUS_COLOR = {"Open":"#6366F1","Selected":"#22C55E","In Progress":"#E8A838","Dropped":"#333"}
STATUS_DOT   = {"Open":"◉","Selected":"◉","In Progress":"◉","Dropped":"◎"}


def create_idea(room_id, user_id, title, desc=""):
    return execute("INSERT INTO ideas(room_id,user_id,title,description) VALUES(?,?,?,?)", (room_id,user_id,title,desc))

def update_idea_status(idea_id, status):
    execute("UPDATE ideas SET status=?,updated_at=datetime('now') WHERE id=?", (status,idea_id))

def get_idea_votes(idea_id):
    rows = fetchall("SELECT vote_type,COUNT(*) as cnt FROM votes WHERE idea_id=? GROUP BY vote_type", (idea_id,))
    r = {v:0 for v in VOTE_TYPES.values()}
    for row in rows: r[row["vote_type"]] = row["cnt"]
    return r

def cast_vote(idea_id, user_id, vtype):
    ex = fetchone("SELECT id,vote_type FROM votes WHERE idea_id=? AND user_id=?", (idea_id,user_id))
    if ex:
        if ex["vote_type"] == vtype: execute("DELETE FROM votes WHERE idea_id=? AND user_id=?", (idea_id,user_id))
        else: execute("UPDATE votes SET vote_type=? WHERE idea_id=? AND user_id=?", (vtype,idea_id,user_id))
    else: execute("INSERT INTO votes(idea_id,user_id,vote_type) VALUES(?,?,?)", (idea_id,user_id,vtype))

def get_user_vote(idea_id, user_id):
    r = fetchone("SELECT vote_type FROM votes WHERE idea_id=? AND user_id=?", (idea_id,user_id))
    return r["vote_type"] if r else None

def get_room_ideas(room_id):
    ideas = fetchall("""
        SELECT i.*,u.name as author_name,u.avatar_color as author_color
        FROM ideas i JOIN users u ON i.user_id=u.id
        WHERE i.room_id=? ORDER BY i.created_at DESC
    """, (room_id,))
    for i in ideas:
        i["votes"] = get_idea_votes(i["id"])
        i["vote_count"] = sum(i["votes"].values())
    return ideas


def render_ideas_panel(room_id: int, user_id: int):
    from ui.components import render_empty_state, section_header

    col_h, col_btn = st.columns([3, 1])
    with col_h:
        section_header("Ideas Board", "Submit, vote, and track ideas")
    with col_btn:
        st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Add idea", type="primary", use_container_width=True, key="add_idea_btn"):
            st.session_state["show_idea_form"] = not st.session_state.get("show_idea_form", False)

    if st.session_state.get("show_idea_form"):
        with st.form("nif", border=True):
            t = st.text_input("Idea", placeholder="What's your idea?")
            d = st.text_area("Details (optional)", height=68, placeholder="Add context, goals, how it works…")
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Submit idea", type="primary", use_container_width=True):
                    if t:
                        create_idea(room_id, user_id, t, d)
                        st.session_state["show_idea_form"] = False
                        st.rerun()
            with c2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_idea_form"] = False
                    st.rerun()

    # Filter + sort bar
    fc, sc = st.columns([3, 1])
    with fc:
        sf = st.multiselect(
            "STATUS FILTER", STATUSES,
            default=["Open","Selected","In Progress"],
            label_visibility="collapsed",
            placeholder="Filter by status…",
        )
    with sc:
        sort = st.selectbox("SORT", ["Newest","Most voted"], label_visibility="collapsed")

    ideas    = get_room_ideas(room_id)
    filtered = [i for i in ideas if i["status"] in (sf or STATUSES)]
    if sort == "Most voted": filtered.sort(key=lambda x: x["vote_count"], reverse=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    if not filtered:
        render_empty_state("💡", "No ideas yet", "Be the first to submit one.")
        return

    for idea in filtered:
        _render_idea_row(idea, user_id)


def _render_idea_row(idea: dict, user_id: int):
    status = idea.get("status", "Open")
    color  = STATUS_COLOR.get(status, "#6366F1")
    dot    = STATUS_DOT.get(status, "◉")
    uv     = get_user_vote(idea["id"], user_id)
    votes  = idea.get("votes", {})

    st.markdown(f"""
    <div style="
        background:#181818; border:1px solid #1E1E1E;
        border-radius:8px; padding:0.9rem 1.1rem 0.75rem;
        margin-bottom:0.5rem;
    ">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.35rem;">
            <div style="
                font-family:'Clash Display','Outfit',sans-serif;
                font-size:0.88rem; font-weight:600;
                color:#EEEADF; letter-spacing:-0.01em;
                flex:1; margin-right:0.75rem;
            ">{idea['title']}</div>
            <span style="
                color:{color}; font-size:0.68rem; font-weight:600;
                font-family:'Inter',sans-serif;
                white-space:nowrap;
                background:{color}12; border:1px solid {color}25;
                border-radius:4px; padding:2px 8px;
                text-transform:uppercase; letter-spacing:0.06em;
            ">{dot} {status}</span>
        </div>
        {'<div style="color:#334155;font-size:0.76rem;font-family:Outfit,sans-serif;margin-bottom:0.35rem;">'+idea.get("description","")+"</div>" if idea.get("description") else ""}
        <div style="color:#2A2A2A;font-size:0.7rem;font-family:'Outfit',sans-serif;">
            {idea.get('author_name','?')} · {str(idea.get('created_at',''))[:10]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    vc = st.columns([1, 1, 1, 2])
    for j, (emoji, vtype) in enumerate(VOTE_TYPES.items()):
        cnt   = votes.get(vtype, 0)
        voted = uv == vtype
        label = f"{emoji} {cnt}{'  ✓' if voted else ''}"
        with vc[j]:
            if st.button(label, key=f"v_{idea['id']}_{vtype}", use_container_width=True):
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
            update_idea_status(idea["id"], ns)
            st.rerun()
