
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, FastMarkerCluster

st.write("""
# Indicadores de de seguimiento a los retos transversales

Mapa de concetración de número de estudiantes por equipo de cómputo

""")

sedes_tic = pd.read_csv(r'data\sedes_geo.csv', sep = '|')

def generateBaseMap(default_location=[4.631530, -74.109180], default_zoom_start=11):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    return base_map

basemap=generateBaseMap()


#from folium.plugins import FastMarkerCluster
FastMarkerCluster(data=sedes_tic[['LATITUD', 'LONGITUD','Estudiantes por computador']].values.tolist()).add_to(basemap)
basemap

st.write(basemap)

