import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Configuración inicial
st.set_page_config(page_title="Dashboard de Seguridad Bogotá", layout="wide")

# Conexión a la base de datos
DB_URL = "postgresql://neondb_owner:dVO76wDFuhWM@ep-bitter-pond-a5neo6us.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DB_URL)

st.title("📊 Dashboard de Seguridad Ciudadana - Bogotá")
st.markdown("Visualización interactiva de incidentes, delitos, multas y estaciones de policía por localidad.")

# Selector de localidad
localidades = pd.read_sql("SELECT DISTINCT nombre_de_localidad, localidad FROM bogota.localidades_informacion ORDER BY nombre_de_localidad", engine)
localidad_nombre = st.sidebar.selectbox("Selecciona una localidad:", localidades["nombre_de_localidad"])
localidad_id = localidades.query("nombre_de_localidad == @localidad_nombre")["localidad"].iloc[0]

st.sidebar.write(f"📍 Localidad seleccionada: **{localidad_nombre}**")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["🚓 Delitos", "📞 Llamadas 123", "💸 Multas", "🏢 Estaciones y CAIs"])

# --- TAB 1: DELITOS ---
with tab1:
    delitos = pd.read_sql(f"SELECT ano, modalidad, total FROM bogota.delitos_alto_impacto WHERE localidad = {localidad_id}", engine)
    if delitos.empty:
        st.warning("No hay datos de delitos para esta localidad.")
    else:
        fig = px.bar(delitos, x="ano", y="total", color="modalidad", title=f"Delitos de Alto Impacto en {localidad_nombre}")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LLAMADAS ---
with tab2:
    llamadas = pd.read_sql(f"SELECT ano, tipo_de_llamada, total FROM bogota.incidentes_llamadas_reportadas WHERE localidad = {localidad_id}", engine)
    if llamadas.empty:
        st.warning("No hay datos de llamadas reportadas.")
    else:
        fig2 = px.line(llamadas, x="ano", y="total", color="tipo_de_llamada", title=f"Llamadas Reportadas (Línea 123) - {localidad_nombre}")
        st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3: MULTAS ---
with tab3:
    multas = pd.read_sql(f"SELECT nombre_upz, descripcion_comparendo FROM bogota.multas WHERE localidad = {localidad_id}", engine)
    if multas.empty:
        st.warning("No hay datos de multas para esta localidad.")
    else:
        top_multas = multas["descripcion_comparendo"].value_counts().head(10)
        fig3 = px.bar(top_multas, x=top_multas.values, y=top_multas.index, orientation='h', title="Top 10 Infracciones Más Comunes")
        st.plotly_chart(fig3, use_container_width=True)

# --- TAB 4: ESTACIONES Y CAIs ---
with tab4:
    estaciones = pd.read_sql(f"SELECT estacion_de_policia, latitud, longitud FROM bogota.estaciones_de_policia WHERE localidad = {localidad_id}", engine)
    cais = pd.read_sql(f"SELECT nombre_del_cai, direccion FROM bogota.cais WHERE localidad = {localidad_id}", engine)

    if not estaciones.empty:
        st.map(estaciones.rename(columns={'latitud':'lat', 'longitud':'lon'}))
        st.dataframe(estaciones)
    else:
        st.warning("No hay estaciones registradas en esta localidad.")

    st.subheader("CAIs registrados")
    st.dataframe(cais)

