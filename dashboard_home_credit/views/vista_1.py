import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

from ui.render import render_html

DATA_PATH = Path(__file__).resolve().parent.parent / "train_selected_features.parquet"

DIMENSIONES = {
    "Edad": "AGE_YEARS",
    "Educación": "NAME_EDUCATION_TYPE",
    "Tipo de ingreso": "NAME_INCOME_TYPE",
    "Historial de buró": "no_bureau_history",
    "Rango de crédito": "EXT_SOURCE_MEAN",
}

ETIQUETAS_EDUCACION = {
    "Lower secondary": "Secundaria baja",
    "Secondary / secondary special": "Secundaria",
    "Incomplete higher": "Superior incompleta",
    "Higher education": "Educación superior",
    "Academic degree": "Grado académico",
}

ETIQUETAS_INGRESO = {
    "Working": "Trabajador",
    "Commercial associate": "Asociado comercial",
    "State servant": "Empleado público",
    "Pensioner": "Pensionado",
    "Unemployed": "Desempleado",
    "Student": "Estudiante",
    "Businessman": "Empresario",
    "Maternity leave": "Licencia de maternidad",
}

ORDEN_EDUCACION = list(ETIQUETAS_EDUCACION.values())
ORDEN_INGRESO = list(ETIQUETAS_INGRESO.values())
ORDEN_EDAD = ["20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-55", "55-60", "60-65", "65-70"]
ORDEN_CREDITO = ["Muy bajo", "Bajo", "Medio", "Medio alto", "Alto", "Muy alto"]
ORDEN_BUREAU = ["Con historial", "Sin historial"]


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.read_parquet(DATA_PATH)


