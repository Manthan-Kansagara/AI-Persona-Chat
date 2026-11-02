"""
backend.py
----------
Everything that talks to OpenAI, and everything that builds the prompt.
This file does NOT import streamlit -- so it can be tested or reused
(e.g. in a FastAPI app) without any UI.
"""

from dotenv import load_dotenv
from openai import OpenAI

from prompt import GENERAL_RULES, PROMPT_SECTIONS

# Read OPENAI_API_KEY from the .env file into environment variables.
load_dotenv()

# Settings you may want to tweak, kept in one place.
MODEL_NAME = "gpt-5.4-nano"
MAX_REPLY_TOKENS = 1000
MAX_HISTORY_MESSAGES = 20   # only the last 20 chat messages are sent (saves cost)


def create_client() -> OpenAI:
    """Create the OpenAI client. Raises an error if the API key is missing."""
    return OpenAI()


def build_system_prompt(persona: dict) -> str:
    """
    Turn the form answers into one system prompt.

    persona = {"name": "Riya", "background": "...", "tone": "...", ...}
    Empty fields are skipped, so a short form still gives a clean prompt.
    """
    name = persona.get("name", "").strip() or "this person"

    parts = [f"You are an AI persona of {name}. Reply exactly the way {name} would talk."]

    for key, heading in PROMPT_SECTIONS:
        value = persona.get(key, "").strip()
        if value:
            parts.append(f"{heading}:\n{value}")

    parts.append(GENERAL_RULES)
    return "\n\n".join(parts)


def new_conversation(persona: dict) -> list[dict]:
    """A fresh conversation always starts with just the system prompt."""
    return [{"role": "system", "content": build_system_prompt(persona)}]


def get_ai_reply(client: OpenAI, messages: list[dict]) -> str:
    """
    Send the conversation to OpenAI and return the reply text.

    `messages` looks like:
        [{"role": "system", "content": "..."},
         {"role": "user", "content": "React kaise seekhun?"}]

    We always keep the system prompt (messages[0]) and only the most
    recent chat messages after it, so long chats don't grow forever.
    """
    recent = [messages[0]] + messages[1:][-MAX_HISTORY_MESSAGES:]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=recent,
        max_completion_tokens=MAX_REPLY_TOKENS,
    )
    return response.choices[0].message.content.strip()
