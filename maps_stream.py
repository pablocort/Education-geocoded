import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go  # Importing graph_objects from plotly
import plotly as px



def load_data():
    zip_file_path = 'data/icfes_performance.zip'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        csv_file_name = zip_file.namelist()[0]
        with zip_file.open(csv_file_name) as file:
            icfes = pd.read_csv(file, delimiter='|')
    return icfes



def create_stacked_bar_plot(data, custom_palette):
    # Convert the custom_palette to the Plotly color format
    custom_palette_plotly = [
        f'rgb({int(color[0] * 255)},{int(color[1] * 255)},{int(color[2] * 255)})'
        for color in custom_palette
    ]
    selected_columns = ['Matemáticas', 
                    'Sociales',
                    'Ciencias naturales', 
                    'Lectura crítica']
    mean_percentages = []
    for column in selected_columns:
        percentages = data[column].value_counts(normalize=True) * 100
        mean_percentages.append(percentages)

# Create a DataFrame for the stacked bar plot
    mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
    mean_percentages_df = mean_percentages_df[[1,2,3,4]]

    # Transpose the DataFrame for horizontal bars
    mean_percentages_df = mean_percentages_df.transpose()

    # Create a horizontal stacked bar plot for mean percentages using Plotly
    fig = go.Figure()

    for column in mean_percentages_df.columns:
        fig.add_trace(go.Bar(
            x=mean_percentages_df.index,
            y=mean_percentages_df[column],
            text=[f'{value:.1f}%' for value in mean_percentages_df[column]],
            hoverinfo='text',
            name=f'Nivel {column}',
            marker=dict(color=custom_palette_plotly[int(column)-1]),
        ))

    # Customize the layout
    fig.update_layout(
        title='',
        xaxis_title='Áreas temáticas',
        yaxis_title='Participación porcentual',
        barmode='stack',
        showlegend=True,  # Set to True to show the legend
    )

    # Add legend titles for each Nivel
    for index, color in zip(mean_percentages_df.columns, custom_palette_plotly):
        fig.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='markers',
            marker=dict(color=color),
            name=f'Nivel {index}',
            legendgroup=f'Nivel {index}',
        ))

    return fig



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
    
    table_styles = [
        dict(selector="th", props=[("font-size", "10pt")]),
        dict(selector="td", props=[("font-size", "10pt")]),
    ]

    st.table(top_30_institutions.set_index('Nombre de la institución'))


# Load data
icfes = load_data()

# Set page configuration for wider margins
st.set_page_config(layout="wide")

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



# Use custom CSS to widen the layout
st.markdown(
    """
    <style>
        .main {
            max-width: 1200px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Create a layout with two columns
col1, col2 = st.columns(2)

# In the first column, display the stacked bar plot
with col1:
    fig = create_stacked_bar_plot(filtered_data, custom_palette)

# Add an empty space between the two columns
st.markdown("&nbsp;")

# In the second column, display the top 30 institutions table
with col2:
    create_top_30_institutions_table(filtered_data, title="Custom Title for Top 30 Institutions:")


