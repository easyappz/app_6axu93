import os
import re
import uuid
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")
LISTINGS_DIR = os.path.join(MEDIA_ROOT, "listings")


@dataclass
class ParsedData:
    title: Optional[str]
    image_url: Optional[str]


def fetch_html(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_title_and_image(html: str) -> ParsedData:
    soup = BeautifulSoup(html, "html.parser")

    # Prefer OpenGraph metadata
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_image = soup.find("meta", attrs={"property": "og:image"})

    title = og_title["content"].strip() if og_title and og_title.get("content") else None
    image_url = og_image["content"].strip() if og_image and og_image.get("content") else None

    if not title:
        t = soup.find("title")
        if t and t.text:
            title = t.text.strip()

    if not image_url:
        # try to find first reasonably-sized image
        img = soup.find("img")
        if img and img.get("src"):
            image_url = img["src"]

    return ParsedData(title=title, image_url=image_url)


def _guess_ext_from_url(url: str) -> str:
    path = urlparse(url).path
    basename = os.path.basename(path)
    m = re.search(r"\.(jpg|jpeg|png|webp|gif)(?:$|\?)", basename, re.IGNORECASE)
    if m:
        return "." + m.group(1).lower()
    return ".jpg"


def download_image(image_url: str) -> str:
    os.makedirs(LISTINGS_DIR, exist_ok=True)
    ext = _guess_ext_from_url(image_url)
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(LISTINGS_DIR, filename)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.avito.ru/",
    }
    with requests.get(image_url, headers=headers, stream=True, timeout=20) as r:
        r.raise_for_status()
        with open(abs_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    # Return relative path for DB storage (relative to /media/)
    return f"listings/{filename}"
