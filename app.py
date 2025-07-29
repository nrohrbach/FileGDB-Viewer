import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import zipfile
import os
import tempfile
import fiona
import requests

# Funktion zum Finden von .gdb-Ordnern
def find_all_gdb_folders(root_dir):
    return [
        os.path.join(dirpath, dirname)
        for dirpath, dirnames, _ in os.walk(root_dir)
        for dirname in dirnames
        if dirname.lower().endswith('.gdb')
    ]

# Caching-Funktion für das Laden und Transformieren eines Layers
@st.cache_data(show_spinner="Lade Layer...")
def load_layer(gdb_path, layer_name):
    df = gpd.read_file(gdb_path, layer=layer_name)
    if isinstance(df, gpd.GeoDataFrame) and df.crs and df.crs.to_epsg() != 4326:
        df = df.to_crs(epsg=4326)
    return df

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🗺️ FileGDB Viewer mit Streamlit")

st.markdown("### Datenquelle wählen")
upload_option = st.radio("Wähle die Quelle der .gdb-Daten:", ["Datei-Upload", "URL"])

zip_data = None

if upload_option == "Datei-Upload":
    uploaded_file = st.file_uploader("Lade eine .gdb-Datei als ZIP hoch", type="zip")
    if uploaded_file:
        zip_data = uploaded_file.read()

elif upload_option == "URL":
    url = st.text_input("Gib die URL zu einer ZIP-Datei mit .gdb-Daten ein")
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            zip_data = response.content
            st.success("ZIP-Datei erfolgreich von der URL geladen.")
        except Exception as e:
            st.error(f"Fehler beim Herunterladen der Datei: {e}")

if zip_data:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "data.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_data)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        gdb_folders = find_all_gdb_folders(tmpdir)

        if gdb_folders:
            selected_gdb = st.selectbox("Wähle einen .gdb-Ordner", gdb_folders)

            try:
                layers = fiona.listlayers(selected_gdb)
                st.success(f"{len(layers)} Layer gefunden.")
                tabs = st.tabs(layers)

                for i, layer in enumerate(layers):
                    with tabs[i]:
                        st.subheader(f"📄 Layer: {layer}")
                        try:
                            df = load_layer(selected_gdb, layer)

                            st.write(df.head())
                            st.markdown(f"**Anzahl Zeilen:** {len(df)}")

                            if isinstance(df, gpd.GeoDataFrame) and df.geometry.notnull().any():
                                st.markdown(f"**CRS (transformiert):** {df.crs}")
                                centroid = df.geometry.centroid.dropna()
                                m = folium.Map(
                                    location=[centroid.y.mean(), centroid.x.mean()],
                                    zoom_start=10
                                )
                                geojson_data = df[['geometry']].to_json()
                                folium.GeoJson(geojson_data, name=layer).add_to(m)
                                st_folium(m, width=1000, height=600)
                            else:
                                st.info("Dieser Layer enthält keine Geometrie – es handelt sich um eine Tabelle.")
                        except Exception as e:
                            st.error(f"Fehler beim Laden des Layers '{layer}': {e}")
            except Exception as e:
                st.error(f"Fehler beim Zugriff auf die GDB: {e}")
        else:
            st.warning("Keine .gdb-Ordner in der ZIP-Datei gefunden.")
