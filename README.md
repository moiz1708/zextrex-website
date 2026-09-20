# Zextrex Technology — Flask project

The Zextrex Technology website (with the Zextrex chatbot and voice greeting)
as a Python project you can open and run in VS Code.

## Project layout

```
zextrex_site/
├── app.py              Flask app: serves the site, exposes POST /api/chat
├── assistant.py         Zextrex's persona, the model call, and an offline fallback
├── requirements.txt      Python dependencies
├── .env.example          Copy to .env and add your OpenAI key (optional)
├── templates/
│   └── index.html        The full site (unchanged design, JS now calls /api/chat)
└── static/                (empty — everything is inlined in index.html for now)
```

## Run it in VS Code

1. Open this folder in VS Code (`File → Open Folder…`).
2. Open a terminal (`` Ctrl+` ``) and create a virtual environment:
   ```bash
   python -m venv .venv
   ```
   Activate it:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional but recommended) Copy `.env.example` to `.env` and paste in an
   OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Without a key, Zextrex still works — `assistant.py` falls back to a
   built-in, rule-based reply set so the demo runs with zero setup.
5. Run the app:
   ```bash
   python app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser.

VS Code tip: install the "Python" extension, select the `.venv` interpreter
(bottom-right corner or `Ctrl+Shift+P → Python: Select Interpreter`), then
just press **F5** (or Run ▶) on `app.py` to start it with the debugger attached.

## How the chatbot works

- The page (`templates/index.html`) sends each message, plus the last few
  turns of conversation, to `POST /api/chat` as JSON.
- `app.py` hands that to `assistant.get_reply()` in `assistant.py`.
- If `OPENAI_API_KEY` is set, it calls the OpenAI chat completions API using
  the `ZEXTREX_RULES` system prompt (the company facts and the "answer
  indirectly" style) and returns the model's reply.
- If no key is set, or the call fails for any reason, `offline_fallback()`
  answers instead using simple keyword rules — so the chatbot never goes
  silent.
- The voice greeting ("Welcome to Zextrex Technology…") and the browser
  reading replies aloud both use the browser's built-in Web Speech API —
  no Python or API key needed for that part.

## Switching to a different model provider

`assistant.py` isolates the model call in `call_model()`. To use Anthropic's
API instead of OpenAI's, replace the body of that function with a call to
the `anthropic` Python client, keeping the same signature (accepts
`message` and `history`, returns a plain string).

## Customizing

- Company facts, founder names and emails: edit `COMPANY_FACTS` in
  `assistant.py`.
- Chatbot personality/style rules: edit `ZEXTREX_RULES` in `assistant.py`.
- Site content, layout and styling: edit `templates/index.html` directly —
  it is a single self-contained file (HTML, CSS and JS together).
