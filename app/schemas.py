from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class PropertyItem(BaseModel):
    source: str                 # "domain" | "realestate"
    title: Optional[str] = None
    address: Optional[str] = None
    price: Optional[str] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    parking: Optional[float] = None
    url: Optional[HttpUrl] = None
    image_urls: List[HttpUrl] = []
    # tuỳ chọn: vector hoá ảnh
    image_embeddings: Optional[list] = None  # 2D list [n_images][512]

class SearchResponse(BaseModel):
    query: str
    results: List[PropertyItem] = []

class EmbedRequest(BaseModel):
    image_urls: List[HttpUrl]

class EmbedResponse(BaseModel):
    vectors: list  # 2D list
