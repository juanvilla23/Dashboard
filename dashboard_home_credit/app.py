import streamlit as st

from ui.render import render_html
from views.vista_1 import render_vista_1


st.set_page_config(
    page_title="Home Credit Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(229, 57, 53, 0.08), transparent 30%),
            #0d0d0d;
        color: #f4f4f4;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1.5rem;
        max-width: 1680px;
    }

    section[data-testid="stSidebar"] {
        background: #0b0b0b;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 0.8rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 6px 20px 6px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 10px;
    }

    .brand-icon {
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1.5px solid #e53935;
        color: #e53935;
        font-size: 18px;
        border-radius: 6px;
    }

    .brand-title {
        color: #ffffff;
        font-size: 20px;
        font-weight: 700;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 14px;
        border-radius: 10px;
        margin-bottom: 4px;
        color: #9aa3af;
        font-size: 14px;
        border: 1px solid transparent;
    }

    .sidebar-item.active {
        background: linear-gradient(90deg, rgba(229, 57, 53, 0.85), rgba(183, 28, 28, 0.75));
        color: #ffffff;
        border-color: rgba(255, 82, 82, 0.35);
    }

    .sidebar-bottom {
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.08);
        color: #8b949e;
        font-size: 13px;
        line-height: 1.8;
    }

    .top-header {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }

    .date-pill {
        background: #1a1a1a;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px;
        padding: 9px 14px;
        color: #d1d5db;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .export-btn {
        background: #1a1a1a;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px;
        padding: 9px 16px;
        color: #d1d5db;
        font-size: 13px;
        cursor: pointer;
    }

    .view-tabs {
        display: flex;
        gap: 14px;
        margin-bottom: 10px;
    }

    .view-card {
        flex: 1;
        max-width: 280px;
        min-height: 78px;
        padding: 14px 16px;
        border-radius: 10px 10px 0 0;
        border: 1px solid rgba(255,255,255,0.10);
        background: #1a1a1a;
        color: #d7dde5 !important;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 14px;
        transition: 0.2s ease;
    }

    .view-card:hover {
        border-color: rgba(229, 57, 53, 0.5);
    }

    .view-card.active {
        border-color: #e53935;
        background: linear-gradient(145deg, rgba(50, 20, 24, 0.95), rgba(26, 26, 26, 0.98));
        box-shadow: 0 0 18px rgba(229, 57, 53, 0.12);
    }

    .view-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: rgba(255,255,255,0.06);
        font-size: 18px;
        flex-shrink: 0;
    }

    .view-card.active .view-icon {
        background: rgba(229, 57, 53, 0.18);
        color: #e53935;
    }

    .view-title {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
    }

    .view-card.active .view-title {
        color: #ff5252;
    }

    .view-subtitle {
        display: block;
        margin-top: 2px;
        font-size: 12px;
        color: #9aa3af;
    }

    .info-banner {
        background: #1a1a1a;
        border: 1px solid rgba(255,255,255,0.08);
        color: #9aa3af;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 13px;
    }

    .info-banner strong {
        color: #ff5252;
    }

    .panel-box {
        background: #1a1a1a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 16px;
    }

    .panel-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 12px;
    }

    .panel-subtitle {
        color: #e53935;
        font-size: 13px;
        font-weight: 600;
        margin-top: -8px;
        margin-bottom: 14px;
    }

    .filter-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .filter-clear {
        color: #e53935;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
    }

    .kpi-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .kpi-card:last-of-type {
        border-bottom: none;
    }

    .kpi-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #e53935, #b71c1c);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 17px;
        font-weight: 700;
        flex-shrink: 0;
    }

    .kpi-label {
        color: #9aa3af;
        font-size: 12px;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 20px;
        font-weight: 700;
        margin-top: 2px;
    }

    .kpi-delta {
        margin-left: auto;
        color: #e53935;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
    }

    .kpi-link {
        display: block;
        margin-top: 12px;
        color: #9aa3af;
        font-size: 12px;
        text-decoration: none;
    }

    .chart-panel {
        background: #1a1a1a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 16px 18px 8px 18px;
    }

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }

    .chart-footer {
        border: 1px dashed rgba(229, 57, 53, 0.55);
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 10px;
        color: #9aa3af;
        font-size: 13px;
        background: rgba(229, 57, 53, 0.03);
    }

    .placeholder {
        padding: 60px 25px;
        border-radius: 12px;
        border: 1px dashed rgba(229, 57, 53, 0.45);
        background: rgba(255,255,255,0.02);
        text-align: center;
        color: #c6ced8;
    }

    .placeholder h2 {
        color: #ff5252;
        font-size: 20px;
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input {
        background-color: #121212 !important;
        border-color: rgba(255,255,255,0.10) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    div[data-testid="stMetric"] {
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 10px 0;
    }

    div[data-testid="stMetricLabel"] {
        color: #9aa3af !important;
        font-size: 12px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    div[data-testid="stButton"] button {
        background: #1a1a1a !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        color: #d1d5db !important;
        border-radius: 8px !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #e53935, #b71c1c) !important;
        border-color: #e53935 !important;
        color: #ffffff !important;
    }

    div[data-testid="stPlotlyChart"] {
        background: transparent;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #1a1a1a;
        border-color: rgba(255,255,255,0.08) !important;
        border-radius: 10px;
        padding: 4px 8px;
    }

    div[data-testid="column"] .panel-inner {
        padding: 4px 2px;
    }
    """
)


def render_sidebar() -> None:
    with st.sidebar:
        render_html(
            """
            <div class="brand">
                <div class="brand-icon">▥</div>
                <div class="brand-title">Analytics</div>
            </div>

            <div class="sidebar-item active">▦ &nbsp; Resumen</div>
            <div class="sidebar-item">◫ &nbsp; Vistas</div>
            <div class="sidebar-item">▥ &nbsp; Indicadores</div>
            <div class="sidebar-item">⌕ &nbsp; Exploración</div>
            <div class="sidebar-item">♧ &nbsp; Alertas</div>
            <div class="sidebar-item">▤ &nbsp; Reportes</div>
            <div class="sidebar-item">⚙ &nbsp; Configuración</div>

            <div class="sidebar-bottom">
                ◔ &nbsp; Tema oscuro
                <br><br>
                ◉ &nbsp; Usuario<br>
                <span style="color:#6b7280; margin-left:26px;">Administrador</span>
            </div>
            """
        )


def render_header() -> None:
    col_spacer, col_date, col_export = st.columns([5.5, 2.2, 1])

    with col_date:
        render_html(
            """
            <div class="date-pill">
                <span>📅</span>
                <span>01 may. 2024 – 31 may. 2024</span>
            </div>
            """
        )

    with col_export:
        st.button("⬇ Exportar", use_container_width=True)


def render_view_tabs(active_view: str) -> str:
    views = [
        {"id": "1", "icon": "◎", "title": "Vista 1", "subtitle": "Riesgo y volumen"},
        {"id": "2", "icon": "↗", "title": "Vista 2", "subtitle": "Score externo y perfil"},
        {"id": "3", "icon": "◔", "title": "Vista 3", "subtitle": "Simulador de corte"},
    ]

    cards = []
    for view in views:
        active_class = "active" if active_view == view["id"] else ""
        cards.append(
            f"""
            <a class="view-card {active_class}" href="?view={view["id"]}" target="_self">
                <div class="view-icon">{view["icon"]}</div>
                <div>
                    <div class="view-title">{view["title"]}</div>
                    <span class="view-subtitle">{view["subtitle"]}</span>
                </div>
            </a>
            """
        )

    render_html(
        f"""
        <div class="view-tabs">
            {''.join(cards)}
        </div>

        <div class="info-banner">
            ⓘ &nbsp; Cada vista responde una <strong>pregunta de negocio</strong> diferente.
            El código está separado por archivos para facilitar el mantenimiento.
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


render_sidebar()
render_header()

active_view = str(st.query_params.get("view", "1"))
active_view = render_view_tabs(active_view)

if active_view == "1":
    render_vista_1()
elif active_view == "2":
    render_placeholder("2", "Score externo y perfil del cliente")
elif active_view == "3":
    render_placeholder("3", "Simulador de punto de corte")
else:
    render_vista_1()
