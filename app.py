import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Cursos - Pródentis",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        footer { display:none !important; }
        .block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
        section[data-testid="stMain"] > div { padding:0 !important; }
        iframe { border:none !important; }
    </style>
""", unsafe_allow_html=True)

# Proteção por chave na URL
chave = st.query_params.get("chave", "")
CHAVES_VALIDAS = {"prodentis2026", "ARP2026"}
if chave not in CHAVES_VALIDAS:
    st.error("🔒 Acesso restrito. URL inválida.")
    st.stop()

html_content = Path("Dashboard_Cursos_2026.html").read_text(encoding="utf-8")
st.components.v1.html(html_content, height=4200, scrolling=True)



