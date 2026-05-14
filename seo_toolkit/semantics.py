from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from seo_toolkit.models import NormalizedPage


def build_semantics(pages: list[NormalizedPage]) -> tuple[np.ndarray, TfidfVectorizer | None]:
    documents = [page.text or page.title or page.url for page in pages]
    if not documents:
        return np.empty((0, 0)), None
    vectorizer = TfidfVectorizer(max_features=800, stop_words=None, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents)
    return matrix, vectorizer


def cluster_pages(pages: list[NormalizedPage], matrix, vectorizer: TfidfVectorizer | None) -> list[dict]:
    if not pages or vectorizer is None or len(pages) < 2:
        return []

    cluster_count = min(6, max(2, round(len(pages) ** 0.5)))
    labels = KMeans(n_clusters=cluster_count, n_init="auto", random_state=42).fit_predict(matrix)
    terms = np.array(vectorizer.get_feature_names_out())
    clusters: list[dict] = []

    for cluster_id in sorted(set(labels)):
        indexes = np.where(labels == cluster_id)[0]
        centroid = np.asarray(matrix[indexes].mean(axis=0)).ravel()
        top_terms = terms[centroid.argsort()[-6:][::-1]].tolist()
        clusters.append(
            {
                "cluster": int(cluster_id),
                "label": top_terms[0] if top_terms else f"Cluster {cluster_id}",
                "keywords": top_terms,
                "pages": [{"url": pages[i].url, "title": pages[i].title, "score": pages[i].score} for i in indexes],
            }
        )
    return clusters


def similarity_matrix(matrix) -> np.ndarray:
    if matrix.shape[0] == 0:
        return np.empty((0, 0))
    return cosine_similarity(matrix)
