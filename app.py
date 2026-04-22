"""
Flask web app for the URL summarizer.
Serves a clean front-end and calls the existing summarize() function
from Calling.py when the user submits a URL.
"""

from flask import Flask, render_template, request, jsonify
from Calling import summarize

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "Please provide a URL."}), 400

    # Lightweight URL validation — prepend https:// if scheme is missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        summary = summarize(url)
        return jsonify({"summary": summary, "url": url})
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {e}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
