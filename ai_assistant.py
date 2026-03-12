"""
SankalpRoom - AI Assistant Module
Powered by Groq API for fast AI collaboration features.
"""

import os
import json
import streamlit as st

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def _get_client():
    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    if not GROQ_AVAILABLE:
        return None
    return Groq(api_key=api_key)


def _call_ai(system: str, user_message: str, max_tokens: int = 800) -> str:
    client = _get_client()

    if not client:
        return _fallback_response(user_message)

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


def _fallback_response(message: str) -> str:
    return (
        "🤖 **AI Assistant** (Demo Mode)\n\n"
        "I'm running in demo mode. To enable full AI capabilities, set your `GROQ_API_KEY`.\n\n"
        "Sample response:\n"
        "- **Idea 1**: Use team strengths to solve the problem\n"
        "- **Idea 2**: Break the challenge into smaller tasks\n"
        "- **Idea 3**: Validate ideas with early user feedback"
    )


BRAINSTORM_SYSTEM = """You are SankalpAI, an expert team collaboration and innovation strategist embedded in SankalpRoom. 
Your job is to help teams brainstorm effectively, analyze ideas critically, and make great decisions.
Be concise, practical, and energizing. Use markdown formatting. Keep responses focused and actionable."""


def brainstorm_ideas(topic: str, context: str = "") -> str:

    prompt = f"""Generate 5 creative brainstorming ideas.

Topic: {topic}
Context: {context}

For each idea provide:
- Idea title
- One-line description
- Key benefit
"""

    return _call_ai(BRAINSTORM_SYSTEM, prompt, 700)


def expand_idea(title: str, description: str) -> str:

    prompt = f"""
Analyze this idea:

Idea: {title}
Description: {description}

Provide:
Pros
Cons
Risks
Effort (Low/Medium/High)
Quick validation step
"""

    return _call_ai(BRAINSTORM_SYSTEM, prompt, 600)


def cluster_ideas(ideas: list) -> str:

    if not ideas:
        return "No ideas to cluster yet."

    idea_list = "\n".join(f"- {i['title']}" for i in ideas)

    prompt = f"""
Cluster these ideas into themes.

Ideas:
{idea_list}

Output clusters and recommend which to pursue.
"""

    return _call_ai(BRAINSTORM_SYSTEM, prompt, 600)


def impact_effort_analysis(ideas: list) -> str:

    if not ideas:
        return "No ideas to analyze."

    idea_list = "\n".join(f"- {i['title']}" for i in ideas)

    prompt = f"""
Rate ideas on Impact vs Effort.

Ideas:
{idea_list}

Return a table:
Idea | Impact | Effort | Quadrant | Recommendation
"""

    return _call_ai(BRAINSTORM_SYSTEM, prompt, 700)


def summarize_discussion(messages: list, ideas: list) -> str:

    if not messages:
        return "No discussion to summarize."

    chat_text = "\n".join(f"{m['user_name']}: {m['content']
