import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go
import folium
from folium.plugins import FastMarkerCluster



def load_data():
    zip_file_path = 'data/icfes_performance.zip'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        csv_file_name = zip_file.namelist()[0]
        with zip_file.open(csv_file_name) as file:
            icfes = pd.read_csv(file, delimiter='|')
            
    return icfes

def load_data_geo():
    zip_file_path = 'data/sedes_geo.zip'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        csv_file_name = zip_file.namelist()[0]
        with zip_file.open(csv_file_name) as file:
            icfes = pd.read_csv(file, delimiter='|')
    return icfes



def create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns):
    fig = go.Figure()

    for column in mean_percentages_df.columns:
        if column in selected_columns:
            fig.add_trace(go.Bar(
                x=mean_percentages_df.index,
                y=mean_percentages_df[column],
                text=[f'{value:.1f}%' if pd.notna(value) and isinstance(value, (int, float)) else '' for value in mean_percentages_df[column]],
                hoverinfo='text',
                name=f'Nivel {column}',
                marker=dict(color=custom_palette_plotly[selected_columns.index(column)])
            ))

    fig.update_layout(
        title='',
        xaxis_title='Áreas temáticas',
        yaxis_title='Participación porcentual',
        barmode='stack',
        showlegend=True,
    )

    for index, color in zip(selected_columns, custom_palette_plotly):
        fig.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='markers',
            marker=dict(color=color),
            name=f'Nivel {index}',
            legendgroup=f'Nivel {index}',
        ))

    return fig

areas = {"punt_matematicas": 'Matemáticas',
       'punt_ingles': 'desemp_ingles', 
       'punt_c_naturales':'Ciencias naturales', 
       'punt_lectura_critica': 'Lectura crítica',
       'punt_sociales_ciudadanas': 'Sociales'}

def create_top_institutions_table(filtered_data, selected_subject, num_institutions, decimal_points=1, title="Top de instituciones con desempeños más bajos:"):
    if selected_subject == 'Matemáticas':
        Puntaje_selected = 'punt_matematicas'
    elif selected_subject == 'Ciencias naturales':
        Puntaje_selected = 'punt_c_naturales'
    elif selected_subject == 'Lectura crítica':
        Puntaje_selected = 'punt_lectura_critica'
    elif selected_subject == 'Sociales':
        Puntaje_selected = 'punt_sociales_ciudadanas'
        
    top_institutions = (
        filtered_data[filtered_data[selected_subject] == 1]
        .groupby('cole_nombre_establecimiento')[Puntaje_selected]
        .median()
        .reset_index()
        .sort_values(by=[Puntaje_selected], ascending=True)
        .head(num_institutions)
    )

 # Rename columns
    custom_column_names = {'cole_nombre_establecimiento': 'Nombre de la institución', 
                           Puntaje_selected: 'Puntaje'}
    top_institutions.rename(columns=custom_column_names, inplace=True)

    # Set decimal points
    top_institutions['Puntaje'] = top_institutions['Puntaje'].round(decimal_points)

    # Set table styles
    table_styles = [
        dict(selector="th", props=[("font-size", "10pt")]),
        dict(selector="td", props=[("font-size", "10pt")]),
    ]

    # Display the table
    st.table(top_institutions.set_index('Nombre de la institución').style.format({'Puntaje': f"{{:.{decimal_points}f}}"}).set_table_styles(table_styles))

def create_cluster_map(data, selected_subject, selected_department):
    # Filter data based on selected department and subject
    filtered_data = data[(data['Departamento'] == selected_department) & (data[selected_subject].notna())]

    # Create the map centered around the selected department
    m = folium.Map(location=[filtered_data['LATITUD'].mean(), filtered_data['LONGITUD'].mean()], zoom_start=8)

    # Add marker clusters using FastMarkerCluster
    marker_cluster = FastMarkerCluster(filtered_data[['LATITUD', 'LONGITUD']].values).add_to(m)

    for index, row in filtered_data.iterrows():
        folium.Marker([row['LATITUD'], row['LONGITUD']],
                      popup=f"{row['Nombre de la institución']} - Puntaje: {row[selected_subject]}",
                      icon=None).add_to(marker_cluster)

    return m

def create_heat_map(data, selected_subject, selected_department):
    # Filter data based on selected department and subject
    filtered_data = data[(data['Departamento'] == selected_department) & (data[selected_subject].notna())]

    # Create the map centered around the selected department
    m = folium.Map(location=[filtered_data['LATITUD'].mean(), filtered_data['LONGITUD'].mean()], zoom_start=8)

    # Add heat map layer
    heat_data = [[row['LATITUD'], row['LONGITUD']] for index, row in filtered_data.iterrows()]
    folium.plugins.HeatMap(heat_data).add_to(m)

    return m