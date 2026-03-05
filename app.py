import streamlit as st
import pandas as pd
from parser_actividades import procesar_chat_instalaciones
from exportadores import generar_archivos

st.set_page_config(page_title="Parser Instalaciones Fibra", page_icon="📡", layout="wide")

st.title("📡 Parser de Actividades - Instalaciones Fibra Óptica")
st.markdown("Procesa reportes de WhatsApp de instalación, enrutamiento y relevamiento. Agrupa por cliente en sesiones con fecha inicio/fin.")

uploaded_file = st.file_uploader("📄 Sube tu archivo de chat de WhatsApp (.txt)", type=["txt"])

if uploaded_file:
    with st.spinner("🔄 Procesando chat..."):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        df_actividades, df_chat, stats = procesar_chat_instalaciones(temp_path)

    total_ses  = stats.get("total_sesiones", 0)
    total_rep  = stats.get("total_reportes", 0)
    st.success(f"✅ {total_ses} sesiones generadas a partir de {total_rep} reportes crudos")

    tab1, tab2 = st.tabs(["📋 Sesiones", "📊 Dashboard"])

    with tab1:
        st.subheader("📄 Sesiones por Cliente")
        st.caption("Cada fila = una visita/trabajo continuo. Si el mismo cliente aparece más de una vez = sede diferente (gap > 3 días).")
        st.dataframe(df_actividades, use_container_width=True, height=600)

    with tab2:
        st.subheader("📊 Dashboard de Actividades")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sesiones Totales", total_ses)
        with col2:
            st.metric("Completadas", stats.get("por_estado", {}).get("Completada", 0))
        with col3:
            st.metric("En Progreso", stats.get("por_estado", {}).get("En Progreso", 0))
        with col4:
            st.metric("Suspendidas", stats.get("por_estado", {}).get("Suspendida", 0))

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🏭 Top Clientes")
            top_cli = pd.DataFrame(list(stats.get("top_clientes", {}).items())[:10],
                                   columns=["Cliente", "Sesiones"])
            if not top_cli.empty:
                st.bar_chart(top_cli.set_index("Cliente"))

        with col_b:
            st.markdown("#### 👷 Top Técnicos")
            top_tec = pd.DataFrame(list(stats.get("top_tecnicos", {}).items())[:10],
                                   columns=["Técnico", "Sesiones"])
            if not top_tec.empty:
                st.bar_chart(top_tec.set_index("Técnico"))

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("#### 📋 Tipos de Actividad")
            tipos = pd.DataFrame(list(stats.get("por_tipo", {}).items()),
                                 columns=["Tipo", "Cantidad"])
            if not tipos.empty:
                st.bar_chart(tipos.set_index("Tipo"))

        with col_d:
            st.markdown("#### 🌆 Ciudades")
            ciudades = pd.DataFrame(list(stats.get("por_ciudad", {}).items()),
                                    columns=["Ciudad", "Cantidad"])
            if not ciudades.empty:
                st.bar_chart(ciudades.set_index("Ciudad"))

        # Tabla duraciones más largas
        if not df_actividades.empty and "DURACION_DIAS" in df_actividades.columns:
            st.markdown("#### ⏱️ Sesiones con Mayor Duración")
            df_dur = (df_actividades[df_actividades["DURACION_DIAS"] > 0]
                      .sort_values("DURACION_DIAS", ascending=False)
                      .head(10)[["CLIENTE", "CIUDAD", "FECHA_INICIO", "FECHA_FIN",
                                  "DURACION_DIAS", "TIPO_ACTIVIDAD", "ESTADO"]])
            if not df_dur.empty:
                st.dataframe(df_dur, use_container_width=True)
            else:
                st.info("Todas las sesiones se completaron en el mismo día.")

    # Generar archivos
    with st.spinner("📦 Generando archivos..."):
        excel_path = "Actividades_Instalaciones.xlsx"
        json_path  = "Actividades_Instalaciones.json"
        csv_path   = "Actividades_Instalaciones.csv"
        generar_archivos(df_actividades, df_chat, stats, excel_path, json_path, csv_path)

    st.success("✅ Archivos listos para descargar")
    col1, col2, col3 = st.columns(3)
    with col1:
        with open(excel_path, "rb") as f:
            st.download_button("📄 Descargar Excel", f,
                file_name="Actividades_Instalaciones.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        with open(json_path, "rb") as f:
            st.download_button("📄 Descargar JSON", f,
                file_name="Actividades_Instalaciones.json", mime="application/json")
    with col3:
        with open(csv_path, "rb") as f:
            st.download_button("📄 Descargar CSV", f,
                file_name="Actividades_Instalaciones.csv", mime="text/csv")

else:
    st.info("⬆️ Sube un archivo de chat de WhatsApp para comenzar")
    st.markdown("""
    ---
    ### 🔍 Formato esperado del chat:
    ```
    CIUDAD: Bucaramanga
    ING CARGO: Javier Gutierrez
    CLIENTE: fiber group vitelsa
    DIRECCIÓN: parque industrial
    TIPO DE ACTIVIDA: instalación
    AVANCE: se inicia actividad
    ```
    """)
