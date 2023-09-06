import pandas as pd
import streamlit as st
#import geopandas as gpd
import os
os.getcwd()



### import dataframes of interest
path = r'E:\portfolio_projects\Education_prediction\geo_schools.csv'

geo_schools = pd.read_csv(path, sep=';', encoding='ISO-8859-1',
                          on_bad_lines='skip', index_col=False)

sedes_tic = pd.read_csv(r'C:\Users\pablo\Documents\dashboard_crime\code\processing_c600\intermediate_data\sedes_tics_counts.csv', sep= '|')


### process geodata


## process the geodata
geo_schools = geo_schools.dropna(subset=['COD_DANE'])  # Drop rows with NaN in 'COD_INST' column
geo_schools['sede_codigo'] = geo_schools['COD_DANE'].astype(str)
geo_schools['LATITUD'] = pd.to_numeric(geo_schools['LATITUD'].str.replace(',', '.'), errors='coerce')
geo_schools['LONGITUD'] = pd.to_numeric(geo_schools['LONGITUD'].str.replace(',', '.'), errors='coerce')

### merge database of tic with geocode
sedes_tic['sede_codigo'] = sedes_tic['sede_codigo'].astype(str)
sedes_tic = sedes_tic.merge(geo_schools, on = 'sede_codigo', how = 'left',
                            indicator = 'merge_geo')
sedes_tic.dropna(subset=['Estudiantes por computador'], inplace=True)
sedes_tic.dropna(subset=['LONGITUD'], inplace=True)
sedes_tic.dropna(subset=['LATITUD'], inplace=True)



import folium
from folium.plugins import HeatMap

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


