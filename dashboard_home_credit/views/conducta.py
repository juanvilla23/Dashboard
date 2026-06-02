"""Variables de comportamiento crediticio previo y matrices de riesgo."""

import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from logic_v1 import BASE_RATE, SCORE_P33, SCORE_P66, lift_color
from ui.theme import plotly_colors
from views.segmentacion import anadir_linea_tasa_general, colores_barras_tasa_default

BASE_RATE_PCT = BASE_RATE * 100

MATRIX_FILAS_RECHAZO = ["0%", "1-25%", "25-50%", "50-75%", "75-100%"]
MATRIX_COLS_SOLICITUDES = ["1-2", "3-5", "6+"]

BANDAS_SCORE_MATRIZ = ["Score bajo", "Score medio", "Score alto"]
GRUPOS_BURO_MATRIZ = ["Con historial de buró", "Sin historial de buró"]

VARIABLES_CONDUCTA = {
    "Nº créditos activos": {
        "columna": "bureau_n_active",
        "descripcion": "Créditos vigentes reportados en buró",
    },
    "Tasa de rechazo previa": {
        "columna": "prev_refused_rate",
        "descripcion": "Proporción de solicitudes previas rechazadas",
    },
    "Nº solicitudes previas": {
        "columna": "prev_app_count",
        "descripcion": "Historial de solicitudes anteriores en la entidad",
    },
    "Endeudamiento": {
        "columna": "bureau_debt_ratio",
        "descripcion": "Ratio deuda total / crédito en buró (winsorizado)",
    },
}

TERCERAS_DIMENSIONES = {
    "Sin tercera dimensión": None,
    "Banda de score externo": "score",
    "Con / sin historial de buró": "buro",
}


def _banda_conteo_activos(valores: pd.Series) -> pd.Series:
    return pd.cut(
        valores,
        bins=[-0.1, 0.9, 1.9, 3.9, 6.9, 10.9, 999],
        labels=["0", "1", "2-3", "4-6", "7-10", "11+"],
    )


def _banda_solicitudes(valores: pd.Series) -> pd.Series:
    return pd.cut(
        valores,
        bins=[-0.1, 0.9, 1.9, 2.9, 4.9, 7.9, 999],
        labels=["0", "1", "2", "3-4", "5-7", "8+"],
    )


def _banda_rechazo(valores: pd.Series) -> pd.Series:
    pct = valores * 100
    return pd.cut(
        pct,
        bins=[-0.1, 0.1, 10, 25, 50, 75, 100.1],
        labels=["0%", "1-10%", "11-25%", "26-50%", "51-75%", "76-100%"],
    )


def _banda_endeudamiento(valores: pd.Series) -> pd.Series:
    limpio = valores.clip(valores.quantile(0.01), valores.quantile(0.99))
    return pd.qcut(
        limpio.rank(method="first"),
        q=5,
        labels=["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"],
    )


def _banda_rechazo_matriz(valores: pd.Series) -> pd.Series:
    pct = valores * 100
    return pd.cut(
        pct,
        bins=[-0.1, 0.1, 25, 50, 75, 100.1],
        labels=MATRIX_FILAS_RECHAZO,
    )


def _banda_solicitudes_matriz(valores: pd.Series) -> pd.Series:
    return pd.cut(
        valores,
        bins=[0.9, 2.9, 5.9, 9999],
        labels=MATRIX_COLS_SOLICITUDES,
    )


def _banda_score_matriz(valores: pd.Series) -> pd.Series:
  return pd.cut(
      valores,
      bins=[-np.inf, SCORE_P33, SCORE_P66, np.inf],
      labels=BANDAS_SCORE_MATRIZ,
  )


def crear_bandas(df: pd.DataFrame, nombre_variable: str) -> pd.Series:
    columna = VARIABLES_CONDUCTA[nombre_variable]["columna"]
    valores = df[columna]

    if nombre_variable == "Nº créditos activos":
        return _banda_conteo_activos(valores)
    if nombre_variable == "Nº solicitudes previas":
        return _banda_solicitudes(valores)
    if nombre_variable == "Tasa de rechazo previa":
        return _banda_rechazo(valores)
    return _banda_endeudamiento(valores)


