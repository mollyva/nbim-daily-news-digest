import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2"


def load_topics(filepath="backend/nbim_topics.txt"):
    """Read nbim_topics.txt and return a list of topics"""
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def load_countries(filepath="backend/nbim_markets.txt"):
    """Read nbim_markets.txt and return a list of country codes"""
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def fetch_topic_articles() -> list[dict]:
    """
    Fetches articles from the /everything endpoint based on NBIM topics.
    Uses OR between the search terms so we get hits on any of them.
    Eks: "equity markets OR ESG regulation OR geopolitics OR ..."
    """
    topics = load_topics()

    query = " OR ".join(topics[:5])

    response = requests.get(
        f"{BASE_URL}/everything",
        params={
            "q": query,  # the search query
            "language": "en",  # only english articles
            "sortBy": "publishedAt",  # newest first, for daily digest this makes most sense
            "pageSize": 20,  # maximum 20 articles
            "apiKey": NEWS_API_KEY,
            "domains": "reuters.com,bloomberg.com,ft.com,wsj.com,cnbc.com,economist.com,forbes.com,businessinsider.com,marketwatch.com,apnews.com,bbc.co.uk,theguardian.com,nytimes.com,dn.no,e24.no,finansavisen.no",
        },
    )

    return response.json().get("articles", [])


def fetch_headline_articles() -> list[dict]:
    """
    Fetches top headlines from the /top-headlines endpoint.
    Goes through each country in nbim_markets.txt and fetches up to 5 articles per country.
    Total maximum 25 articles (5 countries x up to 5 articles).
    category: business is used as a rough filter — Claude does fine filtering afterwards.
    """
    countries = load_countries()
    articles = []

    for country in countries:
        response = requests.get(
            f"{BASE_URL}/top-headlines",
            params={
                "country": country,  # country code, for example "us" for USA, "no" for Norway
                "category": "business",  # rough filter before Claude does fine filtering
                "pageSize": 5,  # up to 5 articles per country
                "apiKey": NEWS_API_KEY,
            },
        )
        articles.extend(response.json().get("articles", []))

    return articles


def fetch_all_articles() -> list[dict]:
    """
    Combines articles from both endpoints and removes duplicates.
    Returns a maximum of 20 articles total to be sent further to Claude.
    """
    all_articles = fetch_topic_articles() + fetch_headline_articles()

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

    return unique[:20]


# Only runs if you start the file directly with "python news_fetcher.py"
# Not when it is imported from another file, for example from main.py
if __name__ == "__main__":
    articles = fetch_all_articles()
    print(f"Fetched {len(articles)} articles")
    for a in articles:
        print(f"- {a['title']}")
