from __future__ import annotations

from seo_toolkit.models import NormalizedPage


def detect_changes(previous: dict | None, pages: list[NormalizedPage], issues: list[dict]) -> list[dict]:
    if not previous:
        return []

    old_pages = {page["url"]: page for page in previous.get("pages", [])}
    new_pages = {page.url: page for page in pages}
    old_issues = {
        (issue["url"], issue["code"], issue["severity"])
        for issue in previous.get("issues", [])
    }
    new_issues = {(issue["url"], issue["code"], issue["severity"]) for issue in issues}

    changes: list[dict] = []
    for url, page in new_pages.items():
        if url not in old_pages:
            changes.append({"type": "new_page", "url": url, "detail": "Pagina nueva detectada"})
            continue
        old_score = float(old_pages[url].get("score", 0))
        diff = round(page.score - old_score, 1)
        if abs(diff) >= 5:
            direction = "mejora" if diff > 0 else "caida"
            changes.append({"type": "score_change", "url": url, "detail": f"{direction} de score: {diff:+.1f}"})

    for url in sorted(set(old_pages) - set(new_pages)):
        changes.append({"type": "removed_page", "url": url, "detail": "Pagina ya no encontrada en el rastreo"})

    for url, code, severity in sorted(new_issues - old_issues):
        changes.append({"type": "new_issue", "url": url, "detail": f"Nuevo error {severity}: {code}"})

    return changes[:100]
