
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import folium


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
# El siguiente tablero permite localizar aquellas instituciones que afrontan mayores
# retos en cuanto al desempeño en pruebas Saber 11
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
top_30_institutions = top_30_institutions['sede_codigo'].value_counts().head(30)

# Display the top 30 institutions with a bar plot
st.bar_chart(top_30_institutions)



filtered_data['latitud'] = filtered_data['latitud'].str.replace(',', '.').astype(float)
filtered_data['longitud'] = filtered_data['longitud'].str.replace(',', '.').astype(float)

# Ensure 'latitud' and 'longitud' are numeric and drop rows with missing values
filtered_data['latitud'] = pd.to_numeric(filtered_data['latitud'])
filtered_data['longitud'] = pd.to_numeric(filtered_data['longitud'])
filtered_data = filtered_data.dropna(subset=['latitud', 'longitud'])

filtered_data_geo = filtered_data.groupby(['sede_codigo','longitud','latitud']).head(1)
top_30_institutions_map = top_30_institutions.merge(filtered_data_geo,
                                                    on = 'sede_codigo', how = 'inner', indicator = 'merge_geo2')

# Create a map centered on the selected city
city_location = [filtered_data['latitud'].mean(), filtered_data['longitud'].mean()]
m = folium.Map(location=city_location, zoom_start=12)


# Add markers for the top 30 institutions
for _, row in top_30_institutions_map.iterrows():
    lat = row['latitud']  # Assuming you have a 'latitud' column
    lon = row['longitud']  # Assuming you have a 'longitud' column
    institution_name = row['sede_codigo']  # Assuming this is the institution name
    folium.Marker([lat, lon], popup=institution_name).add_to(m)

# Display the map in Streamlit
st.write(m)