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

## load data
zip_file_path = 'data/sedes_geo.zip'
# Open the compressed file in binary read mode ('rb')
with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
    # Assuming the ZIP file contains a CSV file
    csv_file_name = zip_file.namelist()[0]  #Get the first file in the ZIP archive

    # Read the CSV file from the ZIP archive into a DataFrame
    with zip_file.open(csv_file_name) as file:
        sedes_tic = pd.read_csv(file, delimiter='|') 
 

def generateBaseMap(default_location=[4.631530, -74.109180], default_zoom_start=11):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    return base_map

basemap=generateBaseMap()


#from folium.plugins import FastMarkerCluster
FastMarkerCluster(data=sedes_tic[['LATITUD', 'LONGITUD','Estudiantes por computador']].values.tolist()).add_to(basemap)

'''A continuación se presentan el promedio del número total de estudiantes por computador para cada región en Colombia'''

st_folium(basemap)
















#### 2


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import folium
from streamlit_folium import st_folium
import altair as alt



## load data
zip_file_path = 'data/icfes_performance.zip'
# Open the compressed file in binary read mode ('rb')
with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
    # Assuming the ZIP file contains a CSV file
    csv_file_name = zip_file.namelist()[0]  #Get the first file in the ZIP archive

    # Read the CSV file from the ZIP archive into a DataFrame
    with zip_file.open(csv_file_name) as file:
        icfes = pd.read_csv(file, delimiter='|') 
 
st.write("""
# El siguiente tablero permite localizar aquellas instituciones que afrontan mayores retos en cuanto al desempeño en pruebas Saber 11
""")

# Create a select box for city selection
selected_city = st.selectbox("Select a City", icfes['Departamento'].unique())

st.write(f"Showing data for {selected_city}")

# Filter the DataFrame based on the selected city
filtered_data = icfes[icfes['Departamento'] == selected_city]

######
######
# Select the columns for the variables you want to analyze
selected_columns = ['Matemáticas', 
                    'Sociales',
                    'Ciencias naturales', 
                    'Lectura crítica']

custom_palette = [(0/255, 47/255, 135/255),  # RGB for the first color
                  (121/255, 163/255, 220/255),  # RGB for the second color
                  (232/255, 114/255, 0/255),  # RGB for the third color
                  (245/255, 179/255, 53/255)]  # RGB for the fourth color

# Calculate the mean count percentage for each level (1 to 4) for each variable
mean_percentages = []
for column in selected_columns:
    percentages = filtered_data[column].value_counts(normalize=True) * 100
    mean_percentages.append(percentages)

# Create a DataFrame for the stacked bar plot
mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
mean_percentages_df = mean_percentages_df[[1,2,3,4]]

# Create a stacked bar plot for mean percentages
# Create a stacked bar plot for mean percentages
fig, ax = plt.subplots()  # Create a Matplotlib figure and axis
mean_percentages_df.plot(kind='barh', stacked=True, figsize=(12, 8), 
                         color=custom_palette, ax=ax)

# Customize the plot
plt.title('Porcentaje de participación de los niveles de desempeño, \nsegún area temática y departamento')
plt.xlabel('Participación porcentual de cada nivel de desempeño')
plt.ylabel('')

# Add labels with one decimal place above each section
for i, (idx, row) in enumerate(mean_percentages_df.iterrows()):
    xpos = 0
    for j, value in enumerate(row):
        plt.text(xpos + value / 2, i, f'{value:.1f}%', ha='center', va='center')
        xpos += value

# Display the Matplotlib plot using Streamlit's st.pyplot
st.pyplot(fig)




# Select the top 30 institutions with the highest participation in Level 1
top_30_institutions = filtered_data[filtered_data['Matemáticas'] == 1]
top_30_institutions = top_30_institutions.groupby('cole_nombre_establecimiento')['punt_matematicas'].median().reset_index().sort_values(by=['punt_matematicas'])

top_30_institutions = top_30_institutions.head(30)

# Display the top 30 institutions with a bar plot
chart = alt.Chart(top_30_institutions).mark_bar().encode(
    x='cole_nombre_establecimiento',
    y='punt_matematicas'
)

st.altair_chart(chart, use_container_width=True)




