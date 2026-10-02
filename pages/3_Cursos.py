from pathlib import Path

import streamlit as st

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: #f8f4fc !important;
        }
        iframe {
            display: block;
            border: none !important;
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

HTML_PATH = Path(__file__).parent.parent / "Dashboard_Cursos_2026.html"
html_content = HTML_PATH.read_text(encoding="utf-8")

auto_resize = """
<script>
(function() {
    function sendHeight() {
        var h = document.body.scrollHeight || document.documentElement.scrollHeight;
        window.parent.postMessage({type: 'streamlit:setFrameHeight', height: h}, '*');
    }
    window.addEventListener('load', function() {
        sendHeight();
        setTimeout(sendHeight, 500);
        setTimeout(sendHeight, 1500);
    });
    window.addEventListener('resize', sendHeight);
    var obs = new MutationObserver(sendHeight);
    obs.observe(document.body, {childList: true, subtree: true, attributes: true});
})();
</script>
"""
html_content = html_content.replace("</body>", auto_resize + "</body>")

st.components.v1.html(html_content, height=2500, scrolling=False)
