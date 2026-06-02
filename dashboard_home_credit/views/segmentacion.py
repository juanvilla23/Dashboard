"""Agregación por segmento y gráficas compartidas entre vistas."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.render import render_html
from ui.theme import plotly_colors

DATA_PATH = Path(__file__).resolve().parent.parent / "train_selected_features.parquet"

METRICAS = [
    "Tasa de default",
    "Cantidad absoluta de defaults",
    "Participación en el total de defaults",
]

DIMENSIONES = {
    "Edad": "AGE_YEARS",
    "Ocupación": "OCCUPATION_TYPE",
    "Organización": "ORGANIZATION_TYPE",
    "Educación": "NAME_EDUCATION_TYPE",
    "Tipo de ingreso": "NAME_INCOME_TYPE",
    "Historial de buró": "no_bureau_history",
    "Rango de crédito": "EXT_SOURCE_MEAN",
    "Género": "CODE_GENDER",
}

ETIQUETAS_GENERO = {
    "M": "Hombre",
    "F": "Mujer",
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

ETIQUETAS_OCUPACION = {
    "Unknown": "Desconocido",
    "Laborers": "Obreros",
    "Sales staff": "Ventas",
    "Core staff": "Personal base",
    "Managers": "Gerentes",
    "Drivers": "Conductores",
    "High skill tech staff": "Técnico especializado",
    "Accountants": "Contadores",
    "Cooking staff": "Cocina",
    "Cleaning staff": "Limpieza",
    "Security staff": "Seguridad",
    "Waiters/barmen staff": "Meseros / barman",
    "Low skill Laborers": "Obreros baja calificación",
    "Private service staff": "Servicio privado",
    "Realty agents": "Agentes inmobiliarios",
    "Secretaries": "Secretarias",
    "Medicine staff": "Personal médico",
    "HR staff": "Recursos humanos",
    "IT staff": "TI",
}

ETIQUETAS_ORGANIZACION = {
    "unknown": "Desconocido",
    "Unknown": "Desconocido",
    "others": "Otros",
    "Other": "Otros",
    "Self-employed": "Independiente",
    "Business Entity Type 3": "Empresa tipo 3",
    "Business Entity Type 2": "Empresa tipo 2",
    "Business Entity Type 1": "Empresa tipo 1",
    "Government": "Gobierno",
    "Medicine": "Medicina",
    "School": "Educación",
    "Trade: type 7": "Comercio tipo 7",
    "Trade: type 6": "Comercio tipo 6",
    "Trade: type 5": "Comercio tipo 5",
    "Trade: type 4": "Comercio tipo 4",
    "Trade: type 3": "Comercio tipo 3",
    "Trade: type 2": "Comercio tipo 2",
    "Trade: type 1": "Comercio tipo 1",
    "Transport: type 4": "Transporte tipo 4",
    "Transport: type 3": "Transporte tipo 3",
    "Transport: type 2": "Transporte tipo 2",
    "Transport: type 1": "Transporte tipo 1",
    "Industry: type 11": "Industria tipo 11",
    "Industry: type 9": "Industria tipo 9",
    "Industry: type 7": "Industria tipo 7",
    "Industry: type 6": "Industria tipo 6",
    "Industry: type 5": "Industria tipo 5",
    "Industry: type 3": "Industria tipo 3",
    "Industry: type 2": "Industria tipo 2",
    "Industry: type 1": "Industria tipo 1",
    "Security Ministries": "Seguridad / ministerios",
    "Services": "Servicios",
    "Police": "Policía",
    "Military": "Militar",
    "Housing": "Vivienda",
    "Construction Company": "Construcción",
    "Bank": "Banco",
    "Religion": "Religión",
    "Postal": "Correo",
    "Mobile": "Telecomunicaciones",
    "Electricity": "Electricidad",
    "Insurance": "Seguros",
}

ORDEN_EDUCACION = list(ETIQUETAS_EDUCACION.values())
ORDEN_INGRESO = list(ETIQUETAS_INGRESO.values())
ORDEN_EDAD = [
    "20-25 años", "25-30 años", "30-35 años", "35-40 años", "40-45 años",
    "45-50 años", "50-55 años", "55-60 años", "60-65 años", "65-70 años",
]

TITULOS_EJE_X = {
    "Edad": "Edad (años)",
    "Educación": "Nivel educativo",
    "Tipo de ingreso": "Tipo de ingreso",
    "Ocupación": "Ocupación",
    "Organización": "Organización",
    "Historial de buró": "Historial de buró",
    "Rango de crédito": "Rango de score externo",
    "Género": "Género",
}
ORDEN_CREDITO = ["Muy bajo", "Bajo", "Medio", "Medio alto", "Alto", "Muy alto"]
ORDEN_BUREAU = ["Con historial", "Sin historial"]
ORDEN_GENERO = ["Hombre", "Mujer"]


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.read_parquet(DATA_PATH)


def formatear_numero(valor: float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def formatear_porcentaje(valor: float) -> str:
    return f"{valor:.1f}%".replace(".", ",")


def crear_segmento_edad(edades: pd.Series) -> pd.Series:
    bins = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    return pd.cut(edades, bins=bins, labels=ORDEN_EDAD, right=False)


def crear_segmento_credito(puntajes: pd.Series) -> pd.Series:
    return pd.qcut(
        puntajes.rank(method="first"),
        q=len(ORDEN_CREDITO),
        labels=ORDEN_CREDITO,
    )


def aplicar_filtro_historial(df: pd.DataFrame, historial_bureau: str) -> pd.DataFrame:
    if historial_bureau == "Con historial":
        return df[df["no_bureau_history"] == 0]
    if historial_bureau == "Sin historial":
        return df[df["no_bureau_history"] == 1]
    return df


def crear_columna_segmento(df: pd.DataFrame, dimension: str) -> pd.Series:
    if dimension == "Edad":
        return crear_segmento_edad(df["AGE_YEARS"])

    if dimension == "Educación":
        return df["NAME_EDUCATION_TYPE"].map(ETIQUETAS_EDUCACION).fillna("Sin dato")

    if dimension == "Tipo de ingreso":
        return df["NAME_INCOME_TYPE"].map(ETIQUETAS_INGRESO).fillna("Sin dato")

    if dimension == "Ocupación":
        serie = df["OCCUPATION_TYPE"].map(ETIQUETAS_OCUPACION)
        return serie.fillna(df["OCCUPATION_TYPE"].astype(str))

    if dimension == "Organización":
        serie = df["ORGANIZATION_TYPE"].map(ETIQUETAS_ORGANIZACION)
        return serie.fillna(df["ORGANIZATION_TYPE"].astype(str))

    if dimension == "Historial de buró":
        return df["no_bureau_history"].map({0: "Con historial", 1: "Sin historial"})

    if dimension == "Género":
        return df["CODE_GENDER"].map(ETIQUETAS_GENERO)

    return crear_segmento_credito(df["EXT_SOURCE_MEAN"])


def ordenar_segmentos(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    orden_fijo = {
        "Edad": ORDEN_EDAD,
        "Educación": ORDEN_EDUCACION,
        "Tipo de ingreso": ORDEN_INGRESO,
        "Historial de buró": ORDEN_BUREAU,
        "Rango de crédito": ORDEN_CREDITO,
        "Género": ORDEN_GENERO,
    }

    if dimension in orden_fijo:
        df["segmento"] = pd.Categorical(df["segmento"], categories=orden_fijo[dimension], ordered=True)
        return df.sort_values("segmento").reset_index(drop=True)

    return df.sort_values("clientes_default", ascending=False).reset_index(drop=True)


def agrupar_por_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    df_trabajo = df.copy()
    df_trabajo["segmento"] = crear_columna_segmento(df_trabajo, dimension)
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

    return ordenar_segmentos(agrupado, dimension)


def calcular_kpis(df: pd.DataFrame) -> dict[str, str]:
    total_clientes = len(df)
    clientes_default = int(df["TARGET"].sum())
    tasa_default = clientes_default / total_clientes * 100 if total_clientes else 0

    return {
        "solicitudes": formatear_numero(total_clientes),
        "tasa_default": formatear_porcentaje(tasa_default),
        "clientes_default": formatear_numero(clientes_default),
    }


def obtener_configuracion_metrica(metrica: str) -> dict:
    return {
        "Tasa de default": {
            "columna": "tasa_default_pct",
            "titulo": "Tasa de default por segmento",
            "eje_y": "Tasa de default (%)",
            "sufijo": "%",
            "enfoque": "riesgo (política)",
        },
        "Cantidad absoluta de defaults": {
            "columna": "clientes_default",
            "titulo": "Volumen de clientes en default",
            "eje_y": "Clientes en default",
            "sufijo": "",
            "enfoque": "volumen (pérdidas)",
        },
        "Participación en el total de defaults": {
            "columna": "participacion_defaults_pct",
            "titulo": "Participación en el total de defaults",
            "eje_y": "Participación en defaults (%)",
            "sufijo": "%",
            "enfoque": "concentración (pérdidas)",
        },
    }[metrica]


def segmentos_destacados(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    idx_tasa = df["tasa_default_pct"].idxmax()
    idx_volumen = df["clientes_default"].idxmax()
    idx_participacion = df["participacion_defaults_pct"].idxmax()

    return {
        "tasa": df.loc[idx_tasa],
        "volumen": df.loc[idx_volumen],
        "participacion": df.loc[idx_participacion],
    }


def texto_insight_riesgo_volumen(df: pd.DataFrame, dimension: str) -> str:
    destacados = segmentos_destacados(df)
    if not destacados:
        return "No hay datos suficientes para comparar riesgo y volumen."

    tasa = destacados["tasa"]
    volumen = destacados["volumen"]
    participacion = destacados["participacion"]

    mismo_volumen_participacion = volumen["segmento"] == participacion["segmento"]

    texto = (
        f"En <strong>{dimension}</strong>, el segmento con mayor "
        f"<strong style='color:#ff5252;'>tasa de default</strong> es "
        f"<strong>{tasa['segmento']}</strong> ({tasa['tasa_default_pct']:.1f}%). "
        f"El que concentra más <strong style='color:#ff5252;'>pérdidas en volumen</strong> es "
        f"<strong>{volumen['segmento']}</strong> ({int(volumen['clientes_default']):,} clientes, "
        f"{volumen['participacion_defaults_pct']:.1f}% del total)."
    ).replace(",", ".")

    if not mismo_volumen_participacion:
        texto += (
            f" La mayor <strong>participación relativa</strong> está en "
            f"<strong>{participacion['segmento']}</strong> "
            f"({participacion['participacion_defaults_pct']:.1f}%)."
        )

    if tasa["segmento"] != participacion["segmento"]:
        texto += (
            f" Ejemplo: <strong>{participacion['segmento']}</strong> lidera participación "
            f"({participacion['participacion_defaults_pct']:.1f}%), pero "
            f"<strong>{tasa['segmento']}</strong> tiene mayor tasa "
            f"({tasa['tasa_default_pct']:.1f}%) — útil para decidir política (tasa) "
            f"vs dónde se acumulan pérdidas (volumen)."
        )
    else:
        texto += (
            " En esta dimensión, riesgo y volumen coinciden en el mismo segmento."
        )

    return texto


def calcular_tasa_general_default(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df["TARGET"].mean() * 100)


def colores_barras_tasa_default(valores: pd.Series, tasa_base: float) -> tuple[list[str], list[int]]:
    """Verde (bajo), amarillo (cerca de la base), rojo (por encima de la base)."""
    colores: list[str] = []
    anchos: list[int] = []

    for valor in valores.astype(float):
        if valor > tasa_base:
            exceso = (valor - tasa_base) / max(tasa_base, 0.5)
            intensidad = min(1.0, 0.72 + exceso * 0.12)
            colores.append(f"rgba(229, 57, 53, {intensidad})")
            anchos.append(2)
        elif valor < tasa_base * 0.92:
            colores.append("rgba(76, 175, 80, 0.85)")
            anchos.append(1)
        else:
            colores.append("rgba(255, 235, 59, 0.92)")
            anchos.append(1)

    return colores, anchos


def colores_destacar_maximo(valores: pd.Series) -> tuple[list[str], list[int]]:
    """Solo resalta la barra con el valor más alto; el resto en gris neutro."""
    maximo = float(valores.max())
    colores: list[str] = []
    anchos: list[int] = []

    for valor in valores.astype(float):
        if valor >= maximo:
            colores.append("rgba(229, 57, 53, 0.95)")
            anchos.append(2)
        else:
            colores.append("rgba(100, 106, 115, 0.5)")
            anchos.append(1)

    return colores, anchos


def anadir_linea_tasa_general(fig: go.Figure, tasa_base: float) -> None:
    colors = plotly_colors()
    fig.add_hline(
        y=tasa_base,
        line_dash="dash",
        line_color=colors["ref_line"],
        line_width=1.5,
        annotation_text=f"Tasa general: {tasa_base:.1f}%",
        annotation_position="top right",
        annotation_font_color=colors["annotation_text"],
        annotation_font_size=12,
        annotation_bgcolor=colors["annotation_bg"],
    )


def render_indicadores_clave(df: pd.DataFrame | None = None) -> None:
    """Panel global de KPIs (debajo de las pestañas de vista)."""
    if df is None:
        if not DATA_PATH.exists():
            return
        df = cargar_datos()

    kpis = calcular_kpis(df)
    with st.container(border=True):
        render_html('<div class="panel-title" style="margin-bottom:4px;">Indicadores clave</div>')
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            render_kpi_card("$", "Solicitudes analizadas", kpis["solicitudes"], "+0.0% ↑")
        with col2:
            render_kpi_card("↗", "Tasa general de default", kpis["tasa_default"], "+0.0% ↑")
        with col3:
            render_kpi_card("◎", "Clientes en default", kpis["clientes_default"], "-0.0% ↓")


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


def _texto_barras(valores: pd.Series, sufijo: str) -> list[str]:
    if sufijo == "%":
        return [f"{v:.1f}%" for v in valores]
    return [f"{v:,.0f}".replace(",", ".") for v in valores]


def crear_grafica_barras(
    df: pd.DataFrame,
    configuracion: dict,
    destacar_riesgo_volumen: bool = False,
    tasa_general: float | None = None,
    dimension: str | None = None,
) -> go.Figure:
    columna = configuracion["columna"]
    sufijo = configuracion["sufijo"]
    segmentos = df["segmento"].astype(str).tolist()
    texto_barras = _texto_barras(df[columna], sufijo)

    colores = ["rgba(229, 57, 53, 0.75)"] * len(df)
    anchos_linea = [1] * len(df)

    if columna == "tasa_default_pct" and tasa_general is not None:
        colores, anchos_linea = colores_barras_tasa_default(df[columna], tasa_general)
    elif columna in ("clientes_default", "participacion_defaults_pct") and not df.empty:
        colores, anchos_linea = colores_destacar_maximo(df[columna])
    elif destacar_riesgo_volumen and not df.empty:
        destacados = segmentos_destacados(df)
        etiquetas_destacadas = {
            str(destacados["tasa"]["segmento"]),
            str(destacados["participacion"]["segmento"]),
        }
        colores = [
            "rgba(255, 120, 80, 0.95)" if seg in etiquetas_destacadas else "rgba(229, 57, 53, 0.45)"
            for seg in segmentos
        ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=segmentos,
            y=df[columna],
            name=configuracion["eje_y"],
            text=texto_barras,
            textposition="outside",
            marker={
                "color": colores,
                "line": {"color": colores, "width": anchos_linea},
            },
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

    colors = plotly_colors()
    fig.update_layout(
        height=440,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        bargap=0.28,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["font"], "family": "Inter, Arial, sans-serif", "size": 12},
        xaxis={
            "title": TITULOS_EJE_X.get(dimension or "", ""),
            "showgrid": False,
            "tickangle": -30,
            "linecolor": colors["line"],
            "tickfont": {"color": colors["font"]},
        },
        yaxis={
            "title": configuracion["eje_y"],
            "gridcolor": colors["grid"],
            "griddash": "dot",
            "zeroline": False,
            "tickfont": {"color": colors["font"]},
            "ticksuffix": "%" if sufijo == "%" else "",
        },
        showlegend=False,
    )

    if columna == "tasa_default_pct" and tasa_general is not None:
        anadir_linea_tasa_general(fig, tasa_general)
        y_max = max(float(df[columna].max()), tasa_general) * 1.12
        fig.update_yaxes(range=[0, y_max])

    return fig
