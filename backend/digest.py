import anthropic
import json
import os
from dotenv import load_dotenv
from fastapi import HTTPException

try:
    from backend.news_fetcher import fetch_all_articles, load_topics
except ImportError:
    from news_fetcher import fetch_all_articles, load_topics

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def load_prompt(filepath="backend/config/prompt.txt"):
    """Read prompt.txt and return the prompt as a string"""
    with open(filepath, "r") as f:
        return f.read()


def format_articles(articles: list[dict]) -> str:
    """
    Formats articles into a readable string to insert into the prompt.
    Each article is separated by a blank line for clarity.
    """
    formatted = []
    for a in articles:
        formatted.append(f"""Title: {a.get('title')}
Author: {a.get('author')}
Source: {a.get('source')}
Published: {a.get('publishedAt')}
Description: {a.get('description')}
Content: {a.get('content')}
URL: {a.get('url')}""")
    return "\n\n".join(formatted)


def generate_digest(mock: bool = False) -> list[dict]:
    """
    Fetches articles, sends them to Claude with the prompt,
    and returns a structured list of relevant articles with actions.

    Args:
        mock: If True, returns hardcoded mock data instead of calling Claude API.
              Used during frontend development to avoid unnecessary API costs.
    """
    if mock:
        return [
            {
                "title": "NBIM divests from three Israeli defence companies",
                "author": "Sarah Collins",
                "source": "Financial Times",
                "published_at": "2026-05-11",
                "url": "https://ft.com",
                "relevance_score": 5,
                "summary": "NBIM has divested from three Israeli defence manufacturers citing ethical guideline violations. This directly involves NBIM and requires leadership attention.",
                "action": "Recommend public response",
                "action_reasoning": "NBIM is directly named and the article concerns the fund's ethical guidelines.",
            },
            {
                "title": "Goldman Sachs reports surprise 40% drop in quarterly profits",
                "author": "James Wright",
                "source": "Reuters",
                "published_at": "2026-05-11",
                "url": "https://ft.com",
                "relevance_score": 4,
                "summary": "Goldman Sachs reported a dramatic fall in quarterly earnings. As a major financial institution likely held in NBIM's portfolio, this is material information for the investment side.",
                "action": "Alert portfolio manager",
                "action_reasoning": "Goldman Sachs is likely held in NBIM's portfolio and a 40% profit drop is material financial information.",
            },
            {
                "title": "EU parliament debates new transparency rules for sovereign wealth funds",
                "author": None,
                "source": "The Guardian",
                "published_at": "2026-05-11",
                "url": "https://ft.com",
                "relevance_score": 4,
                "summary": "European lawmakers are pushing for stricter disclosure requirements for sovereign wealth funds, explicitly referencing Norway's oil fund.",
                "action": "Comms team action required",
                "action_reasoning": "The article references Norway's oil fund and NBIM will likely need to respond to questions about this.",
            },
            {
                "title": "ESG investing sees record inflows in first quarter of 2026",
                "author": None,
                "source": "Bloomberg",
                "published_at": "2026-05-11",
                "url": "https://ft.com",
                "relevance_score": 3,
                "summary": "Sustainable investment funds attracted record capital in Q1 2026. Relevant to NBIM's sustainability focus but no immediate action required.",
                "action": "Monitor only",
                "action_reasoning": "Broad ESG market trend with no direct NBIM relevance requiring action.",
            },
        ]

    # Load prompt and topics
    prompt_template = load_prompt()
    topics = load_topics()
    topics_str = "\n".join(topics)

    # Fetch articles
    articles, _, _ = fetch_all_articles()

    # Format articles into string for prompt
    articles_str = format_articles(articles)

    # Fill in prompt placeholders
    prompt = prompt_template.replace("{topics}", topics_str)
    prompt = prompt.replace("{articles}", articles_str)

    # Send to Claude API
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate digest — Claude API error"
        )

    # Parse JSON response
    response_text = message.content[0].text

    # Strip markdown code blocks if Claude added them despite instructions
    if response_text.strip().startswith("```"):
        response_text = response_text.strip()
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    try:
        digest = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing Claude response: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to parse digest — invalid JSON from Claude"
        )

    # Defensive filter — remove articles below relevance score 3
    # Claude should already exclude these, but this is a safety net
    digest = [a for a in digest if a.get("relevance_score", 0) >= 3]

    if not digest:
        print("Warning: Claude returned no relevant articles")

    return digest


# Only runs if you start the file directly with "python backend/digest.py"
# Not when it is imported from another file, for example from main.py
if __name__ == "__main__":
    import sys

    # Pass "mock" as argument to use mock data: python backend/digest.py mock
    use_mock = len(sys.argv) > 1 and sys.argv[1] == "mock"

    if use_mock:
        print("Running in MOCK mode — no API calls made\n")
    else:
        print("Fetching articles and generating digest...\n")

    digest = generate_digest(mock=use_mock)

    print(f"Digest contains {len(digest)} relevant articles:\n")
    for article in digest:
        print(f"Title:          {article['title']}")
        print(f"Relevance:      {article['relevance_score']}/5")
        print(f"Action:         {article['action']}")
        print(f"Action reasoning: {article['action_reasoning']}")
        print("-" * 80)
