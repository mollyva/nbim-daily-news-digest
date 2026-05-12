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
                "title": "Norway Wealth Fund Faces NGO Scrutiny Over Climate Voting Record",
                "author": None,
                "source": "ESG News",
                "published_at": "2026-05-06",
                "url": "https://esg-investing.com/2026/05/05/norway-wealth-fund-faces-ngo-scrutiny-over-climate-voting-record/",
                "relevance_score": 5,
                "summary": "Norwegian NGO Future in Our Hands publicly criticizes NBIM's 2025 climate voting record, arguing the fund failed to use director votes to hold major oil and gas companies accountable. NBIM is directly and centrally named and its core ESG stewardship mandate is being challenged.",
                "action": "Recommend public response",
                "action_reasoning": "NBIM is directly criticized by an NGO over its ESG voting behavior — a core stated position — requiring proactive external communication to protect the fund's reputation.",
            },
            {
                "title": "Norwegian Sovereign Wealth Fund Eyes Partnership With Dangote Group On Africa Investments",
                "author": None,
                "source": "TVC News",
                "published_at": "2026-05-11",
                "url": "https://www.tvcnews.tv/norwegian-sovereign-wealth-fund-eyes-partnership-with-dangote-group-on-africa-investments/",
                "relevance_score": 5,
                "summary": "NBIM CEO Nicolai Tangen met with Dangote Group CEO to discuss a potential partnership expanding the fund's footprint across Africa in power, energy, renewables and agriculture. NBIM is directly named and the CEO is involved in a high-profile strategic discussion.",
                "action": "Comms team action required",
                "action_reasoning": "NBIM is directly named and the CEO is involved, but this is a positive investment story rather than a controversy — comms team should prepare talking points in case journalists ask for comment.",
            },
            {
                "title": "Syria: TotalEnergies Signs a Cooperation Agreement on Offshore Exploration",
                "author": None,
                "source": "Business Wire",
                "published_at": "2026-05-11",
                "url": "https://finance.yahoo.com/sectors/energy/articles/syria-totalenergies-signs-cooperation-agreement-122400333.html",
                "relevance_score": 4,
                "summary": "TotalEnergies has signed an MoU with the Syrian Petroleum Company for offshore exploration, resuming a relationship that ended in 2011. This is a potentially controversial geopolitical move by a major portfolio company with sanctions and ESG implications.",
                "action": "Alert portfolio manager",
                "action_reasoning": "TotalEnergies is a specific named major portfolio company entering a material and potentially controversial agreement with Syria, directly actionable for investment teams assessing portfolio risk.",
            },
            {
                "title": "Nvidia embraces role of AI investor, pushing past $40 billion in equity bets this year",
                "author": "Kristina Partsinevelos",
                "source": "CNBC",
                "published_at": "2026-05-08",
                "url": "https://www.cnbc.com/2026/05/09/nvidia-embraces-ai-investor-topping-40-billion-in-equity-bets-2026.html",
                "relevance_score": 4,
                "summary": "Nvidia has deployed over $40 billion in equity investments in AI companies in 2026, marking a major strategic shift beyond chip manufacturing. Critics have raised concerns about circular investment dynamics that could affect Nvidia's valuation and risk profile.",
                "action": "Alert portfolio manager",
                "action_reasoning": "Nvidia is a specific named major portfolio company undergoing material strategic restructuring with significant capital deployment implications for its valuation.",
            },
            {
                "title": "Climate and Energy: EU Policy and Regulation Update for 6 May 2026",
                "author": None,
                "source": "Cleary Gottlieb",
                "published_at": "2026-05-06",
                "url": "https://www.clearygottlieb.com/news-and-insights/publication-listing/climate-energy-eu-policy-regulation-update-2026-05-06",
                "relevance_score": 3,
                "summary": "A broad EU regulatory update covering sustainability reporting developments including EFRAG's work programme, ISSB's decision not to mandate nature disclosures, and ESMA's consultation on ESG ratings endorsement. Relevant to NBIM's sustainability positioning and reporting obligations.",
                "action": "Monitor only",
                "action_reasoning": "Broad EU sustainability regulation update relevant to NBIM's ESG focus — worth tracking but no immediate comms action required.",
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
