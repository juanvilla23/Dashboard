"""Vista 1: Riesgo y volumen por segmento."""

import streamlit as st

from ui.render import render_html
from views.segmentacion import (
    DATA_PATH,
    DIMENSIONES,
    METRICAS,
    agrupar_por_dimension,
    aplicar_filtro_historial,
    calcular_tasa_general_default,
    cargar_datos,
    crear_grafica_barras,
    obtener_configuracion_metrica,
)


def render_vista_1() -> None:
    if not DATA_PATH.exists():
        st.error(f"No se encontró el archivo de datos: {DATA_PATH.name}")
        return

    df_base = cargar_datos()
    col_filtros, col_grafica = st.columns([1.05, 3.5], gap="medium")

    with col_filtros:
        with st.container(border=True):
            render_html('<div class="panel-title">Filtros</div>')

            dimension = st.selectbox("Segmento", list(DIMENSIONES.keys()), index=0)
            metrica = st.selectbox("Producto", METRICAS, index=0)
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

        df_filtrado = aplicar_filtro_historial(df_base, historial_bureau)
        tasa_general = calcular_tasa_general_default(df_filtrado)

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

            if df_visible.empty:
                st.warning("No hay segmentos con suficientes clientes para mostrar la gráfica.")
            else:
                grafica = crear_grafica_barras(
                    df_visible,
                    configuracion,
                    tasa_general=tasa_general,
                    dimension=dimension,
                )
                st.plotly_chart(
                    grafica,
                    use_container_width=True,
                    config={"displayModeBar": False, "responsive": True},
                )

        if not segmentos_ocultos.empty:
            st.warning(
                f"Se ocultaron {len(segmentos_ocultos)} segmentos "
                f"porque tienen menos de {minimo_clientes} clientes."
            )
