import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go


from functions_viz import load_data, create_stacked_bar_plot, create_top_30_institutions_table



# Load data
icfes = load_data()

# Set page configuration for wider margins
#st.set_page_config(layout="wide")

# Streamlit app
st.write("""
# El siguiente tablero permite localizar aquellas instituciones que afrontan mayores retos en cuanto al desempeño en pruebas Saber 11
""")
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

# Transpose the DataFrame for horizontal bars
mean_percentages_df = mean_percentages_df.transpose()

# Create the stacked bar plot
left_column, right_column = st.beta_columns(2)

# Graph on the left
with left_column:
    st.write(create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns))

# Add an empty space between the two sections
st.markdown("&nbsp;")


# Table on the right
st.write(f"Showing data for {selected_city}")
    
areas = [
    'Matemáticas',
    'Ciencias naturales', 
    'Lectura crítica',
    'Sociales']

selected_subject = st.selectbox("Seleccione un área", areas)

# Use the columns method instead of beta_columns
left_column, right_column = st.columns(2)

# Graph on the left
with left_column:
    st.write(create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns))

# Table on the right
with right_column:
    create_top_30_institutions_table(filtered_data, selected_subject, 10)
    