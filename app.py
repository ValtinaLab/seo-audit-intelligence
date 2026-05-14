from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from seo_toolkit.alerts import send_alerts
from seo_toolkit.pipeline import AuditConfig, run_audit
from seo_toolkit.storage import load_history


load_dotenv()

st.set_page_config(page_title="SEO Audit Intelligence", page_icon="SEO", layout="wide")


def normalize_start_url(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def domain_key(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "") or "sitio"


st.sidebar.title("SEO Audit Intelligence")
start_url = normalize_start_url(st.sidebar.text_input("URL inicial", "https://example.com"))
max_pages = st.sidebar.slider("Paginas maximas", 3, 200, 25)
competitors_text = st.sidebar.text_area(
    "Competidores (una URL por linea)",
    placeholder="https://competidor.com\nhttps://otrocompetidor.com",
)
send_notifications = st.sidebar.checkbox("Enviar alertas si hay errores criticos", value=False)
run_button = st.sidebar.button("Ejecutar auditoria", type="primary")

tabs = st.tabs(["Auditoria", "Historico", "Clustering", "Gaps", "Datos"])

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if run_button:
    competitors = [normalize_start_url(line) for line in competitors_text.splitlines() if line.strip()]
    with st.spinner("Rastreando, auditando y calculando recomendaciones..."):
        config = AuditConfig(start_url=start_url, max_pages=max_pages, competitor_urls=competitors)
        result = run_audit(config)
        st.session_state.last_result = result
    if send_notifications:
        sent = send_alerts(result.alerts)
        if sent:
            st.sidebar.success("Alertas enviadas")
        else:
            st.sidebar.info("No se enviaron alertas. Revisa configuracion o no habia alertas.")

result = st.session_state.last_result

with tabs[0]:
    st.header("Auditoria SEO")
    if not result:
        st.info("Ejecuta una auditoria desde la barra lateral para ver resultados.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Score medio", f"{result.summary['average_score']:.0f}/100")
        col2.metric("Paginas rastreadas", result.summary["pages"])
        col3.metric("Errores criticos", result.summary["critical_issues"])
        col4.metric("Avisos", result.summary["warnings"])

        issues_df = pd.DataFrame(result.issues)
        pages_df = pd.DataFrame([page.to_dict() for page in result.pages])

        st.subheader("Score por pagina")
        if not pages_df.empty:
            fig = px.bar(pages_df.sort_values("score"), x="url", y="score", color="score", range_y=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Errores SEO")
        if issues_df.empty:
            st.success("No se encontraron errores.")
        else:
            st.dataframe(issues_df, use_container_width=True, hide_index=True)

        st.subheader("Recomendaciones de enlazado interno")
        links_df = pd.DataFrame(result.internal_linking)
        if links_df.empty:
            st.info("No hay suficientes paginas para recomendar enlaces internos.")
        else:
            st.dataframe(links_df, use_container_width=True, hide_index=True)

        st.subheader("Cambios desde la auditoria anterior")
        changes_df = pd.DataFrame(result.changes)
        if changes_df.empty:
            st.info("No hay auditoria anterior comparable o no se detectaron cambios relevantes.")
        else:
            st.dataframe(changes_df, use_container_width=True, hide_index=True)

with tabs[1]:
    st.header("Historico de cambios")
    key = domain_key(start_url)
    history = load_history(key)
    if not history:
        st.info("Aun no hay historico para este dominio.")
    else:
        history_df = pd.DataFrame(history)
        history_df["created_at"] = pd.to_datetime(history_df["created_at"])
        st.line_chart(history_df.set_index("created_at")[["average_score", "critical_issues", "warnings"]])
        st.dataframe(history_df.sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)

with tabs[2]:
    st.header("Clustering de contenidos")
    if not result or not result.clusters:
        st.info("Ejecuta una auditoria para ver clusters.")
    else:
        for cluster in result.clusters:
            with st.expander(f"Cluster {cluster['cluster']} - {cluster['label']}"):
                st.write(", ".join(cluster["keywords"]))
                st.dataframe(pd.DataFrame(cluster["pages"]), use_container_width=True, hide_index=True)

with tabs[3]:
    st.header("Content gap vs competidores")
    if not result:
        st.info("Ejecuta una auditoria con competidores para calcular gaps.")
    elif not result.content_gaps:
        st.info("No se detectaron gaps o no se indicaron competidores.")
    else:
        st.dataframe(pd.DataFrame(result.content_gaps), use_container_width=True, hide_index=True)

with tabs[4]:
    st.header("Datos normalizados")
    if not result:
        st.info("Sin datos todavia.")
    else:
        pages_df = pd.DataFrame([page.to_dict() for page in result.pages])
        st.download_button(
            "Descargar CSV",
            pages_df.to_csv(index=False).encode("utf-8"),
            file_name=f"seo-audit-{domain_key(start_url)}-{datetime.utcnow().date()}.csv",
            mime="text/csv",
        )
        st.dataframe(pages_df, use_container_width=True, hide_index=True)
