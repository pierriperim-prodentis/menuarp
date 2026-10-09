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

        /* Esconde o botão de recolher a barra lateral só em telas grandes
           (no celular ele precisa continuar visível, senão não dá pra
           abrir o menu depois que ele recolhe sozinho) */
        @media (min-width: 768px) {
            [data-testid="stSidebarCollapseButton"] {display: none;}
        }

        section[data-testid="stMain"] .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Proteção por chave de acesso na URL ──
CHAVE_CORRETA = "prodentis2026"   # abre a navegação normal (todos os painéis)
CHAVE_INPUT = "ARP2026"           # abre só o formulário de lançamento diário

chave_informada = st.query_params.get("chave", "")

# Chave do formulário: serve o input_painel.html sozinho, sem sidebar/navegação
if chave_informada == CHAVE_INPUT:
    import os
    html_path = os.path.join(os.path.dirname(__file__), "input_painel.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=1600, scrolling=True)
    st.stop()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

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
