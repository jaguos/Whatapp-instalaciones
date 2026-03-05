import streamlit as st
import pandas as pd
from parser_actividades import procesar_chat_instalaciones
from exportadores import generar_archivos
import io

st.set_page_config(page_title="Parser Instalaciones Fibra", page_icon="📡", layout="wide")

st.title("📡 Parser de Actividades - Instalaciones Fibra Óptica")
st.markdown("""Procesa reportes de WhatsApp de instalación, enrutamiento y relevamiento de fibra óptica.
Genera dashboard interactivo, Excel formateado, JSON y CSV.""")

uploaded_file = st.file_uploader("📄 Sube tu archivo de chat de WhatsApp (.txt)", type=["txt"])

if uploaded_file:
    with st.spinner("🔄 Procesando chat..."):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        df_actividades, df_chat, stats = procesar_chat_instalaciones(temp_path)
    
    st.success(f"✅ Procesadas {stats['total_actividades']} actividades")
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 Actividades", "📊 Dashboard"])
    
    with tab1:
        st.subheader("📄 Todas las Actividades")
        st.dataframe(df_actividades, use_container_width=True, height=600)
    
    with tab2:
        st.subheader("📊 Dashboard de Actividades")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Actividades", stats['total_actividades'])
        with col2:
            st.metric("Completadas", stats['por_estado'].get('Completada', 0))
        with col3:
            st.metric("En Progreso", stats['por_estado'].get('En Progreso', 0))
        with col4:
            st.metric("Suspendidas", stats['por_estado'].get('Suspendida', 0))
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 🏭 Top Clientes")
            top_cli = pd.DataFrame(list(stats['top_clientes'].items())[:10], columns=['Cliente', 'Actividades'])
            st.bar_chart(top_cli.set_index('Cliente'))
        
        with col_b:
            st.markdown("#### 👷 Top Técnicos")
            top_tec = pd.DataFrame(list(stats['top_tecnicos'].items())[:10], columns=['Técnico', 'Actividades'])
            st.bar_chart(top_tec.set_index('Técnico'))
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            st.markdown("#### 📋 Tipos de Actividad")
            tipos = pd.DataFrame(list(stats['por_tipo'].items()), columns=['Tipo', 'Cantidad'])
            st.bar_chart(tipos.set_index('Tipo'))
        
        with col_d:
            st.markdown("#### 🌆 Ciudades")
            ciudades = pd.DataFrame(list(stats['por_ciudad'].items()), columns=['Ciudad', 'Cantidad'])
            st.bar_chart(ciudades.set_index('Ciudad'))
    
    # Generar archivos
    with st.spinner("📦 Generando archivos de descarga..."):
        excel_path = "Actividades_Instalaciones.xlsx"
        json_path = "Actividades_Instalaciones.json"
        csv_path = "Actividades_Instalaciones.csv"
        
        generar_archivos(df_actividades, df_chat, stats, excel_path, json_path, csv_path)
    
    st.success("✅ Archivos listos para descargar")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with open(excel_path, "rb") as f:
            st.download_button("📄 Descargar Excel", f, file_name="Actividades_Instalaciones.xlsx",
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        with open(json_path, "rb") as f:
            st.download_button("📄 Descargar JSON", f, file_name="Actividades_Instalaciones.json",
                             mime="application/json")
    with col3:
        with open(csv_path, "rb") as f:
            st.download_button("📄 Descargar CSV", f, file_name="Actividades_Instalaciones.csv",
                             mime="text/csv")

else:
    st.info("⬆️ Sube un archivo de chat de WhatsApp para comenzar")
    st.markdown("""---
    ### 🔍 Formato esperado:
    ```
    CIUDAD: Bucaramanga
    ING CARGO: Javier Gutierrez
    CLIENTE: fiber group vitelsa
    DIRECCIÓN: parque industrial
    TIPO DE ACTIVIDA: instalación
    AVANCE: se inicia actividad
    ```
    """)
