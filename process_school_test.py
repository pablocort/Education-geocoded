import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from unidecode import unidecode
import zipfile



icfes = pd.read_csv(r'E:\portfolio_projects\Education_prediction\data\icfes\icfes_2022.csv',
             sep = '|')
geodata = pd.read_csv(r'E:\portfolio_projects\Education_prediction\geo_schools.csv',
                      sep = ';')
base_madre = pd.read_excel(r'C:\Users\pablo\UWCOLOMBIA\Evaluación - Documentos\Bases\Base_madre_2023.xlsx')


## rename columns names
geodata.columns = geodata.columns.str.lower()
geodata.rename(columns={'cod_dane':'sede_codigo'}, inplace=True)



### icfes cleaning
## select certain variables from icfes test
select_icfes_cols = [var for var in icfes.columns if 'desemp' in var or\
                     'sede_codigo' in var or 'depto' in var or 'mcpio' in var]

other_vars = ['estu_tieneetnia', 'estu_depto_reside' ,'estu_mcpio_reside',"estu_genero"]
select_icfes_cols.extend(other_vars)
icfes = icfes[select_icfes_cols]
icfes.rename(columns={'estu_depto_reside':'Departamento',
                      'estu_mcpio_reside' : 'Municipio',
                      'desemp_matematicas':'Matemáticas', 
                      'desemp_c_naturales':'Ciencias naturales', 
                      'desemp_lectura_critica':'Lectura crítica'}, inplace= True)


### merge process
icfes = icfes.merge( geodata, on = 'sede_codigo',
                    how = 'left', indicator= 'merge_geo')
icfes.merge_geo.value_counts()
icfes = icfes[icfes['merge_geo'] == 'both']

