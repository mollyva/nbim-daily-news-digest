import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2"


def load_topics(filepath="backend/nbim_topics.txt"):
    """Leser nbim_topics.txt og returnerer en liste med søkeord"""
    with open(filepath, "r") as f:
        # Hopper over tomme linjer og kommentarer som starter med #
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def load_countries(filepath="backend/nbim_markets.txt"):
    """Leser nbim_markets.txt og returnerer en liste med landskoder"""
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def fetch_topic_articles() -> list[dict]:
    """
    Henter artikler fra /everything endepunktet basert på NBIM topics.
    Bruker OR mellom søkeordene så vi får treff på hvilket som helst av dem.
    Eks: "equity markets OR ESG regulation OR geopolitics OR ..."
    """
    topics = load_topics()

    # Setter sammen søkestreng med OR mellom topics
    # Begrenser til 5 topics for å holde søket presist og relevant
    query = " OR ".join(topics[:5])

    response = requests.get(
        f"{BASE_URL}/everything",
        params={
            "q": query,  # søkestrengen
            "language": "en",  # kun engelske artikler
            "sortBy": "relevancy",  # mest relevante først
            "pageSize": 20,  # maks 20 artikler
            "apiKey": NEWS_API_KEY,
            "domains": "reuters.com,bloomberg.com,ft.com,wsj.com,cnbc.com,economist.com,forbes.com,businessinsider.com,marketwatch.com,apnews.com,bbc.co.uk,theguardian.com,nytimes.com,dn.no,e24.no,finansavisen.no",
        },
    )

    # Returnerer listen med artikler, eller tom liste hvis noe gikk galt
    return response.json().get("articles", [])


def fetch_headline_articles() -> list[dict]:
    """
    Henter toppnyheter fra /top-headlines endepunktet.
    Går gjennom hvert land i nbim_markets.txt og henter opptil 5 artikler per land.
    Totalt maks 25 artikler (5 land x opptil 5 artikler).
    category: business brukes som grovfilter — Claude gjør finfiltrering etterpå.
    """
    countries = load_countries()
    articles = []

    for country in countries:
        response = requests.get(
            f"{BASE_URL}/top-headlines",
            params={
                "country": country,  # landskode, eks "us", "gb"
                "category": "business",  # grovfilter før Claude gjør finfiltrering
                "pageSize": 5,  # opptil 5 artikler per land
                "apiKey": NEWS_API_KEY,
            },
        )
        # Legger til artiklene fra dette landet i den totale listen
        articles.extend(response.json().get("articles", []))

    return articles


def fetch_all_articles() -> list[dict]:
    """
    Kombinerer artikler fra begge endepunktene og fjerner duplikater.
    Returnerer maks 20 artikler totalt som sendes videre til Claude.
    """
    all_articles = fetch_topic_articles() + fetch_headline_articles()

    # Fjerner duplikater ved å sjekke URL
    # Samme artikkel kan dukke opp i både topic-søk og headline-søk
    seen = set()
    unique = []
    for article in all_articles:
        url = article.get("url")
        if url and url not in seen:
            seen.add(url)
            # Beholder kun feltene vi trenger, fjerner urlToImage
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


# Kjører kun hvis du starter filen direkte med "python news_fetcher.py"
# Ikke når den importeres fra en annen fil
if __name__ == "__main__":
    articles = fetch_all_articles()
    print(f"Hentet {len(articles)} artikler")
    for a in articles:
        print(f"- {a['title']}")
