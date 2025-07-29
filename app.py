import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import os
import tempfile
import fiona
import requests

def find_all_gdb_folders(root_dir):
    return [
        os.path.join(dirpath, dirname)
        for dirpath, dirnames, _ in os.walk(root_dir)
        for dirname in dirnames
        if dirname.lower().endswith('.gdb')
    ]

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
                            gdf = gpd.read_file(selected_gdb, layer=layer)

                            if gdf.crs and gdf.crs.to_epsg() != 4326:
                                gdf = gdf.to_crs(epsg=4326)

                            st.write(gdf.head())
                            st.markdown(f"**CRS (transformiert):** {gdf.crs}")
                            st.markdown(f"**Anzahl Features:** {len(gdf)}")

                            if not gdf.empty and gdf.geometry.notnull().any():
                                centroid = gdf.geometry.centroid.dropna()
                                m = folium.Map(
                                    location=[centroid.y.mean(), centroid.x.mean()],
                                    zoom_start=10
                                )
                                folium.GeoJson(gdf).add_to(m)
                                st_folium(m, width=1000, height=600)
                            else:
                                st.warning("Keine gültige Geometrie zum Anzeigen gefunden.")
                        except Exception as e:
                            st.error(f"Fehler beim Laden des Layers '{layer}': {e}")
            except Exception as e:
                st.error(f"Fehler beim Zugriff auf die GDB: {e}")
        else:
            st.warning("Keine .gdb-Ordner in der ZIP-Datei gefunden.")
