import pandas
import pandas as pd
import pymssql


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
            max_val = max(f_df['HorasSTD'].tolist())*100
            max_val = round(max_val, 2)
            df.loc[(df['Celula'] == celula) & (df['ReferenciaSAP'] == referencia), 'HorasSTD'] = max_val
            df = df.drop_duplicates()

    return df


df = get_master_table()
print(df.to_string())
