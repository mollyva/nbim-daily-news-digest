# 🗞️ NBIM Daily News Digest

A proof-of-concept tool for NBIM's communications team that automatically fetches, filters, and categorizes daily news articles relevant to the fund.

Built as a case interview project.

## 📌 What it does

Each time the digest is triggered, the tool:

1. Fetches up to 25 articles from NewsAPI based on NBIM-relevant topics
2. Sends them to Claude with a prompt tailored for NBIM's communications team
3. Returns a categorized digest where each article is assigned one of four actions:
   - **Recommend public response** — NBIM likely needs proactive external communication
   - **Alert portfolio manager** — material development affecting a specific portfolio company
   - **Comms team action required** — internal preparation needed, no public statement yet
   - **Monitor only** — awareness tracking, no immediate follow-up needed

## 🗂️ Repo structure

```text
nbim-daily-news-digest/
├── backend/
│   ├── main.py                      # FastAPI server — exposes /digest endpoint
│   ├── digest.py                    # Claude API integration and digest generation
│   ├── news_fetcher.py              # NewsAPI integration
│   └── config/
│       ├── prompt.txt               # Claude prompt — action taxonomy and instructions
│       ├── nbim_topics.txt          # Topics used for NewsAPI search and Claude context
│       └── nbim_markets.txt         # NBIM key markets (country codes)
├── frontend/
│   └── src/
│       ├── App.jsx                  # Routing between landing and digest view
│       ├── constants.js             # Colors and action badge config
│       └── components/
│           ├── LandingPage.jsx      # Welcome screen with fetch button
│           ├── DigestDashboard.jsx  # Main dashboard with stats and article grid
│           ├── ArticleCard.jsx      # Individual article card
│           ├── ActionBadge.jsx      # Color-coded action badge
│           └── StatsSummary.jsx     # Article count summary by action
├── .env.example                     # Environment variable template
├── requirements.txt                 # Python dependencies
└── README.md
```

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [NewsAPI](https://newsapi.org) API key (free tier works for development)
- An [Anthropic](https://console.anthropic.com) API key

### 1. Clone the repo 🧬

```bash
git clone https://github.com/mollyva/nbim-daily-news-digest.git
cd nbim-daily-news-digest
```

### 2. Set up environment variables 🔐

```bash
cp .env.example .env
```

Fill in your API keys in `.env`:

```text
NEWS_API_KEY=your_newsapi_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Set up the backend 🖥️

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
```

Your terminal prompt should show `(venv)` to confirm the environment is active. Then install dependencies:

```bash
pip install -r requirements.txt
```

Verify everything installed correctly:

```bash
pip list
```

You should see `fastapi`, `uvicorn`, `anthropic`, `requests`, and `python-dotenv` in the list.

### 4. Set up the frontend 🎨

```bash
cd frontend
npm install
```

## 🚀 Running the app

Start the backend from the repo root (with venv active):

```bash
uvicorn backend.main:app --reload
```

Start the frontend in a separate terminal:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🔌 API endpoints

```text
GET /                         → API status check
GET /digest?mock=true         → Returns mock digest (no API calls)
GET /digest?mock=false        → Fetches live articles and generates digest
```

Auto-generated API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🧪 Mock mode

The app defaults to `mock=true` to avoid burning API credits during development and demos. To test with live data, change the fetch URL in `frontend/src/App.jsx`:

```js
const res = await fetch("http://localhost:8000/digest?mock=false");
```

## 🏗️ Architecture

```text
Frontend (React)
    ↓ GET /digest?mock=true/false
Backend (FastAPI)
    ↓ fetch articles
NewsAPI (/everything + /top-headlines)
    ↓ up to 25 articles
Claude API (claude-sonnet-4-5)
    ↓ filtered + categorized JSON
Frontend renders article cards
```

All 25 articles are sent to Claude in a single API call rather than one call per article. This keeps costs low since the topics file and prompt are only sent once, and reduces latency by eliminating per-request overhead. Claude is instructed to treat each article individually despite receiving them together.

## 🗃️ Configuration files

Three plain text files control the tool's behavior and can be updated without touching code:

**`nbim_topics.txt`** — drives both the NewsAPI search query (first entries) and provides Claude with full context on what NBIM cares about. Update this to shift the digest's focus.

**`nbim_markets.txt`** — defines NBIM's key markets by country code. Currently only `us` is used for `/top-headlines` due to a NewsAPI limitation (see Known Limitations), but the file is ready for a production API with multi-country support.

**`prompt.txt`** — the full Claude prompt including the action taxonomy, decision rules, and output format. The `{topics}` and `{articles}` placeholders are filled in at runtime.

## 🎯 Action taxonomy

Each article is assigned exactly one action, defined along two axes: **external vs internal** and **urgency**.

| Action                         | When to use                                                                                                                                                                                                                                 |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Recommend public response**  | NBIM is directly and significantly named, or the article concerns a topic where NBIM has a stated public position (ESG, voting, ethical guidelines). Comms team escalates to leadership with a recommendation — they do not act themselves. |
| **Alert portfolio manager**    | A specific named company likely held in NBIM's portfolio has a material development — unexpected earnings, M&A, scandal, regulatory action, or major restructuring. Investment side must be informed.                                       |
| **Comms team action required** | Relevant to NBIM's reputation but no public statement yet. Comms team prepares internally — drafts Q&A, briefs leadership, monitors journalist interest.                                                                                    |
| **Monitor only**               | Relevant to NBIM's communications responsibilities but no immediate follow-up needed. Comms team keeps awareness in case the situation develops. Specifically for comms monitoring, not investment action.                                  |

## ⚠️ Known limitations

**Norwegian sources not supported**
NewsAPI does not index Norwegian media (DN, E24, Aftenposten, VG). This is a significant gap since Norwegian coverage of NBIM is critical for the communications team. In production, there would be added support for this.

**Article ingress only**
NewsAPI returns only the first ~200 characters of article content due to paywalls. Claude works with titles and descriptions rather than full text. The most relevant sources for NBIM (FT, Bloomberg, WSJ) are behind paywalls, making full-text retrieval difficult. In production, licensed content agreements — realistic for an institution of NBIM's size — would solve this. Then, some form of web scraping would be considered.

**US headlines only**
NewsAPI's `/top-headlines` endpoint only supports country filtering for the US. The other markets in `nbim_markets.txt` (Japan, UK, Germany, France) return empty results. This is a permanent API limitation, not a plan restriction. A production version would use an API with proper multi-country support.

**No caching**
Each button press triggers fresh API calls to both NewsAPI and Claude. A production version would cache the digest for the day and serve the cached result on subsequent requests, reducing costs and latency.

**Non-determinism**
Claude may assign different actions to the same article on different runs, particularly for borderline cases. The prompt's decision rules and examples reduce this but do not eliminate it. A human reviewer on the comms team should always make the final call.

**English only**
The NewsAPI query filters for `language=en`. Important news published in Japanese, German, or French about NBIM or its portfolio companies may be missed. The most significant international financial news is published in English regardless, making this an acceptable trade-off for a PoC.

**Domain list not exhaustive**
The domain filter on `/everything` was set up temporarily and may be missing relevant sources, particularly for non-English markets. Norwegian sources (DN, E24, Finansavisen) are included but rarely return results due to NewsAPI's limited Norwegian indexing.

## 🛠️ Tech stack

| Layer             | Technology                 | Why                                                                         |
| ----------------- | -------------------------- | --------------------------------------------------------------------------- |
| Frontend          | React + Vite               | Fast setup, component-based, easy to iterate                                |
| Backend           | FastAPI                    | Less boilerplate than Flask, auto-generates API docs                        |
| News data         | NewsAPI                    | Simple integration, good English-language financial coverage, free tier     |
| AI filtering      | Claude (claude-sonnet-4-5) | Strong instruction-following, consistent JSON output, good on long contexts |
| Runtime isolation | Python venv                | Reproducible environment across machines                                    |
