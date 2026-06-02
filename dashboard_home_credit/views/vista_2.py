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
    calcular_tasa_general_default,
    cargar_datos,
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
                <div class="panel-subtitle" style="margin:0 0 6px 0;">
                    Gráfica de barras
                </div>
                <div class="v2-section-hint">
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

        render_html('<div class="v2-controls-spacer"></div>')
        render_html('<div class="v2-section-separator">Matriz</div>')

        with st.container(border=True):
            render_html(
                """
                <div class="panel-title" style="margin-bottom:4px;">
                    Matriz rechazo × solicitudes
                </div>
                <div class="panel-subtitle" style="margin:0 0 6px 0;">
                    Tabla de calor
                </div>
                <div class="v2-section-hint">
                    Rechazo previo × nº de solicitudes (y dimensión opcional)
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
