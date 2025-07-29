# FileGDB Viewer mit Streamlit

Dieses Projekt ist eine einfache Webanwendung mit Streamlit, um ESRI File Geodatabases (FileGDB) im Browser zu visualisieren.

## 🔧 Funktionen

- Upload einer `.gdb`-Datei als ZIP
- Anzeige der enthaltenen Layer
- Auswahl eines Layers zur Anzeige
- Interaktive Kartenvisualisierung mit Folium

## 📦 Voraussetzungen

- Python 3.8 oder höher
- GDAL mit FileGDB-Unterstützung

### GDAL mit FileGDB-Unterstützung installieren (empfohlen mit Conda):

```bash
conda create -n gdbviewer python=3.10
conda activate gdbviewer
conda install -c conda-forge gdal geopandas fiona folium streamlit streamlit-folium
