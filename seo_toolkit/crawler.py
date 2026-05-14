from __future__ import annotations

from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from seo_toolkit.models import CrawledPage


class Crawler:
    def __init__(self, start_url: str, max_pages: int = 25, timeout: int = 10) -> None:
        self.start_url = start_url
        self.max_pages = max_pages
        self.timeout = timeout
        self.domain = urlparse(start_url).netloc
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SEOAuditIntelligence/0.1"})

    def crawl(self) -> list[CrawledPage]:
        queue: deque[tuple[str, int]] = deque([(self.start_url, 0)])
        seen: set[str] = set()
        pages: list[CrawledPage] = []

        while queue and len(pages) < self.max_pages:
            url, depth = queue.popleft()
            url = self._clean_url(url)
            if url in seen or not self._is_internal(url):
                continue
            seen.add(url)

            page = self._fetch(url, depth)
            pages.append(page)

            if page.html and page.status_code < 400:
                for link in self._extract_links(page.html, url):
                    if link not in seen and self._is_internal(link):
                        queue.append((link, depth + 1))

        return pages

    def _fetch(self, url: str, depth: int) -> CrawledPage:
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            content_type = response.headers.get("content-type", "")
            html = response.text if "text/html" in content_type else ""
            return CrawledPage(str(response.url), response.status_code, html, content_type, depth)
        except requests.RequestException as exc:
            return CrawledPage(url, 0, "", "", depth, str(exc))

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all("a", href=True):
            absolute = self._clean_url(urljoin(base_url, tag["href"]))
            if absolute.startswith(("http://", "https://")):
                links.append(absolute)
        return links

    def _clean_url(self, url: str) -> str:
        url, _fragment = urldefrag(url)
        return url.rstrip("/")

    def _is_internal(self, url: str) -> bool:
        return urlparse(url).netloc == self.domain
