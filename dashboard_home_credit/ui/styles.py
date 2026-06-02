"""Hoja de estilos global: tema oscuro por defecto en .stApp / #dashboard-root."""

# Variables en la raíz del dashboard (NO en <body>). Tema claro solo con .theme-light
THEME_VARS_DARK = """
.stApp,
#dashboard-root {
    --bg-page: #0d0d0d;
    --bg-card: #1a1a1a;
    --bg-surface: #141414;
    --bg-input: #121212;
    --text-primary: #ffffff;
    --text-secondary: #9aa3af;
    --text-muted: #6b7280;
    --text-body: #f4f4f4;
    --border: rgba(255, 255, 255, 0.08);
    --border-strong: rgba(255, 255, 255, 0.10);
    --accent: #e53935;
    --accent-hover: #ff5252;
    --accent-bg: rgba(229, 57, 53, 0.12);
    --accent-text: #ff8a80;
    --accent-border: rgba(229, 57, 53, 0.45);
    --success: #4caf50;
    --success-bg: rgba(76, 175, 80, 0.15);
    --warning: #ffeb3b;
    --warning-bg: rgba(255, 235, 59, 0.12);
    --info: #42a5f5;
    --info-bg: rgba(66, 165, 245, 0.12);
    --info-border: rgba(66, 165, 245, 0.35);
    --info-text: #90caf9;
    --slider-fill: #e53935;
    --slider-track: rgba(255, 255, 255, 0.12);
    --slider-thumb: #e53935;
    --slider-thumb-border: #ffffff;
    --page-glow: rgba(229, 57, 53, 0.08);
    --shadow-accent: rgba(229, 57, 53, 0.12);
    --chart-reject-zone: rgba(180, 180, 180, 0.12);
}
"""

THEME_VARS_LIGHT = """
.stApp.theme-light,
#dashboard-root.theme-light {
    --bg-page: #F1EFE8;
    --bg-card: #FFFFFF;
    --bg-surface: #F9F8F5;
    --bg-input: #FFFFFF;
    --text-primary: #2C2C2A;
    --text-secondary: #5F5E5A;
    --text-muted: #888780;
    --text-body: #2C2C2A;
    --border: rgba(0, 0, 0, 0.10);
    --border-strong: rgba(0, 0, 0, 0.18);
    --accent: #E24B4A;
    --accent-hover: #C93D3C;
    --accent-bg: #FCEBEB;
    --accent-text: #791F1F;
    --accent-border: #F7C1C1;
    --success: #3B6D11;
    --success-bg: #EAF3DE;
    --warning: #BA7517;
    --warning-bg: #FAEEDA;
    --info: #185FA5;
    --info-bg: #E6F1FB;
    --info-border: #85B7EB;
    --info-text: #0C447C;
    --slider-fill: #E24B4A;
    --slider-track: #D3D1C7;
    --slider-thumb: #E24B4A;
    --slider-thumb-border: #FFFFFF;
    --page-glow: rgba(226, 75, 74, 0.06);
    --shadow-accent: rgba(226, 75, 74, 0.10);
    --chart-reject-zone: rgba(0, 0, 0, 0.05);
}

/* Overrides directos para Streamlit: cuando el OS/browser es dark-mode,
   Streamlit inyecta sus propias variables que sobreescriben las nuestras.
   Estos selectores concretos las neutralizan. */
.stApp.theme-light,
.stApp.theme-light [data-testid="stAppViewContainer"],
.stApp.theme-light [data-testid="stMain"],
.stApp.theme-light .main,
.stApp.theme-light section.main,
.stApp.theme-light [data-testid="block-container"] {
    background-color: #F1EFE8 !important;
    color: #2C2C2A !important;
}

.stApp.theme-light [data-testid="stVerticalBlockBorderWrapper"],
.stApp.theme-light .panel-box,
.stApp.theme-light .chart-panel,
.stApp.theme-light .v3-auc-box,
.stApp.theme-light .v3-corte-box,
.stApp.theme-light .v3-kpi,
.stApp.theme-light .v4-metric,
.stApp.theme-light .v2-matriz-panel,
.stApp.theme-light .kpi-card {
    background-color: #FFFFFF !important;
    border-color: rgba(0, 0, 0, 0.10) !important;
    color: #2C2C2A !important;
}

.stApp.theme-light .view-card {
    background: #FFFFFF !important;
    border-color: rgba(0, 0, 0, 0.18) !important;
    color: #5F5E5A !important;
}

.stApp.theme-light .view-card.active {
    background: #FCEBEB !important;
    border-color: #E24B4A !important;
}

.stApp.theme-light label,
.stApp.theme-light .stCaption,
.stApp.theme-light .stMarkdown,
.stApp.theme-light .stMarkdown p,
.stApp.theme-light p,
.stApp.theme-light span,
.stApp.theme-light div {
    color: #2C2C2A !important;
}

.stApp.theme-light .kpi-label,
.stApp.theme-light .v4-metric-label,
.stApp.theme-light .v3-auc-label,
.stApp.theme-light .v3-chart-sub,
.stApp.theme-light .view-subtitle,
.stApp.theme-light .panel-subtitle,
.stApp.theme-light [data-testid="stMetricLabel"] {
    color: #5F5E5A !important;
}

.stApp.theme-light .kpi-value,
.stApp.theme-light .v3-corte-value,
.stApp.theme-light .v3-kpi-value,
.stApp.theme-light .v4-metric-value,
.stApp.theme-light [data-testid="stMetricValue"] {
    color: #2C2C2A !important;
}

.stApp.theme-light div[data-baseweb="select"] > div,
.stApp.theme-light div[data-testid="stNumberInput"] input,
.stApp.theme-light div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    border-color: rgba(0, 0, 0, 0.18) !important;
    color: #2C2C2A !important;
}

.stApp.theme-light div[data-testid="stButton"] button {
    background: #FFFFFF !important;
    border-color: rgba(0, 0, 0, 0.18) !important;
    color: #5F5E5A !important;
}

.stApp.theme-light div[data-testid="stAlert"] {
    background: #FFFFFF !important;
    border-color: rgba(0, 0, 0, 0.18) !important;
    color: #2C2C2A !important;
}

.stApp.theme-light div[data-testid="stSlider"] [role="slider"] {
    background: #E24B4A !important;
    border-color: #FFFFFF !important;
}

.stApp.theme-light div[data-testid="stSlider"] > div > div > div:first-child {
    background: #D3D1C7 !important;
}
"""

