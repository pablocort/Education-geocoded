import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
#from streamlit_folium import folium_static


from functions_viz import load_data, create_stacked_bar_plot, create_top_institutions_table
from functions_viz import load_data_geo, create_heat_map_p_2


st.set_page_config(layout="wide")

# Load data
icfes = load_data()

geo = load_data_geo()


icfes = icfes.merge(geo[["sede_codigo",'LONGITUD',	'LATITUD']], on = 'sede_codigo',
             how = 'left', indicator = 'merge_geo_2')
icfes = icfes[icfes['merge_geo_2'] == 'both']
del(geo)


# Set page configuration for wider margins
#st.set_page_config(layout="wide")
#

# Streamlit app
st.write("""
# El siguiente tablero permite localizar aquellas instituciones que afrontan mayores retos en cuanto al desempeño en pruebas Saber 11
""")

# Sidebar with index and page selection
selected_page = st.sidebar.radio("Navigate", ["Stacked Bar Plot", "Top Institutions Table", "Heat Map"])


# Create a select box for city selection
selected_city = st.selectbox("Seleccione un departamento", ['All'] + list(icfes['Departamento'].unique()))
st.write(f"Showing data for {selected_city}")

# Create a select box for municipio selection based on the selected departamento
if selected_city != 'All':
    municipios = ['All'] + list(icfes[icfes['Departamento'] == selected_city]['Municipio'].unique())
    selected_municipio = st.selectbox('Seleccione un municipio', municipios)
else:
    selected_municipio = 'All'

# Filter the DataFrame based on the selected departamento and municipio
if selected_city == 'All':
    filtered_data = icfes
else:
    if selected_municipio == 'All':
        filtered_data = icfes[icfes['Departamento'] == selected_city]
    else:
        filtered_data = icfes[(icfes['Departamento'] == selected_city) & 
                              (icfes['Municipio'] == selected_municipio)]

# Select the columns for the variables you want to analyze
selected_columns = ['Matemáticas', 'Sociales', 'Ciencias naturales', 'Lectura crítica']

# Custom color palette
custom_palette = [(0/255, 47/255, 135/255), (121/255, 163/255, 220/255), (232/255, 114/255, 0/255), (245/255, 179/255, 53/255)]

# Calculate the mean count percentage for each level (1 to 4) for each variable using filtered_data
mean_percentages = []
for column in selected_columns:
    percentages = filtered_data[column].value_counts(normalize=True)*100
    mean_percentages.append(percentages)

# Create a DataFrame for the stacked bar plot using filtered_data
mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
mean_percentages_df = mean_percentages_df[[1, 2, 3, 4]]

# Convert the custom_palette to the Plotly color format
custom_palette_plotly = [
    f'rgb({int(color[0] * 255)},{int(color[1] * 255)},{int(color[2] * 255)})'
    for color in custom_palette
]


mean_percentages_df = mean_percentages_df.transpose()


# Main content based on selected page
if selected_page == "Stacked Bar Plot":
    st.write(create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns))
elif selected_page == "Top Institutions Table":
    areas = ['Matemáticas', 'Ciencias naturales', 'Lectura crítica', 'Sociales']
    selected_subject = st.selectbox("Seleccione un área", areas)
    num_institutions = st.selectbox("Seleccione el número de instituciones", [10, 20, 30])
    create_top_institutions_table(filtered_data, selected_subject, num_institutions)
elif selected_page == "Heat Map":
    areas = [
    'Matemáticas',
    'Ciencias naturales', 
    'Lectura crítica',
    'Sociales']

    for subject in areas:
        icfes[subject] = pd.to_numeric(icfes[subject], errors='coerce')
        icfes['LATITUD'] = pd.to_numeric(icfes['LATITUD'], errors='coerce')
        icfes['LONGITUD'] = pd.to_numeric(icfes['LONGITUD'], errors='coerce')
    st.write("Cluster Map")
    selected_subject = st.selectbox("Seleccione un área", areas)

    map = create_heat_map_p_2(icfes, selected_subject, selected_city)
    st.plotly_chart(map, use_container_width=False)



