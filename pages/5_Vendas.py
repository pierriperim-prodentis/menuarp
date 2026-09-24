import os

import streamlit as st

html_path = os.path.join(os.path.dirname(__file__), "..", "relatorio.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=5100, scrolling=False)
