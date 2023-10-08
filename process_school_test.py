import pandas as pd

icfes = pd.read_csv(r'E:\portfolio_projects\Education_prediction\data\icfes\icfes_2022.csv',
             sep = '|')
geodata = pd.read_csv(r'E:\portfolio_projects\Education_prediction\geo_schools.csv',
                      sep = ';')
## rename columns names
geodata.columns = geodata.columns.str.lower()
geodata.rename(columns={'cod_dane':'sede_codigo'}, inplace=True)


## select certain variables from icfes test
select_icfes_cols = [var for var in icfes.columns if 'desemp' in var or\
                     'sede_codigo' in var]

other_vars = ['estu_tieneetnia', 'estu_depto_reside' ,'estu_mcpio_reside',"estu_genero"]

select_icfes_cols.extend(other_vars)
icfes = icfes[select_icfes_cols]

depto = icfes[['sede_codigo', 'estu_depto_reside','estu_mcpio_reside']]

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

