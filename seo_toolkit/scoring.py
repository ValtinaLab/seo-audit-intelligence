from __future__ import annotations

from seo_toolkit.models import NormalizedPage


WEIGHTS = {
    "critical": 18,
    "warning": 7,
    "info": 2,
}


def score_pages(pages: list[NormalizedPage]) -> None:
    for page in pages:
        penalty = sum(WEIGHTS.get(issue["severity"], 0) for issue in page.issues)
        if page.status_code == 0:
            penalty += 30
        page.score = max(0, min(100, 100 - penalty))
