from typing import Optional, Tuple

import os
import uuid
import mimetypes
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AvitologBot/1.0; +https://example.com/bot)"
}

MEDIA_LISTINGS_DIR = os.path.join("server", "media", "listings")


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_title_and_image(html: str) -> Tuple[Optional[str], Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    title: Optional[str] = None
    image_url: Optional[str] = None

    # Prefer Open Graph
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image_url = og_image["content"].strip()

    # Fallbacks
    if not title:
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            h1 = soup.find("h1")
            if h1 and h1.get_text():
                title = h1.get_text().strip()

    if not image_url:
        img = soup.find("img")
        if img and (img.get("src") or img.get("data-src")):
            image_url = (img.get("src") or img.get("data-src")).strip()

    # Normalize protocol-relative URLs
    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url

    return title, image_url


def _guess_extension(content_type: Optional[str], url_path: str) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ext
    base, ext = os.path.splitext(url_path)
    if ext:
        return ext
    return ".jpg"


def _is_image_content_type(content_type: Optional[str]) -> bool:
    if not content_type:
        return False
    return content_type.split(";")[0].strip().lower().startswith("image/")


def download_image(image_url: str) -> str:
    r = requests.get(image_url, headers=DEFAULT_HEADERS, timeout=20, stream=True)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type", "")
    if not _is_image_content_type(content_type):
        raise ValueError("URL content is not an image")
    ext = _guess_extension(content_type, image_url)
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(MEDIA_LISTINGS_DIR, exist_ok=True)
    filepath = os.path.join(MEDIA_LISTINGS_DIR, filename)
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    relative_path = os.path.join("listings", filename).replace("\\", "/")
    return relative_path
