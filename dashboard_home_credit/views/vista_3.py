"""Vista 3: Simulador de punto de corte sobre EXT_SOURCE_MEAN."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.render import render_html
from views.segmentacion import DATA_PATH, cargar_datos, formatear_porcentaje

AUC_MODELO = 0.72
COLUMNA_SCORE = "EXT_SOURCE_MEAN"
N_PUNTOS_CURVA = 80


@st.cache_data
def preparar_simulacion() -> tuple[pd.DataFrame, float, float]:
    df = cargar_datos()[[COLUMNA_SCORE, "TARGET"]].dropna().copy()
    score_min = float(df[COLUMNA_SCORE].min())
    score_max = float(df[COLUMNA_SCORE].max())
    return df, score_min, score_max


@st.cache_data
def calcular_curva_tradeoff(_df_hash: str, score_min: float, score_max: float) -> pd.DataFrame:
    df = cargar_datos()[[COLUMNA_SCORE, "TARGET"]].dropna()
    umbrales = np.linspace(score_min, score_max, N_PUNTOS_CURVA)

    filas = []
    for umbral in umbrales:
        filas.append(_metricas_corte(df, float(umbral)))

    curva = pd.DataFrame(filas)
    curva["umbral"] = umbrales
    return curva


def _metricas_corte(df: pd.DataFrame, umbral: float) -> dict:
    """Aprueba si EXT_SOURCE_MEAN >= umbral (mayor score = menor riesgo)."""
    aprobados = df[df[COLUMNA_SCORE] >= umbral]
    rechazados = df[df[COLUMNA_SCORE] < umbral]

    total = len(df)
    total_defaults = int(df["TARGET"].sum())
    total_buenos = total - total_defaults

    n_aprobados = len(aprobados)
    n_rechazados = len(rechazados)
    defaults_aprobados = int(aprobados["TARGET"].sum())
    defaults_rechazados = int(rechazados["TARGET"].sum())
    buenos_rechazados = n_rechazados - defaults_rechazados

    pct_aprobada = n_aprobados / total * 100 if total else 0.0
    tasa_default_aprobados = (
        defaults_aprobados / n_aprobados * 100 if n_aprobados else 0.0
    )
    pct_defaults_evitados = (
        defaults_rechazados / total_defaults * 100 if total_defaults else 0.0
    )
    pct_buenos_rechazados = (
        buenos_rechazados / total_buenos * 100 if total_buenos else 0.0
    )

    return {
        "pct_cartera_aprobada": pct_aprobada,
        "tasa_default_aprobados": tasa_default_aprobados,
        "pct_defaults_evitados": pct_defaults_evitados,
        "pct_buenos_rechazados": pct_buenos_rechazados,
        "n_aprobados": n_aprobados,
        "n_rechazados": n_rechazados,
    }


def crear_grafica_frontera(curva: pd.DataFrame, umbral_actual: float) -> go.Figure:
    punto = curva.iloc[(curva["umbral"] - umbral_actual).abs().argmin()]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curva["pct_cartera_aprobada"],
            y=curva["tasa_default_aprobados"],
            mode="lines",
            name="Frontera de trade-off",
            line={"color": "rgba(229, 57, 53, 0.5)", "width": 2, "dash": "dot"},
            hovertemplate=(
                "Aprobación: %{x:.1f}%<br>"
                "Tasa default aprobados: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[punto["pct_cartera_aprobada"]],
            y=[punto["tasa_default_aprobados"]],
            mode="markers+text",
            name="Corte seleccionado",
            marker={"size": 14, "color": "#e53935", "line": {"color": "#fff", "width": 2}},
            text=[f"Umbral {umbral_actual:.3f}"],
            textposition="top center",
            textfont={"color": "#ffffff", "size": 11},
            hovertemplate=(
                "Aprobación: %{x:.1f}%<br>"
                "Tasa default: %{y:.1f}%<br>"
                f"Umbral: {umbral_actual:.3f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=380,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#9aa3af", "size": 12},
        xaxis={
            "title": "% cartera aprobada",
            "gridcolor": "rgba(255,255,255,0.08)",
            "range": [0, 105],
        },
        yaxis={
            "title": "Tasa de default en aprobados (%)",
            "gridcolor": "rgba(255,255,255,0.08)",
        },
        legend={"orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"},
    )
    return fig


def crear_grafica_costos(curva: pd.DataFrame, umbral_actual: float) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curva["umbral"],
            y=curva["pct_defaults_evitados"],
            mode="lines",
            name="Defaults evitados",
            line={"color": "#4caf50", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=curva["umbral"],
            y=curva["pct_buenos_rechazados"],
            mode="lines",
            name="Buenos clientes rechazados",
            line={"color": "#ff9800", "width": 2},
        )
    )

    fig.add_vline(
        x=umbral_actual,
        line_width=1,
        line_dash="dash",
        line_color="#e53935",
    )

    fig.update_layout(
        height=320,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#9aa3af", "size": 12},
        xaxis={"title": "Umbral EXT_SOURCE_MEAN (aprobar si ≥)", "gridcolor": "rgba(255,255,255,0.08)"},
        yaxis={"title": "%", "gridcolor": "rgba(255,255,255,0.08)", "range": [0, 105]},
        legend={"orientation": "h", "y": -0.25, "x": 0.5, "xanchor": "center"},
    )
    return fig


def render_vista_3() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df, score_min, score_max = preparar_simulacion()
    tasa_sin_filtro = df["TARGET"].mean() * 100

    col_controles, col_resultados = st.columns([1.1, 3.5], gap="medium")

    with col_controles:
        with st.container(border=True):
            render_html(
                f"""
                <div class="panel-title" style="margin-bottom:4px;">Simulador de corte</div>
                <div class="panel-subtitle" style="margin:0 0 12px 0;">
                    Regla: aprobar si EXT_SOURCE_MEAN ≥ umbral
                </div>
                <div class="chart-footer" style="margin-bottom:12px;">
                    ⓘ Modelo con AUC ≈ <strong style="color:#ff5252;">{AUC_MODELO:.2f}</strong>.
                    Mayor score externo → menor riesgo observado.
                </div>
                """
            )

            escenario = st.selectbox(
                "Escenarios rápidos",
                [
                    "Personalizado (slider)",
                    "Conservador (p75)",
                    "Balanceado (p50)",
                    "Agresivo (p25)",
                    "Muy agresivo (p10)",
                ],
                index=1,
                key="v3_escenario",
            )

            if escenario == "Personalizado (slider)":
                umbral = st.slider(
                    "Umbral de aprobación (EXT_SOURCE_MEAN)",
                    min_value=score_min,
                    max_value=score_max,
                    value=float(np.quantile(df[COLUMNA_SCORE], 0.50)),
                    step=0.01,
                    format="%.3f",
                    key="v3_umbral",
                    help="Solo se aprueban solicitudes con score ≥ umbral.",
                )
            else:
                quantil = {
                    "Conservador (p75)": 0.75,
                    "Balanceado (p50)": 0.50,
                    "Agresivo (p25)": 0.25,
                    "Muy agresivo (p10)": 0.10,
                }[escenario]
                umbral = float(df[COLUMNA_SCORE].quantile(quantil))
                st.metric("Umbral del escenario", f"{umbral:.3f}")

            st.caption(f"Rango histórico: {score_min:.3f} – {score_max:.3f}")

        with st.container(border=True):
            render_html('<div class="panel-title">Sin filtro (baseline)</div>')
            st.metric("Cartera aprobada", "100%")
            st.metric("Tasa default", formatear_porcentaje(tasa_sin_filtro))

    metricas = _metricas_corte(df, umbral)
    curva = calcular_curva_tradeoff("v1", score_min, score_max)

    with col_resultados:
        render_html(
            """
            <div class="panel-title" style="margin-bottom:8px;">
                Trade-off del corte seleccionado
            </div>
            """
        )

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric(
                "% cartera aprobada",
                formatear_porcentaje(metricas["pct_cartera_aprobada"]),
                help="Volumen de negocio que sigue en cartera.",
            )
        with k2:
            st.metric(
                "Tasa default (aprobados)",
                formatear_porcentaje(metricas["tasa_default_aprobados"]),
                delta=f"{metricas['tasa_default_aprobados'] - tasa_sin_filtro:+.1f} pp vs baseline",
                delta_color="inverse",
                help="Riesgo esperado de la cartera que apruebas.",
            )
        with k3:
            st.metric(
                "% defaults evitados",
                formatear_porcentaje(metricas["pct_defaults_evitados"]),
                help="Incumplimientos que rechazas del total histórico.",
            )
        with k4:
            st.metric(
                "% buenos rechazados",
                formatear_porcentaje(metricas["pct_buenos_rechazados"]),
                delta_color="inverse",
                help="Clientes sanos que pierdes por el filtro.",
            )

        with st.container(border=True):
            render_html(
                '<div class="panel-subtitle" style="margin:0 0 8px 0;">'
                "Frontera aprobación vs riesgo"
                "</div>"
            )
            st.plotly_chart(
                crear_grafica_frontera(curva, umbral),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with st.container(border=True):
            render_html(
                '<div class="panel-subtitle" style="margin:0 0 8px 0;">'
                "Costo del filtro: defaults evitados vs buenos rechazados"
                "</div>"
            )
            st.plotly_chart(
                crear_grafica_costos(curva, umbral),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with st.expander("Tabla de escenarios (distintas opciones para comité)"):
            escenarios_umbral = {
                "Muy agresivo (p10)": df[COLUMNA_SCORE].quantile(0.10),
                "Agresivo (p25)": df[COLUMNA_SCORE].quantile(0.25),
                "Balanceado (p50)": df[COLUMNA_SCORE].quantile(0.50),
                "Conservador (p75)": df[COLUMNA_SCORE].quantile(0.75),
                "Actual (slider)": umbral,
            }

            tabla = []
            for nombre, u in escenarios_umbral.items():
                m = _metricas_corte(df, float(u))
                tabla.append(
                    {
                        "Escenario": nombre,
                        "Umbral": round(float(u), 3),
                        "% Aprobada": round(m["pct_cartera_aprobada"], 1),
                        "Tasa default aprob. (%)": round(m["tasa_default_aprobados"], 2),
                        "% Defaults evitados": round(m["pct_defaults_evitados"], 1),
                        "% Buenos rechazados": round(m["pct_buenos_rechazados"], 1),
                    }
                )

            st.dataframe(pd.DataFrame(tabla), use_container_width=True, hide_index=True)

        render_html(
            f"""
            <div class="chart-footer">
                ⓘ &nbsp; Con umbral <strong style="color:#ffffff;">{umbral:.3f}</strong>
                apruebas <strong>{metricas['n_aprobados']:,}</strong> solicitudes
                y rechazas <strong>{metricas['n_rechazados']:,}</strong>.
                Es la vista para comparar <strong style="color:#ff5252;">opciones puras</strong>
                ante un comité: más aprobación suele implicar más riesgo y menos buenos perdidos.
            </div>
            """.replace(",", ".")
        )
