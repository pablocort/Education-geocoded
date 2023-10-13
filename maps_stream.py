
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile

## load data
zip_file_path = 'data/icfes_performance.zip'
# Open the compressed file in binary read mode ('rb')
with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
    # Assuming the ZIP file contains a CSV file
    csv_file_name = zip_file.namelist()[0]  #Get the first file in the ZIP archive

    # Read the CSV file from the ZIP archive into a DataFrame
    with zip_file.open(csv_file_name) as file:
        icfes = pd.read_csv(file, delimiter='|') 
 


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

