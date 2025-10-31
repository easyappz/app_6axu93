from pathlib import Path
from typing import Optional, Tuple
import uuid

import requests
from bs4 import BeautifulSoup

# Simple scraper using requests + BeautifulSoup. No regex unless necessary.
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

MEDIA_LISTINGS_DIR = Path(__file__).resolve().parents[1] / "media" / "listings"


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_title_and_image(html: str) -> Tuple[Optional[str], Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    # Try OpenGraph metadata first
    title_tag = soup.find("meta", property="og:title")
    image_tag = soup.find("meta", property="og:image")

    title: Optional[str] = title_tag.get("content").strip() if title_tag and title_tag.get("content") else None
    image_url: Optional[str] = image_tag.get("content").strip() if image_tag and image_tag.get("content") else None

    # Fallbacks
    if not title:
        h1 = soup.find("h1")
        if h1 and h1.text:
            title = h1.get_text(strip=True)

    if not image_url:
        # Try first <img> with plausible attributes
        img = soup.find("img")
        if img and (img.get("src") or img.get("data-src")):
            image_url = img.get("src") or img.get("data-src")

    return title, image_url


def _infer_ext_from_content_type(content_type: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get(content_type.lower(), ".jpg")


def download_image(image_url: str) -> str:
    MEDIA_LISTINGS_DIR.mkdir(parents=True, exist_ok=True)

    with requests.get(image_url, headers=DEFAULT_HEADERS, timeout=30, stream=True) as r:
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        ext = _infer_ext_from_content_type(content_type)
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = MEDIA_LISTINGS_DIR / filename
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    # Return relative path under /media
    relative_path = f"listings/{filename}"
    return relative_path
