from seo_toolkit.adapter import normalize_pages
from seo_toolkit.audit import audit_pages
from seo_toolkit.models import CrawledPage
from seo_toolkit.scoring import score_pages
from seo_toolkit.semantics import build_semantics, cluster_pages, similarity_matrix
from seo_toolkit.internal_linking import recommend_internal_links


def test_audit_pipeline_without_network():
    crawled = [
        CrawledPage(
            url="https://example.com",
            status_code=200,
            html="""
            <html>
              <head>
                <title>Guia completa de SEO tecnico para ecommerce</title>
                <meta name="description" content="Aprende SEO tecnico para tiendas online.">
                <link rel="canonical" href="https://example.com">
              </head>
              <body>
                <h1>SEO tecnico para ecommerce</h1>
                <h2>Crawl budget</h2>
                <p>Contenido sobre rastreo, indexacion, categorias, productos y arquitectura interna.</p>
                <a href="/blog/arquitectura-seo">Arquitectura SEO</a>
                <img src="/hero.jpg" alt="Panel SEO">
              </body>
            </html>
            """,
        ),
        CrawledPage(
            url="https://example.com/blog/arquitectura-seo",
            status_code=200,
            html="""
            <html>
              <head><title>Arquitectura SEO para enlazado interno</title></head>
              <body>
                <h1>Arquitectura SEO</h1>
                <p>Arquitectura web, clusters, enlazado interno, categorias y profundidad de clic.</p>
              </body>
            </html>
            """,
        ),
    ]

    pages = normalize_pages(crawled)
    issues = audit_pages(pages)
    score_pages(pages)
    matrix, vectorizer = build_semantics(pages)
    similarities = similarity_matrix(matrix)
    clusters = cluster_pages(pages, matrix, vectorizer)
    links = recommend_internal_links(pages, similarities)

    assert len(pages) == 2
    assert pages[0].score <= 100
    assert isinstance(issues, list)
    assert isinstance(clusters, list)
    assert isinstance(links, list)
