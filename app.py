import streamlit as st

st.set_page_config(
    page_title="ARP — Central de Painéis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Esconde o menu/rodapé/cabeçalho padrão do Streamlit
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden; height: 0;}
        [data-testid="stToolbar"] {visibility: hidden;}
        [data-testid="stDecoration"] {visibility: hidden;}
        [data-testid="stSidebarCollapseButton"] {display: none;}
        section[data-testid="stMain"] .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Proteção por chave de acesso na URL (?chave=prodentis2026) ──
CHAVE_CORRETA = "prodentis2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

chave_informada = st.query_params.get("chave", "")
if chave_informada == CHAVE_CORRETA:
    st.session_state.autenticado = True

if not st.session_state.autenticado:
    st.title("🔒 Acesso restrito")
    st.write("Adicione `?chave=SUACHAVE` no final do link para acessar.")
    st.stop()

# ── Navegação entre os painéis ──
pages = [
    st.Page("pages/1_ADM.py", title="ADM", icon="📊", default=True),
    st.Page("pages/2_Funil.py", title="Funil", icon="🎯"),
    st.Page("pages/3_Cursos.py", title="Cursos", icon="🎓"),
    st.Page("pages/4_Fabrica.py", title="Fábrica", icon="🏭"),
    st.Page("pages/5_Vendas.py", title="Vendas", icon="📈"),
    st.Page("pages/6_PainelDiario.py", title="Painel Diário", icon="📅"),
]
nav = st.navigation(pages, position="sidebar")
nav.run()
