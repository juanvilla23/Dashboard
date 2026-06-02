import streamlit as st

from ui.render import render_html
from ui.theme import render_global_styles, render_theme_runtime, view_href
from views.segmentacion import render_indicadores_clave
from views.vista_1 import render_vista_1
from views.vista_2 import render_vista_2
from views.vista_3 import render_vista_3
from views.vista_4 import render_vista_4

VIEWS = [
    {"id": "1", "icon": "▥", "title": "Riesgo y volumen"},
    {"id": "2", "icon": "↗", "title": "Conducta crediticia"},
    {"id": "3", "icon": "◔", "title": "Simulador de corte"},
    {"id": "4", "icon": "◎", "title": "Perfilador de riesgo"},
]

VIEW_RENDERERS = {
    "1": render_vista_1,
    "2": render_vista_2,
    "3": render_vista_3,
    "4": render_vista_4,
}


st.set_page_config(
    page_title="Home Credit Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_global_styles()
render_theme_runtime()

if "_dashboard_theme" not in st.session_state:
    st.session_state._dashboard_theme = "dark"


def render_view_tabs(active_view: str) -> str:
    cards = []
    for view in VIEWS:
        active_class = "active" if active_view == view["id"] else ""
        cards.append(
            f"""
            <a class="view-card {active_class}" href="{view_href(view['id'])}" target="_self">
                <div class="view-icon">{view["icon"]}</div>
                <div>
                    <div class="view-title">{view["title"]}</div>
                </div>
            </a>
            """
        )

    render_html(
        f"""
        <div class="view-tabs">
            {''.join(cards)}
        </div>
        """
    )

    return active_view


def render_placeholder(view_number: str, title: str) -> None:
    render_html(
        f"""
        <div class="placeholder">
            <h2>Vista {view_number}: {title}</h2>
            <p>Esta sección se implementará en su propio archivo.</p>
        </div>
        """
    )


active_view = str(st.query_params.get("view", "1"))
active_view = render_view_tabs(active_view)

if active_view != "4":
    render_indicadores_clave()

render_view = VIEW_RENDERERS.get(active_view, render_vista_1)
render_view()
