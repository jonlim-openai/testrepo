# backend.py
# ------------------------------------------------------------------
# A tiny FastAPI service that returns a short-lived EPHEMERAL_KEY
# required by the OpenAI Realtime WebRTC API.
#
# Start it with:
#   uvicorn backend:app --host 0.0.0.0 --port 8000
# ------------------------------------------------------------------
import os, logging, openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("realtime-token")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in the environment!")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Allow Streamlit (same container) to fetch /session
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten in prod!
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/session")
async def create_session():
    """
    Mint an EPHEMERAL_KEY via the official SDK call.
    The `expires_in` is optional – adjust to your needs.
    """
    try:
        token = openai.beta.realtime.tokens.create(expires_in=600)
        logger.info("Issued new EPHEMERAL_KEY (exp 10 min)")
        return token
    except Exception as exc:
        logger.exception("Token minting failed")
        raise HTTPException(500, "Realtime token request failed") from exc
