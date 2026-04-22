# AI Website Summarizer

A lightweight web app that takes any public URL, scrapes the page content, and returns a concise AI-generated summary using OpenAI. Built with a Flask backend and a clean single-page front-end.

![Stack](https://img.shields.io/badge/backend-Flask-informational)
![Language](https://img.shields.io/badge/language-Python%203.9%2B-blue)
![AI](https://img.shields.io/badge/AI-OpenAI%20gpt--4.1--mini-ff69b4)

## Features

- Paste any URL and get a clean, markdown-formatted summary in seconds
- Modern, responsive UI with a dark gradient theme and Inter typography
- Automatic `https://` prepending if you paste a bare domain
- Inline loading state, error handling, and Markdown rendering of the AI response
- Minimal dependencies — runs locally with a single `python app.py`

## Project Structure

```
.
├── app.py                 # Flask server — serves the UI and the /api/summarize endpoint
├── Calling.py             # OpenAI call wrapper with the prompt & summarize() function
├── scraper.py             # BeautifulSoup website content fetcher
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Front-end (HTML + CSS + JS, single file)
└── README.md
```

## Prerequisites

- Python 3.9 or newer
- An OpenAI API key (get one at https://platform.openai.com/api-keys)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/ai-website-summarizer.git
cd ai-website-summarizer
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# macOS / Linux:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a file named `.env` in the project root:

```
OPENAI_API_KEY=sk-proj-your-key-here
```

> The key must start with `sk-proj-`. Never commit your `.env` file — it's already in `.gitignore`.

### 5. Run the app

```bash
python app.py
```

Open your browser to **http://127.0.0.1:5000**, paste a URL, and hit **Summarize**.

## How It Works

1. The front-end sends the URL to `POST /api/summarize` as JSON.
2. `app.py` validates the URL and calls `summarize(url)` from `Calling.py`.
3. `scraper.py` fetches the page with `requests`, strips scripts/styles/images using BeautifulSoup, and truncates to 2,000 characters.
4. The cleaned text is sent to OpenAI (`gpt-4.1-mini`) with a system + user prompt.
5. The model's markdown response is returned to the browser and rendered via `marked.js`.

## Configuration

You can tweak the behavior by editing `Calling.py`:

- `system_prompt` — controls the tone/persona of the summary
- `user_prompt` — the instruction template sent alongside the scraped content
- `model` — change `gpt-4.1-mini` to any OpenAI chat model you have access to

You can also adjust the scrape length in `scraper.py` (the `[:2_000]` slice).

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `No API key was found` | Make sure `.env` exists in the project root and contains `OPENAI_API_KEY=...` |
| `ModuleNotFoundError: No module named 'flask'` | Activate your venv, then `pip install -r requirements.txt` |
| Summary is empty or generic | The target page may be JavaScript-rendered; the scraper only reads static HTML |
| Port 5000 already in use | Change the port at the bottom of `app.py` (`app.run(..., port=5001)`) |

## License

MIT — feel free to fork, modify, and use.

## Acknowledgments

- [OpenAI](https://openai.com/) for the language model
- [Flask](https://flask.palletsprojects.com/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [marked.js](https://marked.js.org/) for the plumbing