COMPONENT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp,
#dashboard-root {
    background:
        radial-gradient(circle at top right, var(--page-glow), transparent 30%),
        var(--bg-page) !important;
    color: var(--text-body) !important;
}

.stApp.theme-light,
#dashboard-root.theme-light {
    background:
        radial-gradient(circle at top right, var(--page-glow), transparent 32%),
        var(--bg-page) !important;
}

#MainMenu, footer, header {
    visibility: hidden;
    height: 0;
}

section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapsedControl"],
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

div[data-testid="stAppViewContainer"] {
    margin-left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    background: transparent !important;
}

.block-container {
    padding-top: 0.8rem;
    padding-bottom: 1.5rem;
    max-width: 1680px;
}

.view-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-bottom: 10px;
}

.view-card {
    flex: 1;
    min-width: 160px;
    max-width: calc(25% - 11px);
    min-height: 78px;
    padding: 14px 16px;
    border-radius: 10px 10px 0 0;
    border: 1px solid var(--border-strong);
    background: var(--bg-card);
    color: var(--text-secondary) !important;
    text-decoration: none !important;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: 0.2s ease;
}

.view-card:hover {
    border-color: var(--accent);
}

.view-card.active {
    border-color: var(--accent);
    background: linear-gradient(145deg, var(--accent-bg), var(--bg-card));
    box-shadow: 0 0 18px var(--shadow-accent);
}

.view-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--bg-surface);
    font-size: 18px;
    flex-shrink: 0;
}

.view-card.active .view-icon {
    background: var(--accent-bg);
    color: var(--accent);
}

.view-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
}

.view-card.active .view-title {
    color: var(--accent);
}

.view-subtitle {
    display: block;
    margin-top: 2px;
    font-size: 12px;
    color: var(--text-secondary);
}

