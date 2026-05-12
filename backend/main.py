from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.digest import generate_digest

app = FastAPI()

# Allow React frontend to call this API
# CORS = Cross-Origin Resource Sharing
# Without this, the browser blocks requests from frontend to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server default port
    allow_methods=["GET", "POST"],
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Status check — confirms the API is running"""
    return {"status": "NBIM Daily News Digest API is running"}


@app.get("/digest")
def get_digest(mock: bool = False):
    """
    Main endpoint for the news digest.
    Returns a list of relevant articles with summaries and action recommendations.

    Query params:
        mock: if true, returns mock data without calling Claude or NewsAPI.
              Use during frontend development to avoid API costs.
              e.g. http://localhost:8000/digest?mock=true
    """
    digest = generate_digest(mock=mock)
    return {"articles": digest}
