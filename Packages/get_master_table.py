import pandas
import pandas as pd
import pymssql
import numpy as np
import openpyxl
from Packages.constants import resources_folder
import os


def get_master_table() -> pd.DataFrame:
    """Funcion que ejecuta un query en la bd
    y devuelve una columna con todas las referencias"""
    connection = pymssql.connect(server='Fgetcesql1\inst1', database='TrabajoEquipo')
    text_query = "SELECT ref.ReferenciaSAP, ref.Celula, eq.NombreEquipo, dep.Minifabrica, dep.CodMinif, tiempos.HorasSTD " \
                 " FROM TReferencias ref " \
                 " INNER JOIN VEquipos eq " \
                 " ON ref.CodEquipo = eq.CodEquipo" \
                 " INNER JOIN VDepartamentos dep" \
                 " ON eq.Departamento = dep.Departamento" \
                 " INNER JOIN CReferenciasConSTD tiempos" \
                 " ON ref.Referencia = tiempos.Referencia" \
                 " WHERE ref.ReferenciaSAP != '' AND dep.CodMinif = 'EJYE' " \
                 " AND tiempos.Activa = 1 "
    sql_query = pd.read_sql(text_query, connection)
    df = pd.DataFrame(sql_query)
    # Escoger la mayor HoraSTD para cada celula/referencia
    celulas = set(df['Celula'].tolist())
    for celula in celulas:
        filtered_df = df[df['Celula'] == celula]
        referencias = set(filtered_df['ReferenciaSAP'].tolist())
        for referencia in referencias:
            f_df = filtered_df[filtered_df['ReferenciaSAP'] == referencia]
            max_val = max(f_df['HorasSTD'].tolist()) * 100
            max_val = round(max_val, 2)
            df.loc[(df['Celula'] == celula) & (df['ReferenciaSAP'] == referencia), 'HorasSTD'] = max_val
            df = df.drop_duplicates()

    # Agregar los tipos de operaciones segun celula a la tabla
    data2 = pd.read_excel(os.path.join(resources_folder, 'tabla_celulas_operaciones.xlsx'))
    tabla_op = pd.DataFrame(data2, dtype=str)
    df = pd.merge(df, tabla_op, how='left', left_on='Celula', right_on='Celulas')
    df = df.drop(columns=['Celulas'])

    # Agregar las celulas combinadas a la tabla
    text_query2 = "select Celula, Combinada from VCelulas_Comb WHERE Combinada != '' "
    sql_query2 = pd.read_sql(text_query2, connection)
    tabla_cel_comb = pd.DataFrame(sql_query2, dtype=str)
    df = pd.merge(df, tabla_cel_comb, how='left', left_on='Celula', right_on='Celula')
    df["Celula"] = df["Celula"] + df["Combinada"].fillna('')
    df = df.drop(columns=['Combinada'])

    # Agregar columna de porcentajes
    df["Porcentaje de Pedidos"] = 0

    return df


if __name__ == '__main__':
    df = get_master_table()
    df = df.loc[df['ReferenciaSAP'] == 'CE30105']
    print(df.to_string())

    # celulas = set(df['Celula'].tolist())
    # celulas = list(celulas)
    # celulas.sort()
    # data = {'Celulas': celulas, 'Tipo de Operacion': [np.nan] * len(celulas)}
    # dff = pd.DataFrame(data)
    # print(dff)
    # dff.to_excel('tabla_celulas_operaciones.xlsx', index=False)
