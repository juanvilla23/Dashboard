"""Capa de datos del Perfilador de Riesgo (Vista 4)."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "train_selected_features.parquet"

BASE_RATE = 0.080729
N_TOTAL = 307511
TOTAL_DEFAULTS = 24825
MIN_N = 300

SCORE_P33 = 0.471074
SCORE_P66 = 0.565759

DIMS = [
    "band_score",
    "band_edad",
    "CODE_GENDER",
    "NAME_EDUCATION_TYPE",
    "NAME_INCOME_TYPE",
    "OCCUPATION_TYPE",
    "band_activos",
    "band_empleo",
    "buro_flag",
]

DIM_LABELS = {
    "band_score": "Banda de puntuación externa",
    "band_edad": "Rango de edad",
    "CODE_GENDER": "Género",
    "NAME_EDUCATION_TYPE": "Nivel educativo",
    "NAME_INCOME_TYPE": "Tipo de ingreso",
    "OCCUPATION_TYPE": "Ocupación",
    "band_activos": "Créditos activos en buró",
    "band_empleo": "Antigüedad laboral",
    "buro_flag": "Historial de buró",
}

ETIQUETAS_GENERO = {"M": "Hombre", "F": "Mujer"}

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
    "Unknown": "Sin ocupación registrada",
    "Laborers": "Obreros",
    "Sales staff": "Ventas",
    "Core staff": "Personal base",
    "Managers": "Gerentes",
    "Drivers": "Conductores",
    "High skill tech staff": "Técnico especializado",
    "Accountants": "Contadores",
    "Medicine staff": "Personal médico",
    "Security staff": "Seguridad",
    "Cooking staff": "Cocina",
    "Cleaning staff": "Limpieza",
    "Waiters/barmen staff": "Meseros / barman",
    "Low-skill Laborers": "Obreros de baja cualificación",
    "Private service staff": "Servicio privado",
    "Realty agents": "Agentes inmobiliarios",
    "Secretaries": "Secretarias",
    "HR staff": "Recursos humanos",
    "IT staff": "Tecnología de la información",
}

EDUC_ORDER = list(ETIQUETAS_EDUCACION.values())

OCCUPATION_ORDER = [
    ETIQUETAS_OCUPACION["Unknown"],
    ETIQUETAS_OCUPACION["Laborers"],
    ETIQUETAS_OCUPACION["Sales staff"],
    ETIQUETAS_OCUPACION["Core staff"],
    ETIQUETAS_OCUPACION["Managers"],
    ETIQUETAS_OCUPACION["Drivers"],
    ETIQUETAS_OCUPACION["High skill tech staff"],
    ETIQUETAS_OCUPACION["Accountants"],
    ETIQUETAS_OCUPACION["Medicine staff"],
    ETIQUETAS_OCUPACION["Security staff"],
    ETIQUETAS_OCUPACION["Cooking staff"],
    ETIQUETAS_OCUPACION["Cleaning staff"],
    ETIQUETAS_OCUPACION["Private service staff"],
    ETIQUETAS_OCUPACION["Low-skill Laborers"],
    ETIQUETAS_OCUPACION["Waiters/barmen staff"],
    ETIQUETAS_OCUPACION["Secretaries"],
    ETIQUETAS_OCUPACION["Realty agents"],
    ETIQUETAS_OCUPACION["HR staff"],
    ETIQUETAS_OCUPACION["IT staff"],
]

EMPLEO_ORDER = [
    "< 1 año",
    "1-3 años",
    "3-5 años",
    "5-10 años",
    "10-20 años",
    "20+ años",
    "Sin dato",
]

ACTIVOS_ORDER = ["0", "1", "2", "3", "4", "5 o más"]

SCORE_ORDER = [
    "Bajo (tercil inferior)",
    "Medio (tercil medio)",
    "Alto (tercil superior)",
]

SMALL_INCOME_TYPES = {
    ETIQUETAS_INGRESO["Maternity leave"]: 5,
    ETIQUETAS_INGRESO["Unemployed"]: 22,
    ETIQUETAS_INGRESO["Student"]: 18,
    ETIQUETAS_INGRESO["Businessman"]: 10,
}

ACADEMIC_DEGREE_ES = ETIQUETAS_EDUCACION["Academic degree"]


def lift_color(lift: float) -> str:
    if lift >= 1.50:
        return "#c0281e"
    if lift >= 1.20:
        return "#e8392e"
    if lift >= 1.05:
        return "#e8832e"
    if lift > 0.95:
        return "#b0a898"
    if lift > 0.80:
        return "#2e9e8e"
    return "#1db89a"


def lift_label(lift: float) -> str:
    if lift >= 1.50:
        return "Riesgo muy alto"
    if lift >= 1.20:
        return "Riesgo alto"
    if lift >= 1.05:
        return "Riesgo moderado"
    if lift > 0.95:
        return "En línea con la base"
    if lift > 0.80:
        return "Riesgo bajo"
    return "Riesgo muy bajo"


def display_value(dim: str, value: str) -> str:
    """Etiqueta en español para mostrar en UI (valores ya vienen en español del cubo)."""
    return str(value)


@st.cache_data
def load_and_bin() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)

    score_bins = [-np.inf, SCORE_P33, SCORE_P66, np.inf]
    df["band_score"] = (
        pd.cut(df["EXT_SOURCE_MEAN"], bins=score_bins, labels=SCORE_ORDER)
        .astype(str)
    )

    edad_bins = list(range(20, 75, 5))
    edad_labels = [f"{b}-{b + 5} años" for b in edad_bins[:-1]]
    df["band_edad"] = (
        pd.cut(df["AGE_YEARS"], bins=edad_bins, right=False, labels=edad_labels)
        .astype(str)
    )

    df = df[df["CODE_GENDER"].isin(["M", "F"])].copy()
    df["CODE_GENDER"] = df["CODE_GENDER"].map(ETIQUETAS_GENERO)

    df["NAME_EDUCATION_TYPE"] = df["NAME_EDUCATION_TYPE"].map(ETIQUETAS_EDUCACION)
    df["NAME_INCOME_TYPE"] = df["NAME_INCOME_TYPE"].map(ETIQUETAS_INGRESO)

    df["OCCUPATION_TYPE"] = df["OCCUPATION_TYPE"].fillna("Unknown").map(ETIQUETAS_OCUPACION)

    df["band_activos"] = (
        df["bureau_n_active"]
        .fillna(0)
        .astype(int)
        .clip(upper=5)
        .map(lambda x: str(x) if x < 5 else "5 o más")
    )

    years_emp = (-df["DAYS_EMPLOYED"] / 365).clip(lower=0)
    emp_bins = [-0.001, 1, 3, 5, 10, 20, np.inf]
    emp_labels = ["< 1 año", "1-3 años", "3-5 años", "5-10 años", "10-20 años", "20+ años"]
    df["band_empleo"] = pd.cut(years_emp, bins=emp_bins, labels=emp_labels).astype(str)
    df["band_empleo"] = df["band_empleo"].replace("nan", "Sin dato")

    df["buro_flag"] = np.where(
        df["no_bureau_history"] == 1, "Sin historial", "Con historial"
    )

    keep = DIMS + ["TARGET"]
    return df[keep].copy()


@st.cache_data
def build_cube(_df: pd.DataFrame) -> pd.DataFrame:
    return (
        _df.groupby(DIMS, observed=True)["TARGET"]
        .agg(n="size", defaults="sum")
        .reset_index()
    )


def apply_filters(cube: pd.DataFrame, selection: dict) -> pd.DataFrame:
    mask = pd.Series(True, index=cube.index)
    for dim, vals in selection.items():
        if vals:
            mask &= cube[dim].isin(vals)
    return cube[mask]


def segment_stats(
    filtered: pd.DataFrame,
    n_total: int = N_TOTAL,
    total_defaults: int = TOTAL_DEFAULTS,
) -> dict:
    n = int(filtered["n"].sum())
    d = int(filtered["defaults"].sum())
    rate = d / n if n > 0 else 0.0
    lift = rate / BASE_RATE if n > 0 else 0.0
    return {
        "n": n,
        "defaults": d,
        "rate": rate,
        "lift": lift,
        "delta_pp": (rate - BASE_RATE) * 100,
        "pct_cartera": n / n_total if n_total else 0.0,
        "pct_defaults": d / total_defaults if total_defaults else 0.0,
        "low_n": n < MIN_N,
    }


def breakdown(
    cube: pd.DataFrame,
    selection: dict,
    dim_to_break: str,
) -> pd.DataFrame:
    sel_sin_esa_dim = {k: v for k, v in selection.items() if k != dim_to_break}
    sub = apply_filters(cube, sel_sin_esa_dim)
    rows = (
        sub.groupby(dim_to_break, observed=True)[["n", "defaults"]]
        .sum()
        .reset_index()
    )
    rows = rows[rows["n"] > 0].copy()
    rows["rate"] = rows["defaults"] / rows["n"]
    rows["lift"] = rows["rate"] / BASE_RATE
    rows["low_n"] = rows["n"] < MIN_N
    return rows.sort_values("rate", ascending=False)


def dim_options(cube: pd.DataFrame, dim: str) -> list[str]:
    values = cube[dim].dropna().unique().tolist()
    order_map = {
        "band_score": SCORE_ORDER,
        "band_edad": [f"{b}-{b + 5} años" for b in range(20, 70, 5)],
        "CODE_GENDER": list(ETIQUETAS_GENERO.values()),
        "NAME_EDUCATION_TYPE": EDUC_ORDER,
        "OCCUPATION_TYPE": OCCUPATION_ORDER,
        "band_activos": ACTIVOS_ORDER,
        "band_empleo": EMPLEO_ORDER,
        "buro_flag": ["Con historial", "Sin historial"],
    }
    if dim in order_map:
        ordered = [v for v in order_map[dim] if v in values]
        rest = sorted(v for v in values if v not in ordered)
        return ordered + rest
    return sorted(values, key=str)


def multiselect_display_options(dim: str, options: list[str]) -> list[str]:
    return [display_value(dim, o) for o in options]


def selection_from_display(dim: str, selected_display: list[str], options: list[str]) -> list[str]:
    return selected_display
