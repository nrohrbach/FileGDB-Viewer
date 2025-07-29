import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import os
import tempfile

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

        gdb_folders = find_all_gdb_folders(tmpdir