icfes.to_csv(r'data\icfes_performance.csv', sep = '|', index = False)
with zipfile.ZipFile('data/icfes_performance.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('data/icfes_performance.csv', arcname='icfes_performance.csv')


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
    percentages = icfes[column].value_counts(normalize=True) * 100
    mean_percentages.append(percentages)

# Create a DataFrame for the stacked bar plot
mean_percentages_df = pd.DataFrame(mean_percentages, index=selected_columns)
mean_percentages_df = mean_percentages_df[[1,2,3,4]]

# Create a stacked bar plot for mean percentages
ax = mean_percentages_df.plot(kind='barh', stacked=True, figsize=(10, 6),color=custom_palette)

# Customize the plot
plt.title('')
plt.xlabel('')
plt.ylabel('Participación porcentual')

# Add labels with one decimal place above each section
for i, (idx, row) in enumerate(mean_percentages_df.iterrows()):
    xpos = 0
    for j, value in enumerate(row):
        plt.text(xpos + value / 2, i, f'{value:.1f}%', ha='center', va='center')
        xpos += value

# Show the plot
plt.show()





















## transform dataframe to keep % of the lowest performance

icfes = icfes.groupby('sede_codigo')[['desemp_matematicas',
                                      'desemp_c_naturales',
                                      'desemp_lectura_critica',
                                      'desemp_sociales_ciudadanas']].\
                                        apply(lambda x:(x == 1).mean()*100).reset_index()



#merge datasets
icfes = icfes.merge(geodata, on='sede_codigo', how = 'left', indicator= 'merge_geo').\
    merge(depto, on='sede_codigo', how = 'left', indicator= 'merge_depto')

icfes = icfes[icfes['merge_geo'] == 'both']

# merge with UWC dataframe
base_madre.rename(columns={"COD_DANE" : 'sede_codigo'}, inplace= True)
icfes = icfes.merge(base_madre, on = 'sede_codigo', how= 'left', indicator= 'merge_uwc')
icfes.merge_uwc.value_counts()
icfes['Intervención UWC'] = icfes['merge_uwc'].apply(lambda x : 'Sí' if x == 'both' else 'No')
icfes['Intervención UWC'].value_counts()




icfes.rename(columns={'estu_depto_reside': 'depto'}, inplace=True)
icfes['depto'] = icfes['depto'].str.title()



no_include = ["Amazonas","Arauca",
              "San Andres",'Extranjero',
              "Boyaca","Caqueta","Casanare","Cauca", "Choco", "Cordoba", 
              "Guainia", "Guaviare", "Huila", "La Guajira",'Magdalena',
              "Nariño","Norte Santander","Putumayo","Quindio",
              "Risaralda","Santander","Sucre","Tolima","Vaupes", 'Vichada'
]

icfes = icfes[~icfes['depto'].isin(no_include)]
icfes.depto.value_counts()



'''
### graph 1
'''

National = icfes['desemp_matematicas'].mean()

df = icfes.groupby(['depto','Intervención UWC'])['desemp_matematicas'].median().reset_index()
#df = df.groupby('depto','Intervención UWC')['punt_lectura_critica'].median().reset_index()

df_sorted = df.sort_values(by='desemp_matematicas', ascending=False)

# Define custom colors
custom_colors = [(245/255, 179/255, 53/255), (0/255, 47/255, 135/255)]
# Create a horizontal bar plot with hue and custom colors
plt.figure(figsize=(10, 12))
ax = sns.barplot(data=df_sorted, y='depto', x='desemp_matematicas', 
                 hue='Intervención UWC', palette=custom_colors, orient='h')
plt.title('Porcentaje de estudiantes con desempeño bajo en pruebas de matemáticas', 
          fontsize=18)
plt.ylabel('Departamento', fontsize=18)
plt.xlabel('%', fontsize=18)

ax.set_xlim(0, 40) 

# Change the legend title
# Add labels to the bars
for p in ax.patches:
    ax.annotate(f'{p.get_width():.1f}', (p.get_width() + 1.5, p.get_y() + p.get_height() / 2.),
                ha='center', va='center', fontsize=14, color='black', xytext=(5, 0),
                textcoords='offset points')

# Add a vertical dashed line at x=118.1 with a label
plt.axvline(x=National, color='red', linestyle='--', label='Tasa Nacional')
ax.legend(title = 'Intervención UWC',fontsize=14,
          #loc='bottom right', 
          title_fontsize = 15)
ax.tick_params(axis='both', which='major', labelsize=16)

# Increase font size for legend items
legend = ax.get_legend()
for item in legend.get_texts():
    item.set_fontsize(15)

plt.tight_layout()
plt.savefig('results_graphs/final_presentation/desempeño bajo_mate.png', 
            dpi=1000, bbox_inches='tight')
plt.show()








'''
### graph 1
'''

National = icfes['desemp_lectura_critica'].mean()

df = icfes.groupby(['depto','Intervención UWC'])['desemp_lectura_critica'].median().reset_index()
#df = df.groupby('depto','Intervención UWC')['punt_lectura_critica'].median().reset_index()

df_sorted = df.sort_values(by='desemp_lectura_critica', ascending=False)

# Define custom colors
custom_colors = [(245/255, 179/255, 53/255), (0/255, 47/255, 135/255)]
# Create a horizontal bar plot with hue and custom colors
plt.figure(figsize=(10, 12))
ax = sns.barplot(data=df_sorted, y='depto', x='desemp_lectura_critica', 
                 hue='Intervención UWC', palette=custom_colors, orient='h')
plt.title('Porcentaje de estudiantes con desempeño bajo en pruebas de Lectura Crítica', 
          fontsize=18)
plt.ylabel('Departamento', fontsize=18)
plt.xlabel('%', fontsize=18)

ax.set_xlim(0, 30) 

# Change the legend title
# Add labels to the bars
for p in ax.patches:
    ax.annotate(f'{p.get_width():.1f}', (p.get_width() + 1.5, p.get_y() + p.get_height() / 2.),
                ha='center', va='center', fontsize=14, color='black', xytext=(5, 0),
                textcoords='offset points')

# Add a vertical dashed line at x=118.1 with a label
plt.axvline(x=National, color='red', linestyle='--', label='Tasa Nacional')
ax.legend(title = 'Intervención UWC',fontsize=14,
          loc='lower right', 
          title_fontsize = 15)
ax.tick_params(axis='both', which='major', labelsize=16)

# Increase font size for legend items
legend = ax.get_legend()
for item in legend.get_texts():
    item.set_fontsize(15)

plt.tight_layout()
plt.savefig('results_graphs/final_presentation/desempeño bajo_ lectura.png', 
            dpi=1000, bbox_inches='tight')
plt.show()

