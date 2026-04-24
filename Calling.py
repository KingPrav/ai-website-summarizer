"""
OpenAI call wrapper for the summarizer.

Exposes `summarize(url, tone, length)` which scrapes the page and returns
a markdown summary from the configured OpenAI chat model. The OpenAI client
is lazily constructed so a missing key surfaces as a clean error at request
time rather than blowing up on import.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from scraper import fetch_website_contents

load_dotenv(override=True)

MODEL = "gpt-4.1-mini"

# --- Tone presets -------------------------------------------------------------
# Each preset maps to a complete system prompt that sets the assistant's voice.
TONE_PROMPTS = {
    "snarky": "Be a funny and snarky assistant who writes summaries with wit and personality.",
    "professional": (
        "You are a professional content analyst. Produce clear, factual, "
        "neutral summaries with a confident and concise tone."
    ),
    "casual": (
        "You are a friendly, conversational assistant. Summarize like you're "
        "explaining it to a friend over coffee — approachable but accurate."
    ),
}
DEFAULT_TONE = "snarky"

# --- Length presets -----------------------------------------------------------
# Each preset maps to an instruction appended to the user prompt.
LENGTH_INSTRUCTIONS = {
    "short": "Keep the summary to 3-4 sentences at most.",
    "medium": "Provide a concise summary of about two short paragraphs.",
    "detailed": (
        "Provide a thorough, multi-paragraph summary that covers the key "
        "sections, any notable details, and any news or announcements."
    ),
}
DEFAULT_LENGTH = "medium"

BASE_USER_PROMPT = (
    "Here is the content of the website.\n"
    "Provide a summary of this website.\n"
    "If it includes news or announcements, then summarize these too.\n"
)


# Lazily-instantiated client — created on first call to summarize().
_client = None


def _get_client():
    """Return a memoised OpenAI client, raising a clean error if no key is set."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Create a .env file in the project "
                "root containing OPENAI_API_KEY=sk-proj-..."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def _build_system_prompt(tone):
    return TONE_PROMPTS.get(tone, TONE_PROMPTS[DEFAULT_TONE])


def _build_user_prompt(website_content, length):
    length_instruction = LENGTH_INSTRUCTIONS.get(length, LENGTH_INSTRUCTIONS[DEFAULT_LENGTH])
    return f"{BASE_USER_PROMPT}\n{length_instruction}\n\n---\n\n{website_content}"


def _messages_for(website_content, tone, length):
    return [
        {"role": "system", "content": _build_system_prompt(tone)},
        {"role": "user", "content": _build_user_prompt(website_content, length)},
    ]


def summarize(url, tone=DEFAULT_TONE, length=DEFAULT_LENGTH):
    """
    Scrape `url` and return a markdown-formatted summary from OpenAI.

    `tone` must be one of TONE_PROMPTS keys (falls back to default otherwise).
    `length` must be one of LENGTH_INSTRUCTIONS keys (falls back to default).
    """
    website = fetch_website_contents(url)
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=_messages_for(website, tone, length),
    )
    return response.choices[0].message.content


def _diagnose_key():
    """CLI-only helper that prints the current key's sanity-check status."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No API key was found — create a .env with OPENAI_API_KEY=sk-proj-...")
    elif not api_key.startswith("sk-proj-"):
        print("An API key was found, but it doesn't start with 'sk-proj-'.")
    elif api_key.strip() != api_key:
        print("An API key was found, but it has whitespace at the start or end.")
    else:
        print("API key found and looks good so far!")


if __name__ == "__main__":
    _diagnose_key()
    print(summarize("https://praveenraj-2002.online/"))
