"""Vista 2: Comportamiento crediticio previo — curva de riesgo y matriz rechazo × solicitudes."""

import streamlit as st

from ui.render import render_html
from views.conducta import (
    BASE_RATE_PCT,
    BANDAS_SCORE_MATRIZ,
    GRUPOS_BURO_MATRIZ,
    TERCERAS_DIMENSIONES,
    VARIABLES_CONDUCTA,
    agrupar_curva_riesgo,
    agrupar_matriz,
    crear_grafica_curva,
    crear_matrices_html,
    estilos_matriz_html,
    opciones_filtro_tercera,
)
from views.segmentacion import (
    DATA_PATH,
    aplicar_filtro_historial,
    calcular_kpis,
    calcular_tasa_general_default,
    cargar_datos,
    render_kpi_card,
)


def render_vista_2() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df_base = cargar_datos()
    col_controles, col_grafica = st.columns([1.15, 3.4], gap="medium")

    with col_controles:
        with st.container(border=True):
            render_html(
                """
                <div class="panel-title" style="margin-bottom:4px;">
                    Comportamiento crediticio previo
                </div>
                <div class="panel-subtitle" style="margin:0 0 12px 0;">
                    Curva de riesgo por variable de conducta
                </div>
                """
            )

            variable = st.selectbox(
                "Variable de conducta",
                list(VARIABLES_CONDUCTA.keys()),
                index=2,
                key="v2_variable",
            )

            st.caption(VARIABLES_CONDUCTA[variable]["descripcion"])

            historial_bureau = st.selectbox(
                "Filtrar por buró",
                ["Todos los clientes", "Con historial", "Sin historial"],
                index=0,
                key="v2_historial",
            )

            minimo_clientes = st.number_input(
                "Mínimo clientes por banda",
                min_value=10,
                max_value=5000,
                value=100,
                step=50,
                key="minimo_clientes_v2",
            )

        with st.container(border=True):
            render_html(
                """
                <div class="panel-title" style="margin-bottom:8px;">
                    Matriz rechazo × solicitudes
                </div>
                """
            )

            tercera_dim_label = st.selectbox(
                "Tercera dimensión (matriz)",
                list(TERCERAS_DIMENSIONES.keys()),
                index=0,
                key="v2_tercera_dim",
            )
            tercera_dim = TERCERAS_DIMENSIONES[tercera_dim_label]

            minimo_celda = st.number_input(
                "Mínimo clientes por celda",
                min_value=5,
                max_value=500,
                value=30,
                step=5,
                key="v2_min_celda",
            )

        df_filtrado = aplicar_filtro_historial(df_base, historial_bureau)
        tasa_general = calcular_tasa_general_default(df_filtrado)
        kpis = calcular_kpis(df_filtrado)

        with st.container(border=True):
            render_html('<div class="panel-title">Resumen global</div>')
            render_kpi_card("$", "Solicitudes", kpis["solicitudes"], "—")
            render_kpi_card("↗", "Tasa de impago", kpis["tasa_default"], "—")
            render_kpi_card("◎", "Impagos", kpis["clientes_default"], "—")

    with col_grafica:
        df_curva = agrupar_curva_riesgo(df_filtrado, variable)
        df_curva_visible = df_curva[df_curva["total_clientes"] >= minimo_clientes].copy()

        with st.container(border=True):
            render_html(
                f"""
                <div class="panel-title" style="margin-bottom:4px;">
                    Curva de riesgo — {variable}
                </div>
                <div class="panel-subtitle" style="margin:0 0 8px 0;">
                    Tasa de impago por banda de la variable seleccionada
                </div>
                """
            )

            if df_curva_visible.empty:
                st.warning("No hay bandas con suficientes clientes.")
            else:
                max_banda = df_curva_visible.loc[df_curva_visible["tasa_default_pct"].idxmax()]
                st.metric(
                    "Banda de mayor riesgo",
                    str(max_banda["segmento"]),
                    f"{max_banda['tasa_default_pct']:.1f}%",
                )
                st.plotly_chart(
                    crear_grafica_curva(df_curva_visible, variable, tasa_general=tasa_general),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        with st.container(border=True):
            render_html(estilos_matriz_html())
            render_html(
                f"""
                <div class="panel-title" style="margin-bottom:4px;">
                    Matriz: rechazo previo × solicitudes previas
                </div>
                <div class="panel-subtitle" style="margin:0 0 12px 0;">
                    Cada celda: tasa de impago, índice vs base ({BASE_RATE_PCT:.2f}%) y volumen (k)
                </div>
                """
            )

            if tercera_dim is None:
                matriz = agrupar_matriz(df_filtrado, None, minimo_celda=minimo_celda)
                render_html(
                    crear_matrices_html([(matriz, "Cartera filtrada")], minimo_celda)
                )
            elif tercera_dim == "buro":
                paneles = [
                    (
                        agrupar_matriz(
                            df_filtrado,
                            tercera_dim,
                            filtro_tercera=opcion,
                            minimo_celda=minimo_celda,
                        ),
                        opcion,
                    )
                    for opcion in GRUPOS_BURO_MATRIZ
                ]
                render_html(crear_matrices_html(paneles, minimo_celda))
            else:
                paneles = [
                    (
                        agrupar_matriz(
                            df_filtrado,
                            tercera_dim,
                            filtro_tercera=banda,
                            minimo_celda=minimo_celda,
                        ),
                        banda,
                    )
                    for banda in BANDAS_SCORE_MATRIZ
                ]
                render_html(crear_matrices_html(paneles, minimo_celda))

            render_html(
                """
                <div class="chart-footer" style="margin-top:14px;">
                    ⓘ &nbsp; Filas: <strong>tasa de rechazo previa</strong> (0% → 75-100%).
                    Columnas: <strong>nº de solicitudes previas</strong> (1-2, 3-5, 6+).
                    El color del índice usa la misma escala que el perfilador (base 8,07%).
                    Celdas con «—» tienen menos clientes que el mínimo configurado.
                </div>
                """
            )

        with st.expander("Tabla — curva de riesgo por banda"):
            tabla_curva = df_curva.copy()
            tabla_curva["tasa_default_pct"] = tabla_curva["tasa_default_pct"].round(2)
            st.dataframe(
                tabla_curva.rename(
                    columns={
                        "segmento": "Banda",
                        "total_clientes": "Clientes",
                        "clientes_default": "Impagos",
                        "tasa_default_pct": "Tasa (%)",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        with st.expander("Tabla — matriz rechazo × solicitudes"):
            filtro_tabla = None
            if tercera_dim == "buro":
                filtro_tabla = st.selectbox(
                    "Corte para tabla",
                    GRUPOS_BURO_MATRIZ,
                    key="v2_tabla_buro",
                )
            elif tercera_dim == "score":
                filtro_tabla = st.selectbox(
                    "Corte para tabla",
                    opciones_filtro_tercera(df_filtrado, tercera_dim),
                    key="v2_tabla_score",
                )

            matriz_tabla = agrupar_matriz(
                df_filtrado,
                tercera_dim,
                filtro_tercera=filtro_tabla,
                minimo_celda=minimo_celda,
            )
            st.dataframe(matriz_tabla, use_container_width=True, hide_index=True)
