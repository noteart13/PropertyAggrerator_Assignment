import re, json, time
from typing import List
from bs4 import BeautifulSoup
from app.utils.http import client
from app.schemas import PropertyItem

DOMAIN = "https://www.domain.com.au/"

def _parse_listing_page(html: str, url: str) -> PropertyItem:
    soup = BeautifulSoup(html, "html.parser")
    item = PropertyItem(source="domain", url=url)

    # JSON-LD (nhiều trang BĐS đều nhúng)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.text.strip())
            if isinstance(data, dict):
                data = [data]
            for d in data:
                if "address" in d:
                    item.address = d.get("address", {}).get("streetAddress") or item.address
                if "name" in d and not item.title:
                    item.title = d["name"]
                if "image" in d:
                    imgs = d["image"]
                    if isinstance(imgs, list):
                        item.image_urls.extend(imgs)
                if "offers" in d and isinstance(d["offers"], dict):
                    item.price = d["offers"].get("price") or d["offers"].get("priceSpecification", {}).get("price")
        except Exception:
            pass

    # fallback: meta og
    if not item.title and (og := soup.find("meta", property="og:title")):
        item.title = og.get("content")
    if not item.image_urls and (ogimg := soup.find("meta", property="og:image")):
        item.image_urls.append(ogimg.get("content"))

    # thô sơ: tìm "x bed", "x bath", "x car"
    text = soup.get_text(" ", strip=True).lower()
    bed = re.search(r"(\d+(\.\d+)?)\s*bed", text)
    bath = re.search(r"(\d+(\.\d+)?)\s*bath", text)
    car = re.search(r"(\d+(\.\d+)?)\s*(car|garage|parking)", text)
    item.bedrooms = float(bed.group(1)) if bed else None
    item.bathrooms = float(bath.group(1)) if bath else None
    item.parking  = float(car.group(1)) if car else None
    return item

def search_by_address(address: str, max_results: int = 5) -> List[PropertyItem]:
    # thử endpoint tìm kiếm chung
    q = address.replace(" ", "+")
    search_urls = [
        f"{DOMAIN}/sale/?q={q}",
        f"{DOMAIN}/rent/?q={q}",
    ]
    items: List[PropertyItem] = []
    with client() as c:
        for surl in search_urls:
            r = c.get(surl)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/"):
                    href = DOMAIN + href
                if "domain.com.au" in href and any(k in href for k in ["property", "listing", "/sale/"]):
                    try:
                        # tải trang chi tiết và parse
                        page = c.get(href)
                        item = _parse_listing_page(page.text, href)
                        if item.address or item.title:
                            items.append(item)
                            if len(items) >= max_results:
                                return items
                        time.sleep(0.5)  # nhẹ tay
                    except Exception:
                        continue
    return items
