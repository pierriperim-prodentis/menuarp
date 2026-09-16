import os

import streamlit as st

st.markdown(
    """
    <style>
        section[data-testid="stMain"] .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

html_path = os.path.join(os.path.dirname(__file__), "..", "painel_mes.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=2500, scrolling=False)