def _formatear_numero(valor: float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def _formatear_porcentaje(valor: float) -> str:
    return f"{valor:.1f}%".replace(".", ",")


def _crear_segmento_edad(edades: pd.Series) -> pd.Series:
    bins = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    return pd.cut(edades, bins=bins, labels=ORDEN_EDAD, right=False)


def _crear_segmento_credito(puntajes: pd.Series) -> pd.Series:
    return pd.qcut(
        puntajes.rank(method="first"),
        q=len(ORDEN_CREDITO),
        labels=ORDEN_CREDITO,
    )


def _aplicar_filtro_historial(df: pd.DataFrame, historial_bureau: str) -> pd.DataFrame:
    if historial_bureau == "Con historial":
        return df[df["no_bureau_history"] == 0]
    if historial_bureau == "Sin historial":
        return df[df["no_bureau_history"] == 1]
    return df


def _crear_columna_segmento(df: pd.DataFrame, dimension: str) -> pd.Series:
    if dimension == "Edad":
        return _crear_segmento_edad(df["AGE_YEARS"])

    if dimension == "Educación":
        return df["NAME_EDUCATION_TYPE"].map(ETIQUETAS_EDUCACION).fillna("Sin dato")

    if dimension == "Tipo de ingreso":
        return df["NAME_INCOME_TYPE"].map(ETIQUETAS_INGRESO).fillna("Sin dato")

    if dimension == "Historial de buró":
        return df["no_bureau_history"].map({0: "Con historial", 1: "Sin historial"})

    return _crear_segmento_credito(df["EXT_SOURCE_MEAN"])


def _ordenar_segmentos(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    orden = {
        "Edad": ORDEN_EDAD,
        "Educación": ORDEN_EDUCACION,
        "Tipo de ingreso": ORDEN_INGRESO,
        "Historial de buró": ORDEN_BUREAU,
        "Rango de crédito": ORDEN_CREDITO,
    }[dimension]

    df["segmento"] = pd.Categorical(df["segmento"], categories=orden, ordered=True)
    return df.sort_values("segmento").reset_index(drop=True)


def agrupar_por_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    df_trabajo = df.copy()
    df_trabajo["segmento"] = _crear_columna_segmento(df_trabajo, dimension)
    df_trabajo = df_trabajo.dropna(subset=["segmento"])

    agrupado = (
        df_trabajo.groupby("segmento", observed=False)
        .agg(
            total_clientes=("TARGET", "count"),
            clientes_default=("TARGET", "sum"),
        )
        .reset_index()
    )

    agrupado["clientes_default"] = agrupado["clientes_default"].astype(int)
    agrupado["tasa_default_pct"] = (
        agrupado["clientes_default"] / agrupado["total_clientes"] * 100
    )

    total_defaults = agrupado["clientes_default"].sum()
    agrupado["participacion_defaults_pct"] = (
        agrupado["clientes_default"] / total_defaults * 100 if total_defaults else 0
    )

    return _ordenar_segmentos(agrupado, dimension)


def calcular_kpis(df: pd.DataFrame) -> dict[str, str]:
    total_clientes = len(df)
    clientes_default = int(df["TARGET"].sum())
    tasa_default = clientes_default / total_clientes * 100 if total_clientes else 0

    return {
        "solicitudes": _formatear_numero(total_clientes),
        "tasa_default": _formatear_porcentaje(tasa_default),
        "clientes_default": _formatear_numero(clientes_default),
    }


def obtener_configuracion_metrica(metrica: str) -> dict:
    return {
        "Tasa de default": {
            "columna": "tasa_default_pct",
            "titulo": "Tasa de default por segmento",
            "eje_y": "Tasa de default (%)",
            "sufijo": "%",
        },
        "Cantidad absoluta de defaults": {
            "columna": "clientes_default",
            "titulo": "Cantidad absoluta de clientes en default",
            "eje_y": "Clientes en default",
            "sufijo": "",
        },
        "Participación en el total de defaults": {
            "columna": "participacion_defaults_pct",
            "titulo": "Participación de cada segmento dentro del total de defaults",
            "eje_y": "Participación en defaults (%)",
            "sufijo": "%",
        },
    }[metrica]


def render_kpi_card(icon: str, label: str, value: str, delta: str) -> None:
    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """
    )


def crear_grafica(
    df: pd.DataFrame,
    dimension: str,
    configuracion: dict,
) -> go.Figure:
    columna = configuracion["columna"]
    sufijo = configuracion["sufijo"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["segmento"].astype(str),
            y=df[columna],
            mode="lines+markers",
            name=configuracion["eje_y"],
            line={"color": "#e53935", "width": 3},
            marker={
                "size": 9,
                "color": "#e53935",
                "line": {"color": "#ff6659", "width": 1},
            },
            fill="tozeroy",
            fillcolor="rgba(229, 57, 53, 0.06)",
            customdata=df[
                ["total_clientes", "clientes_default", "tasa_default_pct", "participacion_defaults_pct"]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{configuracion['eje_y']}: %{{y:.1f}}{sufijo}<br>"
                "Total clientes: %{customdata[0]:,.0f}<br>"
                "Clientes default: %{customdata[1]:,.0f}<br>"
                "Tasa default: %{customdata[2]:.1f}%<br>"
                "Participación defaults: %{customdata[3]:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=420,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#9aa3af", "family": "Inter, Arial, sans-serif", "size": 12},
        xaxis={
            "title": "",
            "showgrid": False,
            "tickangle": -25,
            "linecolor": "rgba(255,255,255,0.12)",
            "tickfont": {"color": "#9aa3af"},
        },
        yaxis={
            "title": "",
            "gridcolor": "rgba(255,255,255,0.08)",
            "griddash": "dot",
            "zeroline": False,
            "tickfont": {"color": "#9aa3af"},
            "ticksuffix": "%" if sufijo == "%" else "",
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "font": {"color": "#9aa3af", "size": 12},
        },
        showlegend=True,
    )
    return fig


def render_vista_1() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df_base = cargar_datos()
    col_filtros, col_grafica = st.columns([1.05, 3.5], gap="medium")

    with col_filtros:
        with st.container(border=True):
            render_html(
                """
                <div class="filter-header">
                    <div class="panel-title" style="margin-bottom:0;">Filtros</div>
                    <span class="filter-clear">Limpiar filtros</span>
                </div>
                """
            )

            st.selectbox("Fecha", ["01 may. 2024 – 31 may. 2024", "Abril 2024", "Marzo 2024"])
            dimension = st.selectbox(
                "Segmento",
                list(DIMENSIONES.keys()),
                index=0,
            )
            metrica = st.selectbox(
                "Producto",
                [
                    "Tasa de default",
                    "Cantidad absoluta de defaults",
                    "Participación en el total de defaults",
                ],
                index=0,
            )
            historial_bureau = st.selectbox(
                "Canal",
                ["Todos los clientes", "Con historial", "Sin historial"],
                index=0,
            )
            st.number_input(
                "Mínimo de clientes",
                min_value=1,
                max_value=10000,
                value=100,
                step=50,
                key="minimo_clientes_v1",
            )

        df_filtrado = _aplicar_filtro_historial(df_base, historial_bureau)
        kpis = calcular_kpis(df_filtrado)

        with st.container(border=True):
            render_html('<div class="panel-title">Indicadores clave</div>')
            render_kpi_card("$", "Solicitudes analizadas", kpis["solicitudes"], "+0.0% ↑")
            render_kpi_card("↗", "Tasa general de default", kpis["tasa_default"], "+0.0% ↑")
            render_kpi_card("◎", "Clientes en default", kpis["clientes_default"], "-0.0% ↓")
            render_html('<a class="kpi-link" href="#">Ver todos los indicadores ›</a>')

    with col_grafica:
        configuracion = obtener_configuracion_metrica(metrica)
        minimo_clientes = st.session_state.get("minimo_clientes_v1", 100)

        df_visualizacion = agrupar_por_dimension(df_filtrado, dimension)

        segmentos_ocultos = df_visualizacion[
            df_visualizacion["total_clientes"] < minimo_clientes
        ]
        df_visible = df_visualizacion[
            df_visualizacion["total_clientes"] >= minimo_clientes
        ].copy()

        with st.container(border=True):
            render_html(
                f"""
                <div class="panel-title" style="margin-bottom:4px;">Visualización principal</div>
                <div class="panel-subtitle" style="margin:0 0 8px 0;">{configuracion["titulo"]}</div>
                """
            )

            st.selectbox("Granularidad", ["Diaria", "Semanal", "Mensual"], index=0)

            if df_visible.empty:
                st.warning("No hay segmentos con suficientes clientes para mostrar la gráfica.")
            else:
                grafica = crear_grafica(df_visible, dimension, configuracion)
                st.plotly_chart(
                    grafica,
                    use_container_width=True,
                    config={"displayModeBar": False, "responsive": True},
                )

            render_html(
                f"""
                <div class="chart-footer">
                    ⓘ &nbsp; Aquí se mostrará la visualización relacionada con la
                    <strong style="color:#ff5252;">
                    pregunta de negocio 1: ¿En qué segmentos se concentra el riesgo?
                    </strong>
                    Métrica: <strong style="color:#ffffff;">{metrica}</strong>.
                    Dimensión: <strong style="color:#ffffff;">{dimension}</strong>.
                </div>
                """
            )

        with st.expander("Ver tabla de detalle"):
            tabla = df_visualizacion.copy()
            tabla["segmento"] = tabla["segmento"].astype(str)
            tabla["tasa_default_pct"] = tabla["tasa_default_pct"].round(2)
            tabla["participacion_defaults_pct"] = tabla["participacion_defaults_pct"].round(2)
            st.dataframe(tabla, use_container_width=True, hide_index=True)

        if not segmentos_ocultos.empty:
            st.warning(
                f"Se ocultaron {len(segmentos_ocultos)} segmentos "
                f"porque tienen menos de {minimo_clientes} clientes."
            )
