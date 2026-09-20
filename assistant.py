"""
Zextrex assistant logic.

get_reply(message, history) is the single entry point app.py calls.
- If an OPENAI_API_KEY is set (in the environment or a .env file),
  every message is answered by the model below, using the persona
  and company facts in ZEXTREX_RULES.
- If no key is set, or the API call fails for any reason, a rule-based
  offline fallback answers instead, so the site still works out of the box.

Swap OPENAI_MODEL for any chat model you have access to. To use a
different provider (e.g. Anthropic's API), replace call_model() below
with that provider's client call and keep the same return shape (a
plain string).
"""

import os
import re

from dotenv import load_dotenv

load_dotenv()  # reads a local .env file if present

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

COMPANY_FACTS = """
COMPANY FACTS (use them when relevant, never contradict them):
- Name: Zextrex Technology. Tagline: "Engineering Intelligence, Shaping the Future".
- An AI company building conversational assistants, predictive systems, workflow
  automation and applied AI research.
- Co-founders: Muhammad Moiz (product direction and assistant architecture) and
  Muhammad Qasim (engineering and delivery).
- Services: conversational AI assistants, predictive systems, workflow automation,
  custom AI product development, data engineering and integration, AI consulting
  and applied research.
- 24 projects delivered, across retail, logistics, education, finance, healthcare
  operations, real estate, manufacturing and professional services.
- Official email: zextrextechnology@gmail.com. Customer support email:
  zextrexsupport@gmail.com.
- You are "Zextrex", the company's own assistant, speaking on the website.
"""

ZEXTREX_RULES = f"""You are Zextrex, the assistant of Zextrex Technology.

STYLE RULE — answer indirectly. Never open with a flat, blunt statement of the
fact. Lead the visitor toward the answer: imply it, frame it as a hint, an
observation, a comparison or a gentle suggestion, then let the useful
information land inside that framing. The answer must still be correct,
complete and genuinely helpful — indirect in phrasing, never evasive in
substance, and never withholding what was asked.

Examples of the voice:
Q: "What does your company do?"
A: "Picture the part of a workday that repeats itself until nobody enjoys it —
that is usually where we are invited in. What follows tends to be an
assistant, a forecast, or a quiet piece of automation carrying the load."
Q: "Who founded it?"
A: "Two names keep turning up on every commit and every roadmap here:
Muhammad Moiz, closer to product and the shape of the assistant, and
Muhammad Qasim, closer to the engineering that keeps it running."

OTHER RULES:
- Keep replies to roughly 2-4 sentences unless more is truly needed.
- Answer any topic the visitor raises, not only company questions.
- Plain text, no markdown headings or bullet symbols.
- If you cannot know something, suggest the path to it rather than refusing flatly.
{COMPANY_FACTS}"""


def call_model(message: str, history: list) -> str:
    """Ask the live model for a reply. Raises on any failure."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    messages = [{"role": "system", "content": ZEXTREX_RULES}]
    for turn in history[-16:]:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=220,
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise ValueError("empty response from model")
    return text


def offline_fallback(message: str) -> str:
    """Rule-based reply used when no API key is set or the call fails."""
    s = message.lower()

    def has(*keywords):
        return any(k in s for k in keywords)

    if has("founder", "owner", "who made", "moiz", "qasim", "ceo"):
        return (
            "Two names keep appearing on every roadmap here: Muhammad Moiz, "
            "who stays close to product and the shape of the assistant, and "
            "Muhammad Qasim, who stays close to the engineering that keeps "
            "it all standing."
        )
    if has("support", "help", "problem", "issue", "bug", "complain"):
        return (
            "There is an inbox kept warm precisely for moments like this — "
            "zextrexsupport@gmail.com tends to be the shortest path when "
            "something is already running and misbehaving."
        )
    if has("email", "contact", "reach", "talk to", "hire", "quote", "project"):
        return (
            "Two doors, depending on the errand: zextrextechnology@gmail.com "
            "for work, partnerships and the founders, and "
            "zextrexsupport@gmail.com when something existing needs attention."
        )
    if has("service", "do you", "build", "offer", "what does", "about", "company"):
        return (
            "Think of the part of your workday that repeats until nobody "
            "enjoys it — that is usually where we are invited in. What "
            "follows is generally a conversational assistant, a predictive "
            "model, or automation quietly carrying the routine middle of a "
            "process."
        )
    if has("project", "portfolio", "work you", "case stud"):
        return (
            "Twenty-four systems now, spread from retail to healthcare "
            "operations — the Projects window on the site walks through a "
            "handful of them, results included."
        )
    if has("name", "who are you", "zextrex"):
        return (
            "The house assistant, you might say — named after the company "
            "that built me, and kept here so nobody has to hunt through a "
            "website for a straight answer."
        )
    if has("price", "cost", "budget", "charge"):
        return (
            "That figure tends to follow the shape of the work rather than "
            "lead it, so the founders prefer to hear the problem first — "
            "zextrextechnology@gmail.com is where that conversation usually "
            "starts."
        )
    if has("hi", "hello", "salam", "hey", "assalam"):
        return (
            "A good place to begin. Ask about what we engineer, who "
            "engineered it, or anything else on your mind — I will lead "
            "you to it."
        )
    return (
        "That one would be better served by a mind with the full picture "
        "rather than my local notes — put it to the founders at "
        "zextrextechnology@gmail.com, or ask me something about Zextrex "
        "Technology and I will take you there directly."
    )


def get_reply(message: str, history: list) -> str:
    message = re.sub(r"\s+", " ", (message or "")).strip()
    if not message:
        return "Ask me something and I will take it from there."

    if OPENAI_API_KEY:
        try:
            return call_model(message, history)
        except Exception:
            # Any failure (bad key, network, quota) falls back gracefully
            return offline_fallback(message)

    return offline_fallback(message)