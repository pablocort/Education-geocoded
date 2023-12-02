import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go

def load_data():
    zip_file_path = 'data/icfes_performance.zip'
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


def create_top_30_institutions_table(filtered_data, selected_subject, title="Top 30 de instituciones con desempeños más bajos:"):
    try:
        subject_column = areas[selected_subject]
        if subject_column not in filtered_data.columns:
            st.warning(f"The selected subject column '{subject_column}' does not exist in the DataFrame.")
            st.warning(f"Available columns: {', '.join(filtered_data.columns)}")
            return
    except KeyError:
        st.warning(f"The selected subject '{selected_subject}' is not recognized.")
        st.warning(f"Available subjects: {', '.join(areas.keys())}")
        return

    try:
        top_30_institutions = (
            filtered_data[filtered_data[subject_column] == 1]
            .groupby('cole_nombre_establecimiento')[f'punt_{selected_subject}']
            .median()
            .reset_index()
            .sort_values(by=[f'punt_{selected_subject}'], ascending=True)
            .head(30)
        )

        custom_column_names = {'cole_nombre_establecimiento': 'Nombre de la institución', f'punt_{selected_subject}': f'Puntaje mediano en {areas[selected_subject]}'}

        st.write(f'## {title}')

        top_30_institutions.rename(columns=custom_column_names, inplace=True)

        table_styles = [
            dict(selector="th", props=[("font-size", "10pt")]),
            dict(selector="td", props=[("font-size", "10pt")]),
        ]

        st.table(top_30_institutions.set_index('Nombre de la institución')).set_style(table_styles)
    except KeyError as e:
        st.warning(f"Error processing the data: {e}")

# ... (Rest of the code remains unchanged)

# Define the areas dictionary
areas = {
    "punt_matematicas": 'Matemáticas',
    'punt_ingles': 'Desempeño en inglés', 
    'punt_c_naturales': 'Ciencias naturales', 
    'punt_lectura_critica': 'Lectura crítica',
    'punt_sociales_ciudadanas': 'Sociales'
}






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

# Calculate the mean count percentage for each level (1 to 4) for each variable using filtered_data
mean_percentages = []
for column in selected_columns:
    percentages = filtered_data[column].value_counts(normalize=True) * 100
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
st.write(create_stacked_bar_plot(mean_percentages_df, custom_palette_plotly, selected_columns))

# Add an empty space between the two sections
st.markdown("&nbsp;")

selected_subject = st.selectbox("Seleccione un área", list(areas.values()))
st.write(f"Showing data for {areas[selected_subject]}")

# Call the function with the selected subject
create_top_30_institutions_table(filtered_data, selected_subject)


# Apply custom style to the table to make it less wide
#table_styles = [
#    dict(selector="th", props=[("font-size", "10pt")]),
#    dict(selector="td", props=[("font-size", "10pt")]),
#    dict(selector=".css-9i1zmu", props=[("max-width", "300px")])  # Adjust the max-width as needed
#]

#st.table(top_30_institutions.set_index('Nombre de la institución')).set_style(table_styles)


