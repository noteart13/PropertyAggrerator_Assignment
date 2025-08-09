from fastapi import FastAPI
from app.routers import properties, embed

app = FastAPI(title="Property Aggregator API", version="0.1.0")

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(properties.router)
app.include_router(embed.router)
