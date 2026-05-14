from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class CrawledPage:
    url: str
    status_code: int
    html: str
    content_type: str = ""
    depth: int = 0
    error: str = ""


@dataclass
class NormalizedPage:
    url: str
    status_code: int
    title: str
    meta_description: str
    h1: list[str]
    h2: list[str]
    canonical: str
    word_count: int
    text: str
    internal_links: list[str]
    external_links: list[str]
    images: list[dict[str, str]]
    robots_noindex: bool
    score: float = 0.0
    issues: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["h1"] = " | ".join(self.h1)
        data["h2"] = " | ".join(self.h2[:8])
        data["internal_links"] = len(self.internal_links)
        data["external_links"] = len(self.external_links)
        data["images"] = len(self.images)
        data["issues"] = len(self.issues)
        return data


@dataclass
class AuditResult:
    pages: list[NormalizedPage]
    issues: list[dict]
    internal_linking: list[dict]
    clusters: list[dict]
    content_gaps: list[dict]
    changes: list[dict]
    alerts: list[str]
    summary: dict
