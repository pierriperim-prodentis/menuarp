import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HTML_PATH = Path(__file__).parent.parent / "Dashboard_ADM.html"
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

components.html(html_content, height=1400, scrolling=False)
