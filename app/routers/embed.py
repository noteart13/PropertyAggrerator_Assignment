from fastapi import APIRouter
from app.schemas import EmbedRequest, EmbedResponse
from app.services.embed_clip import embed_image_urls

router = APIRouter(prefix="/v1/embed", tags=["embedding"])

@router.post("", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    vectors = embed_image_urls([str(u) for u in req.image_urls])
    return EmbedResponse(vectors=vectors)
