from fastapi import APIRouter, Query
from typing import List
from app.schemas import SearchResponse, PropertyItem
from app.config import settings
from app.services import scrape_domain_au, scrape_realestate_au
from app.services.embed_clip import embed_image_urls

router = APIRouter(prefix="/v1/properties", tags=["properties"])

@router.get("/search", response_model=SearchResponse)
def search_properties(address: str = Query(..., min_length=3),
                      with_embeddings: bool = False,
                      max_results: int = None):
    max_results = max_results or settings.max_results
    d_items = scrape_domain_au.search_by_address(address, max_results)
    r_items = scrape_realestate_au.search_by_address(address, max_results)

    # hợp nhất + cắt bớt
    items: List[PropertyItem] = (d_items + r_items)[:max_results]

    if with_embeddings and settings.enable_embeddings:
        for it in items:
            if it.image_urls:
                it.image_embeddings = embed_image_urls([str(u) for u in it.image_urls[:3]])  # mỗi listing tối đa 3 ảnh

    return SearchResponse(query=address, results=items)
