"""
Zextrex Technology — Flask app
================================
Serves the website (templates/index.html) and powers the Zextrex
chatbot through a small JSON API at POST /api/chat.

Run in VS Code:
    1. Open this folder in VS Code.
    2. Create a virtual environment (optional but recommended):
         python -m venv .venv
         .venv\\Scripts\\activate        (Windows)
         source .venv/bin/activate       (macOS / Linux)
    3. Install dependencies:
         pip install -r requirements.txt
    4. Copy .env.example to .env and add your OpenAI API key.
       (If you skip this step, the chatbot still runs — see
       assistant.py — using a built-in offline reply set.)
    5. Run:
         python app.py
    6. Open http://127.0.0.1:5000 in your browser.
"""

import re

from flask import Flask, render_template, request, jsonify
from assistant import get_reply
from emailer import send_contact_email

app = Flask(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []  # [{role, content}, ...] sent by the page

    if not message:
        return jsonify({"reply": "Ask me something and I will take it from there."}), 400

    reply = get_reply(message, history)
    return jsonify({"reply": reply})


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    sender_email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not sender_email or not EMAIL_RE.match(sender_email):
        return jsonify({"ok": False, "error": "Please add a valid email address."}), 400
    if not message:
        return jsonify({"ok": False, "error": "Please add a message before sending."}), 400

    try:
        send_contact_email(sender_email, message)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True)
