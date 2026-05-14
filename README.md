# SEO Audit Intelligence

Herramienta SEO modular con crawler, normalizacion, auditoria, scoring, embeddings semanticos, recomendaciones de enlazado interno, historico, alertas y dashboard.

## Flujo

```text
Crawler
  -> Adapter
  -> Audit Engine
  -> SEO Scoring
  -> Embeddings
  -> Internal Linking
  -> Output
```

Tambien incluye:

- Historico de cambios por dominio.
- Dashboard en Streamlit.
- Alertas por Slack webhook o email SMTP.
- Clustering de contenidos.
- Content gap contra competidores.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

## Ejecutar con Docker

```bash
docker build -t seo-audit-intelligence .
docker run --rm -p 8501:8501 --env-file .env seo-audit-intelligence
```

## Tests

```bash
pytest
```

## Configuracion opcional

Copia `.env.example` a `.env` y configura alertas:

```env
SLACK_WEBHOOK_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
ALERT_EMAIL_FROM=
ALERT_EMAIL_TO=
```

La primera version usa TF-IDF para embeddings y clustering. Puedes cambiarlo despues por OpenAI embeddings, sentence-transformers u otro proveedor sin tocar el flujo principal.

## Arquitectura

- `seo_toolkit/crawler.py`: rastrea paginas internas.
- `seo_toolkit/adapter.py`: convierte HTML en datos SEO normalizados.
- `seo_toolkit/audit.py`: detecta errores y avisos.
- `seo_toolkit/scoring.py`: calcula score 0-100.
- `seo_toolkit/semantics.py`: genera matriz semantica y clusters.
- `seo_toolkit/internal_linking.py`: recomienda enlaces internos.
- `seo_toolkit/content_gap.py`: compara temas contra competidores.
- `seo_toolkit/tracking.py`: detecta cambios contra la auditoria anterior.
- `seo_toolkit/alerts.py`: envia alertas por Slack o email.
- `app.py`: dashboard Streamlit.
