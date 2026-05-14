from __future__ import annotations

from dataclasses import dataclass, field

from seo_toolkit.adapter import normalize_pages
from seo_toolkit.audit import audit_pages
from seo_toolkit.content_gap import find_content_gaps
from seo_toolkit.crawler import Crawler
from seo_toolkit.internal_linking import recommend_internal_links
from seo_toolkit.models import AuditResult
from seo_toolkit.scoring import score_pages
from seo_toolkit.semantics import build_semantics, cluster_pages, similarity_matrix
from seo_toolkit.storage import load_snapshot, save_history, save_snapshot
from seo_toolkit.tracking import detect_changes


@dataclass
class AuditConfig:
    start_url: str
    max_pages: int = 25
    competitor_urls: list[str] = field(default_factory=list)


def run_audit(config: AuditConfig) -> AuditResult:
    crawled_pages = Crawler(config.start_url, max_pages=config.max_pages).crawl()
    pages = normalize_pages(crawled_pages)
    issues = audit_pages(pages)
    score_pages(pages)

    matrix, vectorizer = build_semantics(pages)
    similarities = similarity_matrix(matrix)
    internal_linking = recommend_internal_links(pages, similarities)
    clusters = cluster_pages(pages, matrix, vectorizer)
    content_gaps = find_content_gaps(pages, config.competitor_urls)
    previous_snapshot = load_snapshot(config.start_url)
    changes = detect_changes(previous_snapshot, pages, issues)

    summary = {
        "pages": len(pages),
        "average_score": sum(page.score for page in pages) / len(pages) if pages else 0,
        "critical_issues": sum(1 for issue in issues if issue["severity"] == "critical"),
        "warnings": sum(1 for issue in issues if issue["severity"] == "warning"),
    }
    alerts = [
        f"{issue['url']} - {issue['message']}"
        for issue in issues
        if issue["severity"] == "critical"
    ][:20]
    alerts.extend(change["detail"] + f" - {change['url']}" for change in changes if "caida de score" in change["detail"])
    save_history(config.start_url, summary)
    save_snapshot(config.start_url, [page.to_dict() for page in pages], issues)

    return AuditResult(
        pages=pages,
        issues=issues,
        internal_linking=internal_linking,
        clusters=clusters,
        content_gaps=content_gaps,
        changes=changes,
        alerts=alerts,
        summary=summary,
    )
