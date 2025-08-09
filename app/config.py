from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    user_agent: str = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; PropertyBot/1.0)")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "15"))
    max_results: int = int(os.getenv("MAX_RESULTS", "5"))
    enable_embeddings: bool = os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true"

settings = Settings()
