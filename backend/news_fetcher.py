import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2"


def load_topics(filepath="backend/config/nbim_topics.txt"):
    """Read nbim_topics.txt and return a list of topics"""
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def load_countries(filepath="backend/config/nbim_markets.txt"):
    """Read nbim_markets.txt and return a list of country codes"""
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def fetch_topic_articles() -> list[dict]:
    """
    Fetches articles from the /everything endpoint based on NBIM topics.
    Uses OR between the search terms so we get hits on any of them.
    Ex: "equity markets OR ESG regulation OR geopolitics OR ..."
    Limited to quality financial sources via domains parameter.
    """
    topics = load_topics()
    query = " OR ".join(topics[:10])

    try:
        response = requests.get(
            f"{BASE_URL}/everything",
            params={
                "q": query,  # the search query
                "language": "en",  # only english articles
                "sortBy": "publishedAt",  # newest first, for daily digest this makes most sense
                "pageSize": 20,  # fetch 20 topic articles
                "apiKey": NEWS_API_KEY,
                "domains": "reuters.com,bloomberg.com,ft.com,wsj.com,cnbc.com,economist.com,forbes.com,businessinsider.com,marketwatch.com,apnews.com,bbc.co.uk,theguardian.com,nytimes.com,dn.no,e24.no,finansavisen.no",
            },
        )
        return response.json().get("articles", [])
    except Exception as e:
        print(f"Error fetching topic articles: {e}")
        return []


def fetch_headline_articles() -> list[dict]:
    """
    Fetches top headlines from the /top-headlines endpoint per country from nbim_markets.txt.
    All NBIM key markets are defined in nbim_markets.txt and can easily be updated there.

    Note: NewsAPI only supports country filtering for 'us' on the /top-headlines endpoint.
    This is a permanent API limitation, not a plan restriction.
    We use countries[0] (us) to avoid unnecessary API calls for countries that return nothing.
    In a production version with a news API that supports all countries, all countries in
    nbim_markets.txt would be used automatically.
    """
    countries = load_countries()

    try:
        response = requests.get(
            f"{BASE_URL}/top-headlines",
            params={
                "country": countries[
                    0
                ],  # only 'us' supported by NewsAPI — see docstring above
                "category": "business",  # rough filter before Claude does fine filtering
                "pageSize": 5,  # up to 5 articles
                "apiKey": NEWS_API_KEY,
            },
        )
        return response.json().get("articles", [])
    except Exception as e:
        print(f"Error fetching headline articles: {e}")
        return []


def fetch_all_articles() -> list[dict]:
    """
    Combines articles from both endpoints and removes duplicates.
    20 topic articles + up to 5 US headline articles = up to 25 total.
    """
    topic_articles = fetch_topic_articles()[:20]
    headline_articles = fetch_headline_articles()[:5]
    all_articles = topic_articles + headline_articles

    # Removes duplicates by checking the URL
    # The same article might appear in both topic searches and headline searches
    seen = set()
    unique = []
    for article in all_articles:
        url = article.get("url")
        if url and url not in seen:
            seen.add(url)
            unique.append(
                {
                    "title": article.get("title"),
                    "author": article.get("author"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "publishedAt": article.get("publishedAt"),
                    "content": article.get("content"),
                    "source": article.get("source", {}).get("name"),
                }
            )

    return unique[:25], topic_articles, headline_articles


# Only runs if you start the file directly with "python news_fetcher.py"
# Not when it is imported from another file, for example from main.py
if __name__ == "__main__":
    articles, topic_articles, headline_articles = fetch_all_articles()

    print(f"=== TOPIC ARTICLES ({len(topic_articles)}) ===")
    for a in topic_articles:
        print(f"- {a['title']}")

    print(f"\n=== HEADLINE ARTICLES ({len(headline_articles)}) ===")
    for a in headline_articles:
        print(f"- {a['title']}")

    print(f"\n=== TOTAL UNIQUE ARTICLES ({len(articles)}) ===")
