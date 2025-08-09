import io
from typing import List
from PIL import Image
import torch
import clip  # from openai/CLIP
import httpx

_device = "cpu"
_model, _preprocess = clip.load("ViT-B/32", device=_device)

def _download_image(url: str) -> Image.Image:
    with httpx.Client(timeout=15, headers={"User-Agent": "PropertyBot/1.0"}) as c:
        r = c.get(url)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGB")

def embed_image_urls(urls: List[str]) -> list:
    images = []
    for u in urls:
        try:
            images.append(_preprocess(_download_image(u)).unsqueeze(0))
        except Exception:
            continue
    if not images:
        return []
    batch = torch.cat(images).to(_device)
    with torch.no_grad():
        vec = _model.encode_image(batch)
        vec = vec / vec.norm(dim=-1, keepdim=True)
    return vec.cpu().tolist()  # 2D list