def agrupar_curva_riesgo(df: pd.DataFrame, nombre_variable: str) -> pd.DataFrame:
    trabajo = df.copy()
    trabajo["segmento"] = crear_bandas(trabajo, nombre_variable)
    trabajo = trabajo.dropna(subset=["segmento"])

    agrupado = (
        trabajo.groupby("segmento", observed=False)
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
    agrupado["segmento"] = agrupado["segmento"].astype(str)
    return agrupado


def _preparar_matriz_base(df: pd.DataFrame) -> pd.DataFrame:
    trabajo = df.copy()
    trabajo["banda_rechazo"] = _banda_rechazo_matriz(trabajo["prev_refused_rate"])
    trabajo["banda_solicitudes"] = _banda_solicitudes_matriz(trabajo["prev_app_count"])
    trabajo["banda_score"] = _banda_score_matriz(trabajo["EXT_SOURCE_MEAN"])
    trabajo["grupo_buro"] = trabajo["no_bureau_history"].map(
        {0: GRUPOS_BURO_MATRIZ[0], 1: GRUPOS_BURO_MATRIZ[1]}
    )
    return trabajo.dropna(subset=["banda_rechazo", "banda_solicitudes"])


def agrupar_matriz(
    df: pd.DataFrame,
    tercera_dimension: str | None,
    filtro_tercera: str | None = None,
    minimo_celda: int = 30,
) -> pd.DataFrame:
    trabajo = _preparar_matriz_base(df)

    if tercera_dimension == "score" and filtro_tercera:
        trabajo = trabajo[trabajo["banda_score"].astype(str) == filtro_tercera]
    elif tercera_dimension == "buro" and filtro_tercera:
        trabajo = trabajo[trabajo["grupo_buro"] == filtro_tercera]

    matriz = (
        trabajo.groupby(["banda_rechazo", "banda_solicitudes"], observed=False)
        .agg(
            total=("TARGET", "count"),
            defaults=("TARGET", "sum"),
        )
        .reset_index()
    )
    matriz["tasa_default_pct"] = matriz["defaults"] / matriz["total"] * 100
    matriz.loc[matriz["total"] < minimo_celda, "tasa_default_pct"] = np.nan
    matriz["banda_rechazo"] = matriz["banda_rechazo"].astype(str)
    matriz["banda_solicitudes"] = matriz["banda_solicitudes"].astype(str)
    return matriz


def opciones_filtro_tercera(df: pd.DataFrame, tercera_dimension: str | None) -> list[str]:
    if tercera_dimension is None:
        return ["Todas"]

    if tercera_dimension == "score":
        return BANDAS_SCORE_MATRIZ
    if tercera_dimension == "buro":
        return GRUPOS_BURO_MATRIZ
    return ["Todas"]


def _hex_a_rgba(color_hex: str, alpha: float = 0.22) -> str:
    h = color_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _fmt_clientes_celda(n: int) -> str:
    if n >= 1000:
        miles = n / 1000
        texto = f"{miles:.1f}".replace(".", ",")
        if texto.endswith(",0"):
            texto = texto[:-2]
        return f"{texto}k"
    return f"{n:,}".replace(",", ".")


def estilos_matriz_html() -> str:
    return """
    <style>
    .v2-celda:hover { transform: scale(1.02); z-index: 1; }
    .v2-matriz-leyenda {
        display: flex;
        flex-wrap: wrap;
        gap: 10px 16px;
        margin-top: 14px;
        font-size: 12px;
        color: var(--text-secondary);
    }
    .v2-matriz-leyenda span { display: inline-flex; align-items: center; gap: 5px; }
    .v2-leyenda-punto { width: 10px; height: 10px; border-radius: 3px; }
    </style>
    """


def _celda_html(
    fila: str,
    col: str,
    matriz: pd.DataFrame,
    minimo_celda: int,
) -> str:
    match = matriz[
        (matriz["banda_rechazo"] == fila) & (matriz["banda_solicitudes"] == col)
    ]
    if match.empty:
        return '<div class="v2-celda v2-celda-vacia" title="Sin datos">—</div>'

    fila_datos = match.iloc[0]
    total = int(fila_datos["total"])
    if total < minimo_celda or pd.isna(fila_datos["tasa_default_pct"]):
        return (
            f'<div class="v2-celda v2-celda-vacia" '
            f'title="Muestra insuficiente (n={total})">—</div>'
        )

    tasa_pct = float(fila_datos["tasa_default_pct"])
    lift = (tasa_pct / 100) / BASE_RATE
    color = lift_color(lift)
    fondo = _hex_a_rgba(color, 0.28)
    tooltip = (
        f"Tasa de impago: {tasa_pct:.1f}% · Índice: {lift:.2f}× · "
        f"Clientes: {_fmt_clientes_celda(total)}"
    )
    return f"""
    <div class="v2-celda" style="background:{fondo}; border-color:{_hex_a_rgba(color, 0.45)};"
         title="{html.escape(tooltip)}">
        <div class="v2-celda-tasa" style="color:{color};">{tasa_pct:.1f}%</div>
        <div class="v2-celda-lift" style="color:{color};">{lift:.2f}×</div>
        <div class="v2-celda-n">{_fmt_clientes_celda(total)}</div>
    </div>
    """


def crear_matriz_html(
    matriz: pd.DataFrame,
    titulo: str,
    minimo_celda: int = 30,
) -> str:
    filas_html = ['<div class="v2-matriz-corner"></div>']
    for col in MATRIX_COLS_SOLICITUDES:
        filas_html.append(
            f'<div class="v2-matriz-col-head">{html.escape(col)}</div>'
        )

    for fila in MATRIX_FILAS_RECHAZO:
        filas_html.append(f'<div class="v2-matriz-row-head">{html.escape(fila)}</div>')
        for col in MATRIX_COLS_SOLICITUDES:
            filas_html.append(_celda_html(fila, col, matriz, minimo_celda))

    leyenda_items = [
        ("#1db89a", "Por debajo de la base"),
        ("#b0a898", "Cerca de la base (8,07%)"),
        ("#e8832e", "Riesgo moderado"),
        ("#e8392e", "Riesgo alto"),
        ("#c0281e", "Riesgo muy alto"),
    ]
    leyenda = "".join(
        f'<span><i class="v2-leyenda-punto" style="background:{c};"></i>{t}</span>'
        for c, t in leyenda_items
    )

    return f"""
    <div class="v2-matriz-panel">
        <div class="v2-matriz-titulo">{html.escape(titulo)}</div>
        <div class="v2-matriz-outer">
            <div class="v2-eje-y-label" title="Eje vertical">Tasa de rechazo ↓</div>
            <div class="v2-matriz-main">
                <div class="v2-eje-x-label" title="Eje horizontal">Nº solicitudes →</div>
                <div class="v2-matriz-grid">{''.join(filas_html)}</div>
            </div>
        </div>
        <div class="v2-matriz-leyenda">{leyenda}</div>
    </div>
    """


def crear_grafica_curva(
    df_agrupado: pd.DataFrame,
    nombre_variable: str,
    tasa_general: float | None = None,
) -> go.Figure:
    tasas = df_agrupado["tasa_default_pct"]
    colores, anchos = colores_barras_tasa_default(tasas, tasa_general or float(tasas.mean()))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_agrupado["segmento"],
            y=tasas,
            marker={"color": colores, "line": {"color": colores, "width": anchos}},
            text=[f"{v:.1f}%" for v in tasas],
            textposition="outside",
            customdata=df_agrupado[["total_clientes", "clientes_default"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Tasa de impago: %{y:.1f}%<br>"
                "Clientes: %{customdata[0]:,.0f}<br>"
                "Impagos: %{customdata[1]:,.0f}"
                "<extra></extra>"
            ),
            name="Tasa de impago",
        )
    )
    colors = plotly_colors()
    fig.update_layout(
        height=360,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        bargap=0.25,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["font"], "size": 12},
        xaxis={"title": nombre_variable, "tickangle": -20, "linecolor": colors["line"]},
        yaxis={"title": "Tasa de impago (%)", "gridcolor": colors["grid"]},
        showlegend=False,
    )

    if tasa_general is not None:
        anadir_linea_tasa_general(fig, tasa_general)
        y_max = max(float(tasas.max()), tasa_general) * 1.12
        fig.update_yaxes(range=[0, y_max])

    return fig


def crear_matrices_html(
    paneles: list[tuple[pd.DataFrame, str]],
    minimo_celda: int = 30,
) -> str:
    """Varias matrices en fila (score, buró, etc.)."""
    cuerpo = "".join(
        crear_matriz_html(matriz, titulo, minimo_celda) for matriz, titulo in paneles
    )
    return f'<div class="v2-matrices-wrap">{cuerpo}</div>'
