import pandas as pd
import streamlit as st
print("Before import subprocess")
import subprocess
print("After import subprocess")
subprocess.run(["pip", "install", "geopandas"])
import geopandas as gpd
import folium
from folium.plugins import HeatMap




### import dataframes of interest
sedes_tic = pd.read_csv(r'data\sedes_geo.csv', sep ='|')


def generateBaseMap(default_location=[4.631530, -74.109180], default_zoom_start=11):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    return base_map
basemap=generateBaseMap()

from folium.plugins import FastMarkerCluster
FastMarkerCluster(data=sedes_tic[['LATITUD', 'LONGITUD','Estudiantes por computador']].values.tolist()).add_to(basemap)
basemap

# Set the app title
st.title("Retos de trayectoria")

# Display the text
st.write("Esta es una aplicación mediante la cual podremos visualizar nuestro indicadores de tranformación de manera transversal.")

# Display the map
st.write("Map of Schools")
st.write(basemap)  # Assuming 'basemap' is your Folium map object