filtered_data['latitud'] = filtered_data['latitud'].str.replace(',', '.').astype(float)
filtered_data['longitud'] = filtered_data['longitud'].str.replace(',', '.').astype(float)

# Ensure 'latitud' and 'longitud' are numeric and drop rows with missing values
filtered_data['latitud'] = pd.to_numeric(filtered_data['latitud'])
filtered_data['longitud'] = pd.to_numeric(filtered_data['longitud'])
filtered_data = filtered_data.dropna(subset=['latitud', 'longitud'])

filtered_data = filtered_data.groupby(['sede_codigo','longitud','latitud']).head(1)
top_30_institutions_ = pd.merge(top_30_institutions.reset_index(),filtered_data,on = 'sede_codigo', how = 'inner', indicator = 'merge_geo2')

# Create a map centered on the selected city
city_location = [filtered_data['latitud'].mean(), filtered_data['longitud'].mean()]
m = folium.Map(location=city_location, zoom_start=10)


# Add markers for the top 30 institutions
for _, row in top_30_institutions_.iterrows():
    lat = row['latitud']  # Assuming you have a 'latitud' column
    lon = row['longitud']  # Assuming you have a 'longitud' column
    institution_name = row['sede_codigo']  # Assuming this is the institution name
    folium.Marker([lat, lon], popup=institution_name).add_to(m)

# Display the map in Streamlit

st_folium(m)
st.write(top_30_institutions_)  





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




def create_stacked_bar_plot(filtered_data, selected_columns, custom_palette):
    # Calculate mean percentages
    mean_percentages = [filtered_data[column].value_counts(normalize=True) * 100 for column in selected_columns]
    mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)

    # Reshape DataFrame for Plotly
    mean_percentages_df = mean_percentages_df.T

    # Create an interactive stacked bar plot using Plotly graph_objects
    fig = go.Figure()

    for i, column in enumerate(mean_percentages_df.columns):
        fig.add_trace(go.Bar(x=mean_percentages_df.index, y=mean_percentages_df[column],
                             name=str(column), marker_color=custom_palette[i]))

    # Update layout for better visibility
    fig.update_layout(barmode='stack', xaxis_title='Sample Value', yaxis_title='Percentage',
                      title=f'Porcentaje de participación de los niveles de desempeño - {filtered_data.iloc[0]["Departamento"]}',
                      legend_title_text='Performance Level', 
                      legend=dict(title=dict(text='Performance Level')),
                      width = 500)

    # Display the plot
    st.plotly_chart(fig)


    ##3

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





def create_stacked_bar_plot(data, custom_palette):
    custom_palette_plotly = [f'rgb({int(color[0] * 255)},{int(color[1] * 255)},{int(color[2] * 255)})' for color in custom_palette]
    
    selected_columns = ['Matemáticas', 'Sociales', 'Ciencias naturales', 'Lectura crítica']
    mean_percentages = [data[column].value_counts(normalize=True) * 100 for column in selected_columns]

    mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
    mean_percentages_df = mean_percentages_df[[1, 2, 3, 4]].transpose()

    fig = go.Figure()

    for column in mean_percentages_df.columns:
        fig.add_trace(go.Bar(
            x=mean_percentages_df.index,
            y=mean_percentages_df[column],
            text=[f'{value:.1f}%' for value in mean_percentages_df[column]],
            hoverinfo='text',
            name=f'Nivel {column}',
            marker=dict(color=custom_palette_plotly[int(float(column)) - 1])
        ))

    fig.update_layout(
        title='',
        xaxis_title='Áreas temáticas',
        yaxis_title='Participación porcentual',
        barmode='stack',
        showlegend=True,
    )

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







# Create the stacked bar plot
st.write(create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns))

# Add an empty space between the two sections
st.markdown("&nbsp;")

st.write(f"Showing data for {selected_city}")

areas = [
    'Matemáticas',
    'Ciencias naturales', 
    'Lectura crítica',
    'Sociales']


selected_subject = st.selectbox("Seleccione un área", areas)
#st.write(f"Showing data for {areas[selected_subject]}")

# Call the function with the selected subject
create_top_30_institutions_table(filtered_data,selected_subject, 10)


