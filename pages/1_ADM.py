import os

import streamlit as st
import streamlit.components.v1 as components

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "Dashboard_ADM.html")

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=6000, scrolling=False)
