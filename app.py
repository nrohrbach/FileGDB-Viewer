import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import os
import tempfile
import fiona

def find_all_gdb_folders(root_dir):
    gdb_folders = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            if dirname.lower().endswith('.gdb'):
                gdb_folders.append(os.path.join(dirpath, dirname))
    return gdb_folders

st.set_page_config(layout="wide")
st.title("🗺️ FileGDB Viewer mit Streamlit")

uploaded_file = st.file_uploader("Lade eine .gdb-Datei als ZIP hoch", type="zip")

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

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
                
                            # Transformation nach WGS84
                            if gdf.crs and gdf.crs.to_epsg() != 4326:
                                gdf = gdf.to_crs(epsg=4326)
                
                            st.write(gdf.head())
                            st.markdown(f"**CRS (transformiert):** {gdf.crs}")
                            st.markdown(f"**Anzahl Features:** {len(gdf)}")
                
                            if not gdf.empty and gdf.geometry.notnull().any():
                                centroid = gdf.geometry.centroid.dropna()
                                m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=10)
                                folium.GeoJson(gdf).add_to(m)
                                st_folium(m, width=1000, height=600)
                            else:
                                st.warning("Keine gültige Geometrie zum Anzeigen gefunden.")



