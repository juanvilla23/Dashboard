"""Tema claro / oscuro: .theme-light en #dashboard-root (.stApp), localStorage y Plotly."""

from __future__ import annotations

import json

import streamlit as st

import streamlit.components.v1 as components

from ui.render import render_html
from ui.styles import build_global_stylesheet, get_css_content

STORAGE_KEY = "dashboard-theme"
THEMES = ("dark", "light")

PLOTLY_THEME_COLORS = {
    "dark": {
        "font": "#9aa3af",
        "text_primary": "#e8eaed",
        "bar_label": "#c6ced8",
        "grid": "rgba(255, 255, 255, 0.08)",
        "line": "rgba(255, 255, 255, 0.12)",
        "ref_line": "#ffffff",
        "annotation_text": "#e0e0e0",
        "annotation_bg": "rgba(26, 26, 26, 0.85)",
        "paper": "rgba(0,0,0,0)",
        "plot": "rgba(0,0,0,0)",
    },
    "light": {
        "font": "#2C2C2A",
        "text_primary": "#2C2C2A",
        "bar_label": "#2C2C2A",
        "grid": "rgba(0, 0, 0, 0.08)",
        "line": "rgba(0, 0, 0, 0.12)",
        "ref_line": "#2C2C2A",
        "annotation_text": "#2C2C2A",
        "annotation_bg": "rgba(255, 255, 255, 0.94)",
        "paper": "rgba(0,0,0,0)",
        "plot": "rgba(0,0,0,0)",
    },
}


def get_theme() -> str:
    """Lee el tema activo desde session_state o query_params como fallback."""
    theme = str(st.session_state.get("_dashboard_theme", "dark"))
    # También intentar desde query_params por si el usuario recargó la página
    if theme == "dark":
        qp = st.query_params.get("theme", "")
        if qp == "light":
            theme = "light"
            st.session_state["_dashboard_theme"] = "light"
    return theme if theme in THEMES else "dark"


def view_href(view_id: str) -> str:
    return f"?view={view_id}"


def render_global_styles() -> None:
    """CSS vía st.html (no markdown) + copia al <head> del documento principal."""
    render_html(build_global_stylesheet())

    css_json = json.dumps(get_css_content())
    components.html(
        f"""
        <script>
        (function () {{
            const doc = window.parent.document;
            if (doc.getElementById("dashboard-global-styles")) return;
            const style = doc.createElement("style");
            style.id = "dashboard-global-styles";
            style.textContent = {css_json};
            doc.head.appendChild(style);
        }})();
        </script>
        """,
        height=0,
    )


