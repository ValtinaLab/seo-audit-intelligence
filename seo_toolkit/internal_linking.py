from __future__ import annotations

import numpy as np

from seo_toolkit.models import NormalizedPage


def recommend_internal_links(pages: list[NormalizedPage], similarities: np.ndarray, limit: int = 20) -> list[dict]:
    if len(pages) < 2 or similarities.size == 0:
        return []

    existing = {(source.url, target) for source in pages for target in source.internal_links}
    recommendations: list[dict] = []

    for i, source in enumerate(pages):
        candidates = np.argsort(similarities[i])[::-1]
        for j in candidates:
            if i == j:
                continue
            target = pages[j]
            if (source.url, target.url) in existing:
                continue
            score = float(similarities[i][j])
            if score < 0.12:
                continue
            recommendations.append(
                {
                    "source_url": source.url,
                    "target_url": target.url,
                    "similarity": round(score, 3),
                    "suggested_anchor": target.h1[0] if target.h1 else target.title[:80] or target.url,
                    "reason": "Alta similitud semantica y sin enlace interno detectado",
                }
            )
            break

    return sorted(recommendations, key=lambda item: item["similarity"], reverse=True)[:limit]
