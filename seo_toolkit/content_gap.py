from __future__ import annotations

from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer

from seo_toolkit.adapter import normalize_pages
from seo_toolkit.crawler import Crawler
from seo_toolkit.models import NormalizedPage


def find_content_gaps(own_pages: list[NormalizedPage], competitor_urls: list[str], max_pages_per_competitor: int = 8) -> list[dict]:
    if not competitor_urls:
        return []

    competitor_pages: list[NormalizedPage] = []
    for url in competitor_urls:
        crawled = Crawler(url, max_pages=max_pages_per_competitor).crawl()
        competitor_pages.extend(normalize_pages(crawled))

    own_text = " ".join(page.text for page in own_pages)
    competitor_texts = [page.text for page in competitor_pages if page.text]
    if not own_text or not competitor_texts:
        return []

    vectorizer = TfidfVectorizer(max_features=300, ngram_range=(1, 2), stop_words=None)
    vectorizer.fit([own_text, *competitor_texts])
    terms = vectorizer.get_feature_names_out()
    own_vector = vectorizer.transform([own_text]).toarray()[0]
    competitor_matrix = vectorizer.transform(competitor_texts).toarray()
    competitor_vector = competitor_matrix.mean(axis=0)

    missing_scores = competitor_vector - own_vector
    top_indexes = missing_scores.argsort()[-20:][::-1]
    competitor_counter = Counter(page.url for page in competitor_pages if page.text)

    gaps = []
    for index in top_indexes:
        if missing_scores[index] <= 0:
            continue
        term = terms[index]
        examples = [page.url for page in competitor_pages if term.lower() in page.text.lower()][:3]
        gaps.append(
            {
                "topic": term,
                "opportunity_score": round(float(missing_scores[index]), 4),
                "competitor_examples": ", ".join(examples),
                "competitor_pages_checked": sum(competitor_counter.values()),
            }
        )
    return gaps