.panel-box,
.chart-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
}

.chart-panel {
    padding: 16px 18px 8px 18px;
}

.panel-title {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 12px;
}

.panel-subtitle {
    color: var(--accent);
    font-size: 13px;
    font-weight: 600;
    margin-top: -8px;
    margin-bottom: 14px;
}

.filter-clear {
    color: var(--accent);
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
    border-bottom: 1px solid var(--border);
}

.kpi-card:last-of-type {
    border-bottom: none;
}

.kpi-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent-hover));
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 17px;
    font-weight: 700;
    flex-shrink: 0;
}

.kpi-label {
    color: var(--text-secondary);
    font-size: 12px;
}

.kpi-value {
    color: var(--text-primary);
    font-size: 20px;
    font-weight: 700;
    margin-top: 2px;
}

.kpi-delta {
    margin-left: auto;
    color: var(--accent);
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}

.v2-controls-spacer { height: 28px; }

.v2-section-separator {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 6px 0 18px 0;
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.v2-section-separator::before,
.v2-section-separator::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border-strong);
}

.v2-section-hint {
    color: var(--text-muted);
    font-size: 12px;
    margin: -4px 0 10px 0;
    line-height: 1.4;
}

.placeholder {
    padding: 60px 25px;
    border-radius: 12px;
    border: 1px dashed var(--accent-border);
    background: var(--bg-surface);
    text-align: center;
    color: var(--text-secondary);
}

.placeholder h2 {
    color: var(--accent);
    font-size: 20px;
}

div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextInput"] input {
    background-color: var(--bg-input) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

div[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
}

div[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

div[data-testid="stButton"] button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #ffffff !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    border-radius: 10px;
    padding: 4px 8px;
}

div[data-testid="stPlotlyChart"] {
    background: transparent;
}

div[data-testid="stSlider"] [data-baseweb="slider"] {
    height: 6px;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div {
    background: var(--slider-track) !important;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: var(--slider-fill) !important;
}

div[data-testid="stSlider"] [role="slider"] {
    background: var(--slider-thumb) !important;
    border: 2.5px solid var(--slider-thumb-border) !important;
    width: 18px !important;
    height: 18px !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

div[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: var(--text-secondary) !important;
}

.v3-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    gap: 16px;
}

.v3-title { color: var(--text-primary); font-size: 22px; font-weight: 700; }
.v3-subtitle { color: var(--text-secondary); font-size: 13px; margin-top: 4px; }

.v3-auc-box,
.v3-corte-box,
.v3-kpi {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
}

.v3-auc-box {
    padding: 12px 18px;
    text-align: center;
    min-width: 120px;
}

.v3-auc-label,
.v3-corte-label,
.v3-kpi-title {
    color: var(--text-secondary);
    font-size: 10px;
    letter-spacing: 1px;
}

.v3-kpi-title { font-size: 12px; letter-spacing: 0; margin-bottom: 6px; }

.v3-auc-value { color: var(--accent); font-size: 26px; font-weight: 700; }

.v3-corte-box {
    padding: 10px 16px;
    text-align: center;
    min-width: 100px;
}

.v3-corte-value { color: var(--text-primary); font-size: 22px; font-weight: 700; }

.v3-kpi { padding: 16px; height: 100%; }

.v3-kpi-value { font-size: 28px; font-weight: 700; line-height: 1.1; }

.v3-kpi-sub { color: var(--text-muted); font-size: 12px; margin-top: 6px; }

.v3-chart-title { color: var(--text-primary); font-weight: 600; font-size: 14px; }

.v3-chart-sub {
    color: var(--text-secondary);
    font-size: 12px;
    margin-top: 2px;
    margin-bottom: 8px;
}

.v4-metrics-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}

.v4-metric,
.v4-rate-bar-wrap {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
}

.v4-metric {
    padding: 12px 14px;
    min-height: 78px;
}

.v4-metric-label,
.v4-rate-bar-title,
.v4-lift-legend {
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 600;
}

