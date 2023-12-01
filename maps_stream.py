import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile

def load_data():
    zip_file_path = 'data/icfes_performance.zip'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        csv_file_name = zip_file.namelist()[0]
        with zip_file.open(csv_file_name) as file:
            icfes = pd.read_csv(file, delimiter='|')
    return icfes

def create_stacked_bar_plot(filtered_data, selected_columns):
    mean_percentages = [filtered_data[column].value_counts(normalize=True) * 100 for column in selected_columns]
    mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
    mean_percentages_df = mean_percentages_df[[1, 2, 3, 4]]

    fig, ax = plt.subplots()
    mean_percentages_df.plot(kind='barh', stacked=True, figsize=(12, 8), color=custom_palette, ax=ax)

    plt.title(f'Porcentaje de participación de los niveles de desempeño, según área temática y departamento - {selected_city}')
    plt.xlabel('Participación porcentual de cada nivel de desempeño')
    plt.ylabel('')

    for i, (idx, row) in enumerate(mean_percentages_df.iterrows()):
        xpos = 0
        for j, value in enumerate(row):
            plt.text(xpos + value / 2, i, f'{value:.1f}%', ha='center', va='center')
            xpos += value

    st.pyplot(fig)

def create_top_30_institutions_table(filtered_data, title="Top 30 Institutions with Highest Median Scores:"):
    top_30_institutions = filtered_data[filtered_data['Matemáticas'] == 1]
    top_30_institutions = top_30_institutions.groupby('cole_nombre_establecimiento')['punt_matematicas'].\
        median().reset_index().sort_values(by=['punt_matematicas'], ascending=True)
    top_30_institutions = top_30_institutions.head(30)

    # Custom column names
    custom_column_names = {'cole_nombre_establecimiento': 'Nombre de la institución', 'punt_matematicas': 'Puntaje mediano en matemáticas'}

    st.write(f'## {title}')
    
    # Rename columns
    top_30_institutions.rename(columns=custom_column_names, inplace=True)
    
    st.table(top_30_institutions.set_index('Nombre de la institución'))


# Load data
icfes = load_data()

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
        filtered_data = icfes[(icfes['Departamento'] == selected_city) & (icfes['Municipio'] == selected_municipio)]



# Select the columns for the variables you want to analyze
selected_columns = ['Matemáticas', 'Sociales', 'Ciencias naturales', 'Lectura crítica']

# Custom color palette
custom_palette = [(0/255, 47/255, 135/255), (121/255, 163/255, 220/255), (232/255, 114/255, 0/255), (245/255, 179/255, 53/255)]




# Create a layout with two columns
col1, col2 = st.columns(2)

# In the first column, display the stacked bar plot
with col1:
    create_stacked_bar_plot(filtered_data, selected_columns)

# In the second column, display the top 30 institutions table
with col2:
    create_top_30_institutions_table(filtered_data, title="Custom Title for Top 30 Institutions:")



