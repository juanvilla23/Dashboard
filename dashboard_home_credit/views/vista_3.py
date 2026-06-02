"""Vista 3: Simulador de punto de corte sobre EXT_SOURCE_MEAN."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ui.render import render_html
from ui.theme import color_rgba, get_theme, plotly_colors
from views.segmentacion import DATA_PATH, cargar_datos, formatear_numero, formatear_porcentaje

COLUMNA_SCORE = "EXT_SOURCE_MEAN"
N_CURVA = 120
N_BINS_HIST = 35

PRESETS = {
    "Sin filtro": "min",
    "Muy estricto": 0.10,
    "Estricto": 0.25,
    "Balanceado": 0.50,
    "Conservador": 0.75,
}


@st.cache_data
def preparar_simulacion() -> tuple[pd.DataFrame, float, float, float, float]:
    df = cargar_datos()[[COLUMNA_SCORE, "TARGET"]].dropna().copy()
    score_min = float(df[COLUMNA_SCORE].min())
    score_max = float(df[COLUMNA_SCORE].max())
    tasa_base = float(df["TARGET"].mean() * 100)
    auc = calcular_auc_score(df)
    return df, score_min, score_max, tasa_base, auc


def calcular_auc_score(df: pd.DataFrame) -> float:
    """AUC: mayor score → menor probabilidad de default."""
    y = df["TARGET"].to_numpy()
    scores = df[COLUMNA_SCORE].to_numpy()
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5

    order = np.argsort(scores)
    y_sorted = y[order]
    tpr = np.cumsum(y_sorted) / n_pos
    fpr = np.cumsum(1 - y_sorted) / n_neg
    return float(np.trapezoid(tpr, fpr))


def umbral_desde_preset(preset: str, df: pd.DataFrame, score_min: float) -> float:
    spec = PRESETS[preset]
    if spec == "min":
        return score_min
    return float(df[COLUMNA_SCORE].quantile(spec))


def metricas_corte(df: pd.DataFrame, umbral: float) -> dict:
    aprobados = df[df[COLUMNA_SCORE] >= umbral]
    rechazados = df[df[COLUMNA_SCORE] < umbral]

    total = len(df)
    total_defaults = int(df["TARGET"].sum())
    total_buenos = total - total_defaults

    n_aprobados = len(aprobados)
    defaults_aprobados = int(aprobados["TARGET"].sum())
    defaults_rechazados = int(rechazados["TARGET"].sum())
    buenos_rechazados = len(rechazados) - defaults_rechazados

    pct_aprobada = n_aprobados / total * 100 if total else 0.0
    tasa_aprobados = defaults_aprobados / n_aprobados * 100 if n_aprobados else 0.0

    return {
        "pct_cartera_aprobada": pct_aprobada,
        "tasa_default_aprobados": tasa_aprobados,
        "pct_defaults_evitados": defaults_rechazados / total_defaults * 100 if total_defaults else 0,
        "pct_buenos_rechazados": buenos_rechazados / total_buenos * 100 if total_buenos else 0,
        "n_aprobados": n_aprobados,
        "defaults_evitados": defaults_rechazados,
        "total_defaults": total_defaults,
        "buenos_rechazados": buenos_rechazados,
        "delta_tasa_pp": tasa_aprobados - df["TARGET"].mean() * 100,
    }


@st.cache_data
def curva_tradeoff_completa(_v: str, score_min: float, score_max: float) -> pd.DataFrame:
    df = cargar_datos()[[COLUMNA_SCORE, "TARGET"]].dropna()
    umbrales = np.linspace(score_min, score_max, N_CURVA)
    filas = [metricas_corte(df, float(u)) for u in umbrales]
    curva = pd.DataFrame(filas)
    curva["umbral"] = umbrales
    return curva


def crear_histograma_corte(df: pd.DataFrame, umbral: float, score_min: float, score_max: float) -> go.Figure:
    bins = np.linspace(score_min, score_max, N_BINS_HIST + 1)
    df_hist = df.copy()
    df_hist["bin"] = pd.cut(df_hist[COLUMNA_SCORE], bins=bins, include_lowest=True)

    agrupado = df_hist.groupby("bin", observed=False).agg(
        buenos=("TARGET", lambda s: (s == 0).sum()),
        defaults=("TARGET", "sum"),
    ).reset_index()

    centros = [interval.mid for interval in agrupado["bin"]]
    buenos = agrupado["buenos"].astype(float)
    defaults = agrupado["defaults"].astype(float)

    palette = plotly_colors()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=centros,
            y=buenos,
            name="Buenos",
            marker_color=color_rgba(palette["success"], 0.85),
            hovertemplate="Score: %{x:.3f}<br>Buenos: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=centros,
            y=defaults,
            name="Defaults",
            marker_color=color_rgba(palette["accent"], 0.9),
            hovertemplate="Score: %{x:.3f}<br>Defaults: %{y:,.0f}<extra></extra>",
        )
    )

    colors = plotly_colors()
    plotly_tpl = "plotly_white" if get_theme() == "light" else "plotly_dark"
    fig.update_layout(
        template=plotly_tpl,
        barmode="stack",
        height=380,
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["font"], "size": 12},
        xaxis={
            "title": "",
            "gridcolor": colors["grid"],
            "range": [score_min - 0.01, score_max + 0.01],
        },
        yaxis={"title": "Clientes", "gridcolor": colors["grid"]},
        legend={
            "orientation": "h",
            "y": 1.12,
            "x": 0.5,
            "xanchor": "center",
            "font": {"color": colors["text_primary"], "size": 12},
        },
    )

    fig.add_vline(
        x=umbral,
        line_width=2,
        line_dash="dash",
        line_color=colors["ref_line"],
        annotation_text=f"Corte {umbral:.3f}",
        annotation_font_color=colors["annotation_text"],
        annotation_bgcolor=colors["annotation_bg"],
        annotation_position="top",
    )

    fig.add_vrect(
        x0=score_min - 0.01,
        x1=umbral,
        fillcolor=colors["reject_zone"],
        line_width=0,
        layer="below",
    )

    return fig


def crear_curva_tradeoff(curva: pd.DataFrame, metricas: dict) -> go.Figure:
    fig = go.Figure()

    colors = plotly_colors()
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            line={"color": colors["muted_line"], "dash": "dash", "width": 1},
            name="Azar",
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=curva["pct_buenos_rechazados"],
            y=curva["pct_defaults_evitados"],
            mode="lines",
            line={"color": colors["info"], "width": 3},
            name="Trade-off",
            hovertemplate=(
                "Buenos rechazados: %{x:.1f}%<br>"
                "Defaults evitados: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[metricas["pct_buenos_rechazados"]],
            y=[metricas["pct_defaults_evitados"]],
            mode="markers+text",
            marker={
                "size": 16,
                "color": colors["accent"],
                "line": {"color": colors["text_primary"], "width": 2},
            },
            text=[f"Corte actual"],
            textposition="top center",
            textfont={"color": colors["text_primary"], "size": 11},
            name="Corte actual",
            hovertemplate=(
                "Buenos rechazados: %{x:.1f}%<br>"
                "Defaults evitados: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    plotly_tpl = "plotly_white" if get_theme() == "light" else "plotly_dark"
    fig.update_layout(
        template=plotly_tpl,
        height=380,
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["font"], "size": 12},
        xaxis={
            "title": "% buenos rechazados",
            "range": [-2, 102],
            "gridcolor": colors["grid"],
        },
        yaxis={
            "title": "% defaults evitados",
            "range": [-2, 102],
            "gridcolor": colors["grid"],
        },
        legend={
            "orientation": "h",
            "y": 1.12,
            "x": 0.5,
            "xanchor": "center",
            "font": {"color": colors["text_primary"], "size": 12},
        },
    )
    return fig


def _tarjeta_kpi(titulo: str, valor: str, subtitulo: str, color_valor: str | None = None) -> str:
    if color_valor is None:
        color_valor = plotly_colors()["text_primary"]
    return f"""
    <div class="v3-kpi">
        <div class="v3-kpi-title">{titulo}</div>
        <div class="v3-kpi-value" style="color:{color_valor};">{valor}</div>
        <div class="v3-kpi-sub">{subtitulo}</div>
    </div>
    """


def render_vista_3() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df, score_min, score_max, tasa_base, _ = preparar_simulacion()

    if "v3_umbral" not in st.session_state:
        st.session_state.v3_umbral = float(df[COLUMNA_SCORE].quantile(0.50))
    if "v3_preset" not in st.session_state:
        st.session_state.v3_preset = "Balanceado"

    cols_preset = st.columns(len(PRESETS))
    preset_actual = st.session_state.v3_preset

    for col, nombre in zip(cols_preset, PRESETS.keys()):
        with col:
            if st.button(
                nombre,
                use_container_width=True,
                type="primary" if nombre == preset_actual else "secondary",
                key=f"v3_btn_{nombre}",
            ):
                st.session_state.v3_preset = nombre
                st.session_state.v3_umbral = umbral_desde_preset(nombre, df, score_min)
                st.rerun()

    col_slider, col_corte = st.columns([5, 1])
    with col_slider:
        umbral = st.slider(
            "Umbral EXT_SOURCE_MEAN (aprobar si ≥)",
            min_value=score_min,
            max_value=score_max,
            value=float(st.session_state.v3_umbral),
            step=0.005,
            format="%.3f",
            key="v3_slider",
            label_visibility="collapsed",
        )
    with col_corte:
        render_html(
            f"""
            <div class="v3-corte-box">
                <div class="v3-corte-label">CORTE</div>
                <div class="v3-corte-value">{umbral:.3f}</div>
            </div>
            """
        )

    st.session_state.v3_umbral = umbral
    metricas = metricas_corte(df, umbral)
    curva = curva_tradeoff_completa("v1", score_min, score_max)

    palette = plotly_colors()
    delta_pct = metricas["delta_tasa_pp"] / tasa_base * 100 if tasa_base else 0
    color_tasa = palette["success"]
    if metricas["tasa_default_aprobados"] >= tasa_base:
        color_tasa = palette["warning"]
    if metricas["tasa_default_aprobados"] > tasa_base * 1.05:
        color_tasa = palette["accent"]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_html(
            _tarjeta_kpi(
                "% cartera aprobada",
                f"{metricas['pct_cartera_aprobada']:.1f}%",
                f"{formatear_numero(metricas['n_aprobados'])} clientes",
            )
        )
    with k2:
        render_html(
            _tarjeta_kpi(
                "Tasa default aprobados",
                f"{metricas['tasa_default_aprobados']:.2f}%",
                f"{delta_pct:+.0f}% vs base {tasa_base:.2f}%",
                color_tasa,
            )
        )
    with k3:
        render_html(
            _tarjeta_kpi(
                "% defaults evitados",
                f"{metricas['pct_defaults_evitados']:.1f}%",
                f"{formatear_numero(metricas['defaults_evitados'])} de "
                f"{formatear_numero(metricas['total_defaults'])} defaults",
                palette["success"],
            )
        )
    with k4:
        render_html(
            _tarjeta_kpi(
                "% buenos rechazados",
                f"{metricas['pct_buenos_rechazados']:.1f}%",
                f"{formatear_numero(metricas['buenos_rechazados'])} buenos perdidos",
                palette["warning"],
            )
        )

    col_hist, col_curva = st.columns(2)

    with col_hist:
        render_html(
            """
            <div class="v3-chart-title">Dónde cae el corte</div>
            <div class="v3-chart-sub">
                Distribución del score · zona gris = rechazados · rojo = defaults
            </div>
            """
        )
        st.plotly_chart(
            crear_histograma_corte(df, umbral, score_min, score_max),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_curva:
        render_html(
            """
            <div class="v3-chart-title">Curva de trade-off</div>
            <div class="v3-chart-sub">
                Defaults evitados vs buenos sacrificados · punto = corte actual
            </div>
            """
        )
        st.plotly_chart(
            crear_curva_tradeoff(curva, metricas),
            use_container_width=True,
            config={"displayModeBar": False},
        )
