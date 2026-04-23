"""
Lightweight website content scraper used by the summarizer.

Wraps `requests` + BeautifulSoup with a request timeout and raises a single,
well-typed `ScraperError` with user-friendly messages for every known
failure mode so the caller (app.py) can surface clean HTTP responses.
"""

import requests
from bs4 import BeautifulSoup

# --- Tunables -----------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS = 10
MAX_CONTENT_LENGTH = 2_000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}


class ScraperError(Exception):
    """Raised when a website cannot be fetched or parsed cleanly."""


def _get(url):
    """Fetch `url` with a timeout and raise ScraperError on any failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        raise ScraperError(
            f"The website took longer than {REQUEST_TIMEOUT_SECONDS}s to respond. "
            "Try again or pick a lighter page."
        )
    except requests.exceptions.ConnectionError:
        raise ScraperError(
            "Could not connect to that URL. Check the address and your internet connection."
        )
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        raise ScraperError(f"The website returned HTTP {status}.")
    except requests.exceptions.TooManyRedirects:
        raise ScraperError("The website has too many redirects — request aborted.")
    except requests.exceptions.RequestException as e:
        raise ScraperError(f"Failed to fetch the website: {e}")


def fetch_website_contents(url):
    """
    Return `title + body text` for the page at `url`, truncated to
    MAX_CONTENT_LENGTH. Raises ScraperError on failure.
    """
    response = _get(url)

    try:
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        raise ScraperError(f"Could not parse the page's HTML: {e}")

    title = (
        soup.title.string.strip()
        if soup.title and soup.title.string
        else "No title found"
    )

    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    return (title + "\n\n" + text)[:MAX_CONTENT_LENGTH]


def fetch_website_links(url):
    """Return all non-empty `href` values found on the page at `url`."""
    response = _get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]
