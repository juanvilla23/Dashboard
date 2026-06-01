from typing import Optional

import streamlit as st


def render_html(html: str, *, height: Optional[int] = None) -> None:
    """Renderiza HTML personalizado (compatible con distintas versiones de Streamlit)."""
    if hasattr(st, "html"):
        st.html(html)
        return

    import streamlit.components.v1 as components

    components.html(html, height=height or 120, scrolling=False)
