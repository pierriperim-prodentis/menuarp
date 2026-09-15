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

html_path = os.path.join(os.path.dirname(__file__), "..", "input_painel.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

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
    document.addEventListener('change', function() {
        setTimeout(sendHeight, 150);
        setTimeout(sendHeight, 500);
    });
    var obs = new MutationObserver(sendHeight);
    obs.observe(document.body, {childList: true, subtree: true, attributes: true});
    setInterval(sendHeight, 1000);
})();
</script>
"""
html_content = html_content.replace("</body>", auto_resize + "</body>")

st.components.v1.html(html_content, height=1600, scrolling=False)
