"""
Flask web app for the URL summarizer.

Serves the front-end and exposes POST /api/summarize which calls the
OpenAI-backed summarize() helper. Known error modes are mapped to
appropriate HTTP status codes with clean user-facing messages; anything
unexpected is logged server-side and returns a generic 500.
"""

import logging

from flask import Flask, jsonify, render_template, request

from Calling import DEFAULT_LENGTH, DEFAULT_TONE, LENGTH_INSTRUCTIONS, TONE_PROMPTS, summarize
from scraper import ScraperError

MAX_URL_LENGTH = 2048
ALLOWED_TONES = set(TONE_PROMPTS.keys())
ALLOWED_LENGTHS = set(LENGTH_INSTRUCTIONS.keys())

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("summarizer")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "Please provide a URL."}), 400
    if len(url) > MAX_URL_LENGTH:
        return jsonify({"error": "That URL is too long."}), 400

    # Prepend scheme if the user pasted a bare domain.
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Validate tone/length against allowlists — fall back to defaults for
    # missing or unknown values rather than failing the request.
    tone = (data.get("tone") or DEFAULT_TONE).lower()
    if tone not in ALLOWED_TONES:
        tone = DEFAULT_TONE

    length = (data.get("length") or DEFAULT_LENGTH).lower()
    if length not in ALLOWED_LENGTHS:
        length = DEFAULT_LENGTH

    try:
        summary = summarize(url, tone=tone, length=length)
        return jsonify({
            "summary": summary,
            "url": url,
            "tone": tone,
            "length": length,
        })

    except ScraperError as e:
        # Known fetch failure — the message is already user-friendly.
        logger.warning("Scrape failed for %s: %s", url, e)
        return jsonify({"error": str(e)}), 502

    except RuntimeError as e:
        # Missing config (e.g. OPENAI_API_KEY).
        logger.error("Configuration error: %s", e)
        return jsonify({"error": str(e)}), 500

    except Exception:
        # Anything else — don't leak internals to the client.
        logger.exception("Unexpected error summarizing %s", url)
        return (
            jsonify({"error": "Something went wrong on our end. Please try again."}),
            500,
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
