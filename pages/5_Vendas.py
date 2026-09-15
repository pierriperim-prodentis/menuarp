import os

import streamlit as st

st.markdown(
    """
    <style>
        .block-container { padding: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

html_path = os.path.join(os.path.dirname(__file__), "..", "relatorio.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=1400, scrolling=True)