def render_theme_runtime() -> None:
    """Toggle sol/luna, localStorage, clase .theme-light y actualización de Plotly."""
    plotly_json = json.dumps(PLOTLY_THEME_COLORS)
    components.html(
        f"""
        <script>
        (function () {{
            const STORAGE_KEY = "{STORAGE_KEY}";
            const PLOTLY_PALETTES = {plotly_json};

            function parentDoc() {{
                return window.parent.document;
            }}

            function dashboardRoot() {{
                const doc = parentDoc();
                const app = doc.querySelector(".stApp");
                if (!app) return null;
                app.id = "dashboard-root";
                return app;
            }}

            function readTheme() {{
                const stored = localStorage.getItem(STORAGE_KEY);
                return stored === "light" ? "light" : "dark";
            }}

            function writeTheme(theme) {{
                localStorage.setItem(STORAGE_KEY, theme);
            }}

            function applyThemeClass(theme) {{
                const root = dashboardRoot();
                if (!root) return;
                if (theme === "light") {{
                    root.classList.add("theme-light");
                }} else {{
                    root.classList.remove("theme-light");
                }}
                /* Forzar color de fondo directamente para el caso de OS en dark-mode */
                const bg = theme === "light" ? "#F1EFE8" : "#0d0d0d";
                const fg = theme === "light" ? "#2C2C2A" : "#ffffff";
                root.style.setProperty("background-color", bg, "important");
                root.style.setProperty("color", fg, "important");
                /* Aplicar también al contenedor principal de Streamlit */
                const doc = parentDoc();
                const appView = doc.querySelector("[data-testid='stAppViewContainer']");
                if (appView) {{
                    appView.style.setProperty("background-color", bg, "important");
                }}
                const main = doc.querySelector("[data-testid='stMain']") || doc.querySelector(".main");
                if (main) {{
                    main.style.setProperty("background-color", bg, "important");
                    main.style.setProperty("color", fg, "important");
                }}
            }}

            function axisFontPatches(layout, p, patch) {{
                if (!layout) return;
                Object.keys(layout).forEach((key) => {{
                    if (!/^xaxis|yaxis/.test(key)) return;
                    patch[`${{key}}.tickfont.color`] = p.font;
                    patch[`${{key}}.title.font.color`] = p.font;
                    patch[`${{key}}.gridcolor`] = p.grid;
                    patch[`${{key}}.linecolor`] = p.line;
                }});
            }}

            function plotlyRelayout(theme) {{
                const doc = parentDoc();
                const Plotly = window.parent.Plotly || window.Plotly;
                if (!Plotly) return;
                const p = PLOTLY_PALETTES[theme] || PLOTLY_PALETTES.dark;
                const labelColor = p.text_primary || p.font;
                doc.querySelectorAll(".js-plotly-plot").forEach((plot) => {{
                    try {{
                        const layoutPatch = {{
                            paper_bgcolor: p.paper,
                            plot_bgcolor: p.plot,
                            "font.color": p.font,
                            "legend.font.color": labelColor,
                            "xaxis.gridcolor": p.grid,
                            "yaxis.gridcolor": p.grid,
                            "xaxis.linecolor": p.line,
                            "yaxis.linecolor": p.line,
                            "xaxis.tickfont.color": p.font,
                            "yaxis.tickfont.color": p.font,
                            "xaxis.title.font.color": p.font,
                            "yaxis.title.font.color": p.font,
                        }};
                        axisFontPatches(plot.layout, p, layoutPatch);
                        const shapes = (plot.layout && plot.layout.shapes) || [];
                        shapes.forEach((shape, i) => {{
                            if (shape.type === "line" && shape.line) {{
                                layoutPatch[`shapes[${{i}}].line.color`] = p.ref_line;
                            }}
                        }});
                        const annotations = (plot.layout && plot.layout.annotations) || [];
                        annotations.forEach((ann, i) => {{
                            layoutPatch[`annotations[${{i}}].font.color`] = p.annotation_text;
                            layoutPatch[`annotations[${{i}}].bgcolor`] = p.annotation_bg;
                        }});
                        Plotly.relayout(plot, layoutPatch);

                        const data = plot.data || [];
                        const textTraceIdx = [];
                        const barTextIdx = [];
                        data.forEach((trace, i) => {{
                            if (trace.text) textTraceIdx.push(i);
                            if (trace.textposition === "outside") barTextIdx.push(i);
                        }});
                        if (textTraceIdx.length) {{
                            Plotly.restyle(plot, {{ "textfont.color": labelColor }}, textTraceIdx);
                        }}
                        if (barTextIdx.length) {{
                            Plotly.restyle(
                                plot,
                                {{ "textfont.color": p.bar_label || labelColor }},
                                barTextIdx
                            );
                        }}
                    }} catch (e) {{}}
                }});
            }}

            function refreshCharts(theme) {{
                plotlyRelayout(theme);
                setTimeout(() => plotlyRelayout(theme), 400);
                setTimeout(() => plotlyRelayout(theme), 1200);
            }}

            function updateToggleIcon(theme) {{
                const btn = parentDoc().getElementById("dashboard-theme-toggle");
                if (!btn) return;
                btn.textContent = theme === "light" ? "\\u263E" : "\\u2600";
                btn.title = theme === "light"
                    ? "Cambiar a tema oscuro"
                    : "Cambiar a tema claro";
                btn.setAttribute("aria-label", btn.title);
            }}

            function setTheme(theme, persist) {{
                const next = theme === "light" ? "light" : "dark";
                if (persist) writeTheme(next);
                applyThemeClass(next);
                refreshCharts(next);
                updateToggleIcon(next);
            }}

            function ensureToggleButton() {{
                const doc = parentDoc();
                if (doc.getElementById("dashboard-theme-toggle")) return;

                const btn = doc.createElement("button");
                btn.id = "dashboard-theme-toggle";
                btn.type = "button";
                btn.addEventListener("click", () => {{
                    const current = readTheme();
                    const next = current === "light" ? "dark" : "light";
                    setTheme(next, true);
                    /* Sincronizar con URL para que Python get_theme() lo lea */
                    try {{
                        const url = new URL(window.parent.location.href);
                        if (next === "light") {{
                            url.searchParams.set("theme", "light");
                        }} else {{
                            url.searchParams.delete("theme");
                        }}
                        window.parent.history.replaceState({{}}, "", url.toString());
                    }} catch(e) {{}}
                }});
                doc.body.appendChild(btn);
            }}

            function observePlots() {{
                const doc = parentDoc();
                let timer = null;
                const observer = new MutationObserver(() => {{
                    clearTimeout(timer);
                    timer = setTimeout(() => refreshCharts(readTheme()), 200);
                }});
                const root = doc.querySelector(".stApp");
                if (root) {{
                    observer.observe(root, {{ childList: true, subtree: true }});
                }}
            }}

            function init() {{
                ensureToggleButton();
                const theme = readTheme();
                applyThemeClass(theme);
                updateToggleIcon(theme);
                refreshCharts(theme);
                observePlots();
            }}

            const doc = parentDoc();
            if (doc.readyState === "loading") {{
                doc.addEventListener("DOMContentLoaded", init);
            }} else {{
                init();
            }}
            setTimeout(init, 100);
            setTimeout(init, 600);
        }})();
        </script>
        """,
        height=0,
    )


def plotly_colors() -> dict[str, str]:
    base = PLOTLY_THEME_COLORS.get(get_theme(), PLOTLY_THEME_COLORS["dark"]).copy()
    if get_theme() == "light":
        return {
            **base,
            "muted_line": "rgba(0, 0, 0, 0.18)",
            "text_primary": "#2C2C2A",
            "bar_label": "#5F5E5A",
            "reject_zone": "rgba(0, 0, 0, 0.05)",
            "info": "#185FA5",
            "success": "#3B6D11",
            "warning": "#BA7517",
            "accent": "#E24B4A",
        }
    return {
        **base,
        "muted_line": "rgba(255, 255, 255, 0.2)",
        "text_primary": "#ffffff",
        "bar_label": "#c6ced8",
        "reject_zone": "rgba(180, 180, 180, 0.12)",
        "info": "#42a5f5",
        "success": "#4caf50",
        "warning": "#ff9800",
        "accent": "#e53935",
    }


def color_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
