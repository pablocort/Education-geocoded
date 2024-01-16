import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go
import folium
import plotly.express as px
import geopandas as gpd
from geopandas.tools import geocode
from geopy.geocoders import Nominatim
import geopy


from functions_viz import load_data, create_stacked_bar_plot, create_top_institutions_table
from functions_viz import load_data_geo, create_heat_map_p_2



icfes = load_data()

geo = load_data_geo()


icfes = icfes.merge(geo[["sede_codigo",'LONGITUD',	'LATITUD']], on = 'sede_codigo',
             how = 'left', indicator = 'merge_geo_2')
icfes = icfes[icfes['merge_geo_2'] == 'both']
del(geo)


icfes[(icfes['Departamento'] == 'ANTIOQUIA') & 
      (icfes['Sociales'].notna())]['LATITUD'].mean()
icfes[(icfes['Departamento'] == 'ANTIOQUIA') & 
      (icfes['Sociales'].notna())][['LATITUD', 'LONGITUD']]



def create_heat_map_p_2(icfes, selected_subject, selected_city):
    # Filter data based on selected city and subject
    filtered_data = icfes[(icfes['Departamento'] == selected_city) & (icfes[selected_subject].notna())]
    # Check if the filtered_data DataFrame is not empty
    if not filtered_data.empty:
        mean_latitude = filtered_data['LATITUD'].mean()
        mean_longitude = filtered_data['LONGITUD'].mean()
        # Create heat map using Plotly Express
        fig = px.scatter_mapbox(filtered_data,
                                lon=filtered_data['LONGITUD'], 
                                lat=filtered_data['LATITUD'],
                                zoom=5, 
                                #radius= 3,
                                center=dict(lat=mean_latitude, lon=mean_longitude),
                                color=filtered_data['punt_sociales_ciudadanas'],
                                size= filtered_data[selected_subject],
                                width=1200, height=900,
                                color_continuous_scale="Viridis",
                                title='x'
                                )
        fig.update_layout(mapbox_style= 'open-street-map')
        fig.update_layout(margin = {'r': 0, 't': 50, 'l':0, 'b':10})
        
        # Show the figure
        return fig
    else:
        print(f"No data available for selected city '{selected_city}' and subject '{selected_subject}'.")
        return px.density_mapbox() 
    
create_heat_map_p_2(icfes, 'Sociales', 'ANTIOQUIA')





# Set a custom user_agent to comply with Nominatim's ToS
geopy.geocoders.options.default_user_agent = "my-application"

# Geocode the geometry for Antioquia using OpenStreetMap Nominatim
antioquia_location = geocode("Antioquia, Colombia", 
                             provider='nominatim', user_agent="my-geocoding-app").geometry.iloc[0]

# Create a GeoDataFrame for Antioquia
antioquia_data = {'name': ['Antioquia'], 'geometry': [antioquia_location]}
antioquia_gdf = gpd.GeoDataFrame(antioquia_data, geometry='geometry')

# Load the naturalearth_lowres dataset
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Plot the map with focus on Antioquia within Colombia
fig, ax = plt.subplots(figsize=(10, 8))
world.plot(ax=ax, color='lightgray')  # Plot world map
antioquia_gdf.plot(ax=ax, color='blue', edgecolor='black', alpha=0.5)  # Plot Antioquia
ax.set_title('Antioquia within Colombia')
plt.show()



geopy.geocoders.options.default_user_agent = "my-geocoding-app"

# Geocode the geometry for Antioquia using OpenStreetMap Nominatim
antioquia_location = geocode("Antioquia, Colombia", provider='nominatim').geometry.iloc[0]

# Create a GeoDataFrame for Antioquia
antioquia_data = {'name': ['Antioquia'], 'geometry': [antioquia_location]}
antioquia_gdf = gpd.GeoDataFrame(antioquia_data, geometry='geometry')

# Save the GeoDataFrame to a shapefile or any other desired format
antioquia_gdf.to_file("antioquia_boundaries.shp")

# Load the saved GeoDataFrame
antioquia_boundaries_gdf = gpd.read_file("antioquia_boundaries.shp")

# Plot the map with focus on Antioquia within Colombia
fig, ax = plt.subplots(figsize=(10, 8))
world.plot(ax=ax, color='lightgray')  # Plot world map
antioquia_boundaries_gdf.plot(ax=ax, color='blue', edgecolor='black', alpha=0.5)  # Plot Antioquia
ax.set_title('Antioquia within Colombia')
plt.show()