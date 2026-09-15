import os

import streamlit as st

html_path = os.path.join(os.path.dirname(__file__), "..", "relatorio.html")
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
    var obs = new MutationObserver(sendHeight);
    obs.observe(document.body, {childList: true, subtree: true, attributes: true});
})();
</script>
"""
html_content = html_content.replace("</body>", auto_resize + "</body>")

st.components.v1.html(html_content, height=1400, scrolling=False)
