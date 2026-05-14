from __future__ import annotations

from seo_toolkit.models import NormalizedPage


def audit_pages(pages: list[NormalizedPage]) -> list[dict]:
    issues: list[dict] = []
    for page in pages:
        page.issues = audit_page(page)
        issues.extend(page.issues)
    return issues


def audit_page(page: NormalizedPage) -> list[dict]:
    checks = [
        (page.status_code >= 400 or page.status_code == 0, "critical", "http_status", f"Codigo HTTP {page.status_code}"),
        (not page.title, "critical", "missing_title", "Falta title"),
        (len(page.title) > 60, "warning", "long_title", "Title demasiado largo"),
        (len(page.title) < 25 and bool(page.title), "warning", "short_title", "Title demasiado corto"),
        (not page.meta_description, "warning", "missing_meta_description", "Falta meta description"),
        (len(page.meta_description) > 160, "warning", "long_meta_description", "Meta description demasiado larga"),
        (len(page.h1) == 0, "critical", "missing_h1", "Falta H1"),
        (len(page.h1) > 1, "warning", "multiple_h1", "Hay mas de un H1"),
        (page.word_count < 250, "warning", "thin_content", "Contenido escaso"),
        (not page.canonical, "info", "missing_canonical", "Falta canonical"),
        (page.robots_noindex, "critical", "noindex", "La pagina tiene noindex"),
        (any(not image.get("alt") for image in page.images), "warning", "image_alt_missing", "Hay imagenes sin alt"),
        (len(page.internal_links) == 0, "warning", "orphan_like", "No se detectan enlaces internos salientes"),
    ]
    return [
        {"url": page.url, "severity": severity, "code": code, "message": message}
        for failed, severity, code, message in checks
        if failed
    ]
