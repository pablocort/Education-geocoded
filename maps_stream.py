
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, FastMarkerCluster
from streamlit_folium import st_folium
import zipfile


#st.write(sys.executable)

st.write("""
# Indicadores de seguimiento a los retos transversales

Mapa de concetración de número de estudiantes por equipo de cómputo

""")

zip_file_path = 'data/sedes_geo.zip'
# Open the compressed file in binary read mode ('rb')
with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
    # Assuming the ZIP file contains a CSV file
    csv_file_name = zip_file.namelist()[0]  # Get the first file in the ZIP archive

    # Read the CSV file from the ZIP archive into a DataFrame
    with zip_file.open(csv_file_name) as file:
        sedes_tic = pd.read_csv(file, delimiter='|') 


def generateBaseMap(default_location=[4.631530, -74.109180], default_zoom_start=11):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    return base_map

basemap=generateBaseMap()


#from folium.plugins import FastMarkerCluster
FastMarkerCluster(data=sedes_tic[['LATITUD', 'LONGITUD','Estudiantes por computador']].values.tolist()).add_to(basemap)
import IPython
from IPython.core.display import display, HTML

def folium_deepnote_show(m):
    data = m.get_root().render()
    data_fixed_height = data.replace('width: 100%;height: 100%', 'width: 100%').replace('height: 100.0%;', 'height: 609px;', 1)
    display(HTML(data_fixed_height))

basemap

M = folium_deepnote_show(basemap)
st_folium(M)

