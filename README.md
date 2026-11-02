# 🎭 Persona Chat

Create your own AI persona and chat with it.

You describe a person (background, tone, favourite phrases, example conversations, rules), the app turns your answers into one system prompt, sends it to the OpenAI API, and shows the replies in a chat UI.

<!-- Add a screenshot after deploying: ![App screenshot](screenshot.png) -->
**Live demo:** [https://your-app.streamlit.app](https://ai-persona-chatgit.streamlit.app/) 

## Features

- **Persona form** in the sidebar: name, background, tone and language, phrases, example conversations, rules
- **Prompt builder** that assembles the form answers into a single system prompt (empty fields are skipped)
- **Chat UI** with custom dark theme and chat bubbles
- **Example persona** loaded with one click, so you can try it instantly
- **Cost control:** only the last 20 messages are sent to the API with each request
- **Safe rendering:** user and AI text is HTML-escaped before display
- **Clear separation of concerns:** UI code and backend code live in different files

## How it works

```
Sidebar form  →  build_system_prompt()  →  conversation  →  OpenAI API  →  reply shown in chat
   (app.py)          (backend.py)          (session state)   (backend.py)        (app.py)
```

The OpenAI API is stateless, so every request sends the system prompt plus recent messages. The model only "remembers" what is in that list. Streamlit's `session_state` keeps the list between page reruns.

## Project structure

```
persona_app/
├── app.py            # UI: sidebar form, chat display, buttons (Streamlit)
├── backend.py        # Backend: OpenAI client, prompt builder, API call (no Streamlit)
├── prompt.py         # Prompt template pieces + example persona
├── styles.css        # Theme and chat bubble styling
├── requirements.txt  # Python dependencies
├── .env.example      # Template for the API key (copy to .env)
└── README.md
```

`backend.py` never imports Streamlit, so it can be reused later (for example in a FastAPI service).

## Getting started

**Prerequisites:** Python 3.10+ and an [OpenAI API key](https://platform.openai.com/api-keys).

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR-USERNAME/persona-chat.git
   cd persona-chat
   ```

2. **Install dependencies** (a virtual environment is recommended)
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your API key.** Copy `.env.example` to `.env` and put your key in it:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
   `.env` is listed in `.gitignore`, so it is never committed.

4. **Run the app**
   ```bash
   streamlit run app.py
   ```
   Open `http://localhost:8501`. If `streamlit` is not recognised, use `python -m streamlit run app.py`.

## Usage

1. Fill in the persona form in the sidebar (only **Name** is required), or click **Load example persona**.
2. Click **Apply persona & start chat**.
3. Type a message and press Enter.
4. Use **Clear Chat** to start over with the same persona. Applying a new persona also starts a fresh chat.

Tip: the **Example conversations** field has the biggest effect on how closely the replies match the voice you want.

## Configuration

Settings live at the top of `backend.py`:

| Setting | Default | Meaning |
|---|---|---|
| `MODEL_NAME` | `gpt-5.4-nano` | OpenAI model used for replies |
| `MAX_REPLY_TOKENS` | `1000` | Maximum length of each reply |
| `MAX_HISTORY_MESSAGES` | `20` | How many recent chat messages are sent with each request |

## Deployment (Streamlit Community Cloud)

1. Push the repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), sign in with GitHub and choose **Create app**.
3. Select the repo, branch `main`, and main file `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```
   OPENAI_API_KEY = "sk-your-real-key"
   ```
5. Deploy.

No code changes are needed: the secret is available as an environment variable, which is where the OpenAI client looks for it.

> **Cost warning:** a public deployment uses your API key for every visitor. Set a monthly spending limit in your OpenAI dashboard before sharing the link.

## Limitations

- The persona exists only in the browser session. Refreshing the page clears it.
- The AI knows only what is in the prompt plus its general training. It does not look up real facts about the person you describe.
- Replies can be wrong or invented. Do not rely on them for medical, legal or financial advice.
- Personas are imitations written by a language model, not the real people.

## Ideas for next steps

- Download and upload a persona as a JSON file
- Let visitors enter their own API key instead of using yours
- Focus on one use case, such as interview practice with role selection and feedback
- Stream replies as they are generated

## Tech stack

Python · Streamlit · OpenAI API · python-dotenv
