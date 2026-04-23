"""
OpenAI call wrapper for the summarizer.

Exposes `summarize(url)` which scrapes the page and returns a markdown
summary from the configured OpenAI chat model. The OpenAI client is lazily
constructed so a missing key surfaces as a clean error at request time
rather than blowing up on import.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from scraper import fetch_website_contents

load_dotenv(override=True)

MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = "Be a funny and snarky assistant"
USER_PROMPT = (
    "Here is the url of the website.\n"
    "Provide a short summary of this website.\n"
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


def _messages_for(website_content):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT + website_content},
    ]


def summarize(url):
    """Scrape `url` and return a markdown-formatted summary from OpenAI."""
    website = fetch_website_contents(url)
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=_messages_for(website),
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
