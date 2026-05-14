from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from seo_toolkit.models import CrawledPage, NormalizedPage


def normalize_pages(crawled_pages: list[CrawledPage]) -> list[NormalizedPage]:
    return [normalize_page(page) for page in crawled_pages]


def normalize_page(page: CrawledPage) -> NormalizedPage:
    soup = BeautifulSoup(page.html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = (soup.title.string or "").strip() if soup.title else ""
    meta_description = _meta_content(soup, "description")
    robots = _meta_content(soup, "robots").lower()
    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical = urljoin(page.url, canonical_tag.get("href", "")) if canonical_tag else ""
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
    words = re.findall(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ-]+\b", text)

    internal_links: list[str] = []
    external_links: list[str] = []
    page_domain = urlparse(page.url).netloc
    for anchor in soup.find_all("a", href=True):
        link = urljoin(page.url, anchor["href"]).split("#")[0].rstrip("/")
        if not link.startswith(("http://", "https://")):
            continue
        if urlparse(link).netloc == page_domain:
            internal_links.append(link)
        else:
            external_links.append(link)

    images = []
    for image in soup.find_all("img"):
        images.append({"src": urljoin(page.url, image.get("src", "")), "alt": image.get("alt", "")})

    return NormalizedPage(
        url=page.url,
        status_code=page.status_code,
        title=title,
        meta_description=meta_description,
        h1=[tag.get_text(" ", strip=True) for tag in soup.find_all("h1")],
        h2=[tag.get_text(" ", strip=True) for tag in soup.find_all("h2")],
        canonical=canonical,
        word_count=len(words),
        text=text,
        internal_links=sorted(set(internal_links)),
        external_links=sorted(set(external_links)),
        images=images,
        robots_noindex="noindex" in robots,
    )


def _meta_content(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"name": name})
    return tag.get("content", "").strip() if tag else ""
