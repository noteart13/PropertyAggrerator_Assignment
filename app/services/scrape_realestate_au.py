import re, json, time
from typing import List
from bs4 import BeautifulSoup
from app.utils.http import client
from app.schemas import PropertyItem

BASE = "https://www.realestate.com.au"

def _parse_listing_page(html: str, url: str) -> PropertyItem:
    soup = BeautifulSoup(html, "html.parser")
    item = PropertyItem(source="realestate", url=url)

    # NEXT_DATA hoặc JSON-LD
    for script in soup.find_all("script"):
        t = (script.get("type") or "").lower()
        if "ld+json" in t:
            try:
                data = json.loads(script.text.strip())
                if isinstance(data, dict):
                    data = [data]
                for d in data:
                    if "address" in d:
                        addr = d["address"]
                        if isinstance(addr, dict):
                            item.address = addr.get("streetAddress") or item.address
                    if "name" in d and not item.title:
                        item.title = d["name"]
                    if "image" in d:
                        imgs = d["image"]
                        if isinstance(imgs, list):
                            item.image_urls.extend(imgs)
            except Exception:
                pass

    if not item.title:
        ogt = soup.find("meta", property="og:title")
        if ogt: item.title = ogt.get("content")
    if not item.image_urls:
        ogi = soup.find("meta", property="og:image")
        if ogi: item.image_urls.append(ogi.get("content"))

    text = soup.get_text(" ", strip=True).lower()
    bed = re.search(r"(\d+(\.\d+)?)\s*bed", text)
    bath = re.search(r"(\d+(\.\d+)?)\s*bath", text)
    car = re.search(r"(\d+(\.\d+)?)\s*(car|garage|parking)", text)
    item.bedrooms = float(bed.group(1)) if bed else None
    item.bathrooms = float(bath.group(1)) if bath else None
    item.parking  = float(car.group(1)) if car else None
    return item

def search_by_address(address: str, max_results: int = 5) -> List[PropertyItem]:
    q = address.replace(" ", "+")
    search_urls = [
        f"{BASE}/buy/?includeSurrounding=false&keywords={q}",
        f"{BASE}/rent/?includeSurrounding=false&keywords={q}",
    ]
    items: List[PropertyItem] = []
    with client() as c:
        for surl in search_urls:
            r = c.get(surl)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/"): href = BASE + href
                if "realestate.com.au" in href and any(k in href for k in ["property", "buy", "property-house", "listing"]):
                    try:
                        page = c.get(href)
                        item = _parse_listing_page(page.text, href)
                        if item.address or item.title:
                            items.append(item)
                            if len(items) >= max_results:
                                return items
                        time.sleep(0.5)
                    except Exception:
                        continue
    return items
