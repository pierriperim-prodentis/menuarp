import os

import streamlit as st
import streamlit.components.v1 as components

st.markdown(
    """
    <style>
        .block-container {padding: 0 !important; max-width: 100% !important;}
        iframe {border: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "Dashboard_ADM.html")

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=1400, scrolling=True)
