import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import os
import tempfile
import fiona

st.set_page_config(layout="wide")
st.title("🗺️ FileGDB Viewer mit Streamlit")

uploaded_file = st.file_uploader("Lade eine .gdb-Datei als ZIP hoch", type="zip")

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir, "data.gdb"))

        gdb_path = os.path.join(tmpdir, "data.gdb")
        try:
            layers = fiona.listlayers(gdb_path)
            selected_layer = st.selectbox("Wähle einen Layer", layers)

            gdf = gpd.read_file(gdb_path, layer=selected_layer)
            st.write("📄 Vorschau der Daten:", gdf.head())

            if not gdf.empty and gdf.geometry.notnull().any():
                centroid = gdf.geometry.centroid
                m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=10)
                folium.GeoJson(gdf).add_to(m)
                st_data = st_folium(m, width=1000, height=600)
            else:
                st.warning("Keine gültige Geometrie zum Anzeigen gefunden.")
        except Exception as e:
            st.error(f"Fehler beim Verarbeiten der GDB-Datei: {e}")
