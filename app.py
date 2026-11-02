"""
app.py
------
Streamlit UI only: persona form, layout, styling, chat display.
All OpenAI / prompt logic is imported from backend.py.

Run with:  streamlit run app.py
"""

import html
from pathlib import Path

import streamlit as st

from backend import create_client, get_ai_reply, new_conversation
from prompt import EXAMPLE_PERSONA

# ---------------------------------------------------------------------------
# Page setup (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Persona Chat",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS_FILE = Path(__file__).parent / "styles.css"

# The persona form fields. Each one is stored in session_state as "form_<name>".
FORM_FIELDS = ["name", "background", "tone", "phrases", "examples", "rules"]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def safe_html(text: str) -> str:
    """Escape user/AI text before putting it inside our own HTML.
    Without this, typing <b> or <script> would be treated as real HTML."""
    return html.escape(text).replace("\n", "<br>")


def form_key(field: str) -> str:
    return f"form_{field}"


def load_css() -> None:
    css = CSS_FILE.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_client():
    """Cache the client so it is created once, not on every rerun."""
    try:
        return create_client()
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        st.error("Please make sure your OPENAI_API_KEY is set in your .env file")
        return None


def init_session_state() -> None:
    """Create the values Streamlit should remember between reruns."""
    defaults = {
        "persona": None,        # the applied persona (dict) or None
        "messages": [],         # sent to OpenAI (starts with the system prompt)
        "chat_history": [],     # shown on screen (no system prompt)
        "message_count": 0,
        "processing": False,
        "api_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    for field in FORM_FIELDS:
        st.session_state.setdefault(form_key(field), "")


def reset_chat() -> None:
    """Start a fresh conversation with the current persona."""
    st.session_state.chat_history = []
    st.session_state.messages = new_conversation(st.session_state.persona)
    st.session_state.message_count = 0
    st.session_state.api_error = None


# ---------------------------------------------------------------------------
# Sidebar: the persona form
# ---------------------------------------------------------------------------
def load_example() -> None:
    """Button callback: fill the form with the example persona."""
    for field in FORM_FIELDS:
        st.session_state[form_key(field)] = EXAMPLE_PERSONA[field]


def apply_persona() -> None:
    persona = {f: st.session_state[form_key(f)].strip() for f in FORM_FIELDS}
    if not persona["name"]:
        st.sidebar.warning("Please enter a name for your persona.")
        return
    st.session_state.persona = persona
    reset_chat()


def render_sidebar() -> None:
    with st.sidebar:
        st.header("🎭 Create your persona")
        st.caption("Describe the person. Everything you write becomes the AI's instructions.")

        st.button("✨ Load example persona", on_click=load_example, use_container_width=True)

        with st.form("persona_form"):
            st.text_input("Name *", key=form_key("name"), placeholder="e.g. Riya Sharma")
            st.text_area(
                "Background: who are they?", key=form_key("background"), height=110,
                placeholder="Job, experience, story, what they care about...",
            )
            st.text_area(
                "Tone and language", key=form_key("tone"), height=90,
                placeholder="e.g. friendly, funny, short replies, Hinglish",
            )
            st.text_area(
                "Phrases they often use", key=form_key("phrases"), height=70,
                placeholder="e.g. arre yaar, let's break it down, no worries",
            )
            st.text_area(
                "Example conversations", key=form_key("examples"), height=140,
                placeholder='User: "I feel stuck"\nReply: how this person would answer',
            )
            st.text_area(
                "Rules and things to avoid", key=form_key("rules"), height=80,
                placeholder="e.g. never use emojis, always end with a question",
            )
            applied = st.form_submit_button("Apply persona & start chat", use_container_width=True)

        if applied:
            apply_persona()


# ---------------------------------------------------------------------------
# Main page sections
# ---------------------------------------------------------------------------
def render_header(persona) -> None:
    if persona:
        title = f"🎭 {safe_html(persona['name'])}"
        subtitle = "AI persona chat"
    else:
        title = "🎭 Persona Chat"
        subtitle = "Create your own AI persona and chat with it"

    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats() -> None:
    _, middle, _ = st.columns(3)
    with middle:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{st.session_state.message_count}</div>
            <div class="stats-label">Messages Exchanged</div>
        </div>
        """, unsafe_allow_html=True)


def render_chat(persona) -> None:
    if not persona:
        st.markdown("""
        <div class="welcome-message">
            <h3>👈 Start in the sidebar</h3>
            <p>Fill in your persona's details and click <strong>Apply persona &amp; start chat</strong>.</p>
            <p>No ideas yet? Click <strong>Load example persona</strong> to see how it works.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    name = safe_html(persona["name"])

    if not st.session_state.chat_history:
        st.markdown(f"""
        <div class="welcome-message">
            <h3>💬 You're chatting with {name}</h3>
            <p>Say hello or ask anything. This is an AI persona, not the real person.</p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        text = safe_html(message["content"])
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="persona-message"><span class="persona-name">👤 {name}</span>{text}</div>',
                unsafe_allow_html=True,
            )


def render_input_form(persona):
    """Draw the text box + Send button. Returns (send_button, user_input)."""
    # st.form lets the Enter key submit the message
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Your message",
                placeholder=f"Message {persona['name']}... (type and press Enter)",
                label_visibility="collapsed",
                disabled=st.session_state.processing,
            )
        with col2:
            send_button = st.form_submit_button(
                "Send 🚀",
                use_container_width=True,
                disabled=st.session_state.processing,
            )
    return send_button, user_input


def handle_send(client, persona, user_input: str) -> None:
    """Add the user's message, ask the backend for a reply, store it."""
    st.session_state.api_error = None

    if client is None:
        st.session_state.api_error = "OpenAI client not initialized. Check that OPENAI_API_KEY is set correctly."
        return

    st.session_state.processing = True

    text = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": text})
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.message_count += 1

    try:
        with st.spinner(f"🤔 {persona['name']} is thinking..."):
            ai_response = get_ai_reply(client, st.session_state.messages)  # <- backend call

        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.session_state.message_count += 1
    except Exception as e:
        st.session_state.api_error = str(e)
    finally:
        st.session_state.processing = False

    st.rerun()  # redraw the page so the new messages appear


def render_clear_button() -> None:
    if st.session_state.chat_history and st.button("🗑️ Clear Chat", help="Start a fresh conversation"):
        reset_chat()
        st.rerun()


def render_footer() -> None:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 1rem;">
        <p>🎭 AI personas are imitations generated by a language model, not the real people.</p>
        <p style="font-size: 0.8rem;">⚡ Powered by OpenAI | Made with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page flow
# ---------------------------------------------------------------------------
load_css()
client = get_client()
init_session_state()
render_sidebar()          # runs first so "Apply persona" updates state before the page draws

persona = st.session_state.persona

render_header(persona)
render_stats()
render_chat(persona)

if persona:
    st.markdown("---")
    send_button, user_input = render_input_form(persona)

    if send_button and user_input.strip() and not st.session_state.processing:
        handle_send(client, persona, user_input)

if st.session_state.api_error:
    st.error(f"❌ OpenAI request failed: {st.session_state.api_error}")

render_clear_button()
render_footer()