.v4-metric-label {
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.v4-metric-value {
    font-size: 22px;
    font-weight: 700;
    margin-top: 4px;
    line-height: 1.2;
}

.v4-metric-sub {
    color: var(--text-muted);
    font-size: 11px;
    margin-top: 4px;
}

.v4-rate-bar-wrap {
    padding: 14px 16px 10px;
    margin-bottom: 14px;
}

.v4-rate-bar-title { font-size: 12px; margin-bottom: 10px; }

.v4-rate-track {
    position: relative;
    height: 22px;
    background: var(--border);
    border-radius: 4px;
    overflow: visible;
}

.v4-rate-fill {
    height: 100%;
    border-radius: 4px;
    max-width: 100%;
}

.v4-rate-marker {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 30px;
    background: var(--text-primary);
    transform: translateX(-50%);
    opacity: 0.65;
}

.v4-rate-scale {
    display: flex;
    justify-content: space-between;
    color: var(--text-muted);
    font-size: 10px;
    font-family: ui-monospace, 'Cascadia Code', monospace;
    margin-top: 8px;
}

.v4-lift-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    margin-top: 8px;
    font-weight: 400;
}

.v4-lift-legend span {
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.v4-lift-dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    display: inline-block;
}

@media (max-width: 1100px) {
    .v4-metrics-row { grid-template-columns: repeat(2, 1fr); }
}

.v2-matrices-wrap { display: flex; flex-wrap: wrap; gap: 16px; width: 100%; }

.v2-matriz-panel {
    flex: 1 1 280px;
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: 12px;
    padding: 14px 12px 16px;
    min-width: 0;
}

.v2-matriz-titulo {
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
    text-align: center;
    margin: 0 0 14px 0;
}

.v2-matriz-outer {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr);
    gap: 0 12px;
}

.v2-eje-y-label,
.v2-eje-x-label,
.v2-matriz-row-head {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
}

.v2-eje-y-label {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    display: flex;
    align-items: center;
    justify-content: center;
}

.v2-eje-x-label {
    text-align: center;
    padding: 0 8px 4px;
    border-bottom: 1px solid var(--border);
}

.v2-matriz-main {
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-width: 0;
}

.v2-matriz-grid {
    display: grid;
    grid-template-columns: 72px repeat(3, minmax(0, 1fr));
    gap: 9px;
}

.v2-matriz-col-head {
    text-align: center;
    font-size: 14px;
    font-weight: 700;
    color: var(--text-primary);
    padding: 6px 2px 4px;
}

.v2-matriz-row-head {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
}

.v2-celda {
    border-radius: 10px;
    padding: 12px 8px 10px;
    text-align: center;
    min-height: 86px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border: 1px solid var(--border);
}

.v2-celda-tasa {
    font-size: 20px;
    font-weight: 700;
    line-height: 1.15;
}

.v2-celda-lift {
    font-size: 14px;
    font-weight: 600;
    font-family: ui-monospace, 'Cascadia Code', monospace;
}

.v2-celda-n {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
    font-family: ui-monospace, 'Cascadia Code', monospace;
}

.v2-celda-vacia {
    background: var(--bg-page) !important;
    border-style: dashed;
    border-color: var(--border-strong);
    color: var(--text-muted);
    font-size: 22px;
}

.v2-matriz-leyenda {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 16px;
    margin-top: 14px;
    font-size: 11px;
    color: var(--text-secondary);
}

.v2-leyenda-punto {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    margin-right: 4px;
}

div[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
}

label, .stCaption, .stMarkdown, .stMarkdown p {
    color: var(--text-secondary);
}

/* Botón sol/luna (esquina superior derecha) */
#dashboard-theme-toggle {
    position: fixed;
    top: 12px;
    right: 16px;
    z-index: 999999;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    border: 1px solid var(--border-strong);
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: 20px;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
}

#dashboard-theme-toggle:hover {
    border-color: var(--accent);
    transform: scale(1.04);
}

.stApp.theme-light #dashboard-theme-toggle,
#dashboard-root.theme-light #dashboard-theme-toggle {
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}
"""


def get_css_content() -> str:
    return f"{THEME_VARS_DARK}{THEME_VARS_LIGHT}{COMPONENT_CSS}"


def build_global_stylesheet() -> str:
    return f"<style id='dashboard-global-styles'>{get_css_content()}</style>"
