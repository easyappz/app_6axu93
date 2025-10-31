import os
import uuid
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

# Basic scraper for Avito listing pages
# NOTE: Avito can be dynamic; this parser tries multiple fallbacks.

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")
LISTINGS_DIR = os.path.join(MEDIA_ROOT, "listings")


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code >= 400:
        raise ValueError(f"Failed to fetch page, status: {resp.status_code}")
    return resp.text


def parse_title_and_image(html: str) -> Tuple[Optional[str], Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    # Title candidates
    title = None
    # og:title
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        title = og_title.get("content").strip()
    # h1
    if not title:
        h1 = soup.find("h1")
        if h1 and h1.get_text():
            title = h1.get_text().strip()
    # <title>
    if not title:
        t = soup.find("title")
        if t and t.get_text():
            title = t.get_text().strip()

    # Image candidates
    image_url = None
    og_img = soup.find("meta", attrs={"property": "og:image"})
    if og_img and og_img.get("content"):
        image_url = og_img.get("content").strip()

    if not image_url:
        # try main img tags
        img = soup.find("img")
        if img and img.get("src"):
            image_url = img.get("src").strip()

    return title, image_url


def _guess_extension_from_url(url: str) -> str:
    lowered = url.lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        if ext in lowered:
            return ext
    return ".jpg"


def download_image(image_url: str) -> str:
    os.makedirs(LISTINGS_DIR, exist_ok=True)
    resp = requests.get(image_url, headers=HEADERS, timeout=30)
    if resp.status_code >= 400:
        raise ValueError("Failed to download image")

    ext = _guess_extension_from_url(image_url)
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(LISTINGS_DIR, filename)

    with open(abs_path, "wb") as f:
        f.write(resp.content)

    # Return relative path used by StaticFiles: 'listings/<filename>'
    return f"listings/{filename}"
