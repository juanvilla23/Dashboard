"""Vista 4: Perfilador de riesgo crediticio."""

import streamlit as st
import plotly.graph_objects as go

from logic_v1 import (
    BASE_RATE,
    DIMS,
    DIM_LABELS,
    DATA_PATH,
    SMALL_INCOME_TYPES,
    apply_filters,
    breakdown,
    build_cube,
    dim_options,
    ACADEMIC_DEGREE_ES,
    display_value,
    lift_color,
    lift_label,
    load_and_bin,
    multiselect_display_options,
    segment_stats,
    selection_from_display,
)
from ui.render import render_html
from ui.theme import plotly_colors

MULTISELECT_PLACEHOLDER = "Selecciona opciones"

PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
BASE_RATE_PCT = BASE_RATE * 100


def _fmt_num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _render_metric_card(label: str, value: str, color: str, subtitle: str = "") -> str:
    sub_html = f'<div class="v4-metric-sub">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="v4-metric">
        <div class="v4-metric-label">{label}</div>
        <div class="v4-metric-value" style="color:{color};">{value}</div>
        {sub_html}
    </div>
    """


def _render_metrics_row(stats: dict) -> None:
    color = lift_color(stats["lift"])
    text_primary = plotly_colors()["text_primary"]
    cards = [
        _render_metric_card("Tasa de impago", f"{stats['rate'] * 100:.1f}%", color),
        _render_metric_card(
            "Índice vs base",
            f"{stats['lift']:.2f}×",
            color,
        ),
        _render_metric_card("Clientes", _fmt_num(stats["n"]), text_primary),
        _render_metric_card("% de la cartera", f"{stats['pct_cartera'] * 100:.1f}%", text_primary),
        _render_metric_card(
            "% de los impagos",
            f"{stats['pct_defaults'] * 100:.1f}%",
            text_primary,
            f"{_fmt_num(stats['defaults'])} impagos",
        ),
    ]
    render_html(f'<div class="v4-metrics-row">{"".join(cards)}</div>')


def _render_rate_bar(stats: dict) -> None:
    scale_max = 0.30
    fill_pct = min(100.0, (stats["rate"] / scale_max) * 100) if stats["n"] > 0 else 0
    base_pct = (BASE_RATE / scale_max) * 100
    color = lift_color(stats["lift"]) if stats["n"] > 0 else "#b0a898"

    render_html(
        f"""
        <div class="v4-rate-bar-wrap">
            <div class="v4-rate-bar-title">
                (8,07%)
                &nbsp;·&nbsp; <span style="color:{color};">{lift_label(stats['lift'])}</span>
            </div>
            <div class="v4-rate-track">
                <div class="v4-rate-fill" style="width:{fill_pct:.2f}%; background:{color};"></div>
                <div class="v4-rate-marker" style="left:{base_pct:.2f}%;" title="Tasa base"></div>
            </div>
            <div class="v4-rate-scale">
                <span>0%</span>
                <span>8,07% (base)</span>
                <span>15%</span>
                <span>22,5%</span>
                <span>30%</span>
            </div>
        </div>
        """
    )


def _render_lift_legend() -> None:
    items = [
        ("#c0281e", "≥1,50× riesgo muy alto"),
        ("#e8392e", "≥1,20× riesgo alto"),
        ("#e8832e", "≥1,05× riesgo moderado"),
        ("#b0a898", "±5% en línea con la base"),
        ("#2e9e8e", "0,80–0,95× riesgo bajo"),
        ("#1db89a", "<0,80× riesgo muy bajo"),
    ]
    spans = "".join(
        f'<span><i class="v4-lift-dot" style="background:{c};"></i>{t}</span>'
        for c, t in items
    )
    render_html(f'<div class="v4-lift-legend">{spans}</div>')


def _create_breakdown_chart(rows, dim: str) -> go.Figure:
    labels = [display_value(dim, v) for v in rows[dim].astype(str).tolist()]

    rates_pct = (rows["rate"] * 100).tolist()
    bar_colors = [lift_color(lift) for lift in rows["lift"]]
    opacities = [0.38 if low else 1.0 for low in rows["low_n"]]

    fig = go.Figure()
    theme = plotly_colors()
    fig.add_trace(
        go.Bar(
            y=labels,
            x=rates_pct,
            orientation="h",
            marker={"color": bar_colors, "opacity": opacities, "line": {"width": 0}},
            text=[f"{r:.1f}%" for r in rates_pct],
            textposition="outside",
            textfont={
                "family": "ui-monospace, Cascadia Code, monospace",
                "size": 11,
                "color": theme["bar_label"],
            },
            customdata=list(zip(rows["lift"], rows["n"], rows["defaults"])),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Tasa: %{x:.1f}%<br>"
                "Índice: %{customdata[0]:.2f}×<br>"
                "Clientes: %{customdata[1]:,.0f}<br>"
                "Impagos: %{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=BASE_RATE_PCT,
        line_dash="dash",
        line_color=theme["ref_line"],
        line_width=1.5,
        annotation_text=f"Base: {BASE_RATE_PCT:.2f}%",
        annotation_position="top",
        annotation_font_color=theme["annotation_text"],
        annotation_font_size=11,
        annotation_bgcolor=theme["annotation_bg"],
    )

    x_max = max(max(rates_pct) * 1.15, BASE_RATE_PCT * 1.4, 15) if rates_pct else 20

    fig.update_layout(
        height=max(320, 36 * len(labels) + 80),
        margin={"l": 8, "r": 48, "t": 28, "b": 8},
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font={"color": theme["font"], "family": "Inter, Arial, sans-serif", "size": 12},
        xaxis={
            "title": "Tasa de impago (%)",
            "gridcolor": theme["grid"],
            "griddash": "dot",
            "zeroline": False,
            "range": [0, x_max],
            "ticksuffix": "%",
        },
        yaxis={"categoryorder": "array", "categoryarray": labels[::-1], "showgrid": False},
        showlegend=False,
        bargap=0.22,
    )
    return fig


def _render_warnings(stats: dict, selection: dict) -> None:
    has_filters = any(selection.get(d) for d in DIMS)

    if not has_filters:
        st.info("Vista de la **cartera completa** (sin filtros activos). Tasa base fija: **8,07%**.")

    if stats["n"] == 0:
        st.error("La combinación de filtros no contiene clientes. Reduce los filtros.")
        return

    if stats["low_n"]:
        st.warning(
            f"Muestra baja (n={_fmt_num(stats['n'])}). El IC del 95% supera ±5 p.p. Interpreta con cautela."
        )

    for cat in selection.get("NAME_INCOME_TYPE") or []:
        if cat in SMALL_INCOME_TYPES:
            st.warning(
                f"**{cat}** tiene menos de 30 clientes en la cartera "
                f"(n≈{SMALL_INCOME_TYPES[cat]}). La tasa del segmento filtrado "
                f"(n={_fmt_num(stats['n'])}) no es estadísticamente representativa."
            )

    if ACADEMIC_DEGREE_ES in (selection.get("NAME_EDUCATION_TYPE") or []):
        st.warning(
            f"**{ACADEMIC_DEGREE_ES}** tiene solo ~164 clientes en la cartera (1,8% de impago). "
            "Interpreta con cautela."
        )


def render_vista_4() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df = load_and_bin()
    cube = build_cube(df)

    col_filtros, col_main = st.columns([1.05, 3.5], gap="medium")

    with col_filtros:
        with st.container(border=True):
            render_html(
                """
                <div class="filter-header">
                    <div class="panel-title" style="margin:0;">Perfil del solicitante</div>
                </div>
                """
            )
            if st.button("Limpiar filtros", use_container_width=True):
                for dim in DIMS:
                    st.session_state[f"v4_filter_{dim}"] = []
                st.rerun()

            selection = {}
            for dim in DIMS:
                opts = dim_options(cube, dim)
                display_opts = multiselect_display_options(dim, opts)
                chosen_display = st.multiselect(
                    DIM_LABELS[dim],
                    display_opts,
                    key=f"v4_filter_{dim}",
                    placeholder=MULTISELECT_PLACEHOLDER,
                )
                selection[dim] = selection_from_display(dim, chosen_display, opts)

    filtered = apply_filters(cube, selection)
    stats = segment_stats(filtered)

    with col_main:
        render_html(
            """
            <div class="panel-title" style="margin-bottom:4px;">Perfilador de riesgo</div>
            <div class="panel-subtitle" style="margin:0 0 10px 0;">
                ¿Qué combinación de atributos concentra impago distinto de la base?
            </div>
            """
        )

        _render_warnings(stats, selection)

        if stats["n"] > 0:
            _render_metrics_row(stats)
            _render_rate_bar(stats)

        with st.container(border=True):
            break_dim = st.selectbox(
                "Desglosar por",
                options=DIMS,
                format_func=lambda d: DIM_LABELS[d],
                index=DIMS.index("band_edad"),
                key="v4_breakdown_dim",
            )

            if stats["n"] == 0:
                st.warning("Sin datos para el gráfico con los filtros actuales.")
            else:
                bd = breakdown(cube, selection, break_dim)
                if bd.empty:
                    st.warning("No hay categorías con datos para este desglose.")
                else:
                    st.plotly_chart(
                        _create_breakdown_chart(bd, break_dim),
                        use_container_width=True,
                        config={"displayModeBar": False, "responsive": True},
                    )
                    _render_lift_legend()
