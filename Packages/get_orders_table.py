import datetime
import os.path
import warnings
import numpy as np
import pandas as pd
import pymssql

from Packages.constants import resources_folder


def get_orders_table() -> pd.DataFrame:
    warnings.filterwarnings("ignore")
    """Funcion que ejecuta un query en la bd
    y devuelve una columna con todas las referencias"""
    connection = pymssql.connect(server='Fgetcesql2\inst2', database='Blade_JD')
    # Datos de las celulas de sergio
    text_query = "SELECT orders.DeliveryDate, Reference.Code as Reference, orders.CalculatedPendingQty " \
                 "FROM [Order] orders " \
                 "INNER JOIN Reference " \
                 "ON Reference.Id = orders.ReferenceId " \
                 "WHERE orders.Active = 1"
    sql_query = pd.read_sql(text_query, connection)
    df = pd.DataFrame(sql_query)
    df = df.rename(columns={'CalculatedPendingQty': 'Qty'})

    # datos de las celulas de Laura
    query = open('sql/query_obtener_datos_de_laura.sql', 'r')
    df2 = pd.read_sql_query(query.read(), connection)
    df2 = df2.drop(columns=['Id', 'PlanificationId', 'Code', 'Date'])

    # ------- DEBUGGER -------
    # df_temp = df2
    # df_temp = df_temp.sort_values(by='DeliveryDate')
    # df_temp = df_temp.loc[df_temp['Reference'] == 'R120638']
    # print(df_temp.to_string())

    # Reemplazar los valores del df principal por las cantidades correctas de del df2(solo con los valores de laura)
    df = df2.combine_first(df)

    # Agrupar por fechas los valores
    data = pd.read_excel(
        r"\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\DOCUMENTOS COMUNES\CALENDARIO FISCAL.xlsx",
        sheet_name='Calendar')
    fiscal_calendar_df = pd.DataFrame(data)
    df['Fiscal Month'] = df.apply(lambda row: get_fiscal_month(row['DeliveryDate'], fiscal_calendar_df), axis=1)
    df = df.groupby(['Fiscal Month', 'Reference']).sum().reset_index()

    # Reemplazar las cajas en las referencias a fabricar en cada dia usando desgloses
    # Ejemplo: x1 DE1234 --> x1 CE152 + x2 CE369
    data3 = pd.read_excel(os.path.join(resources_folder, 'desglose_piezas_engranajes_internos.xlsx'))
    df_desgloses = pd.DataFrame(data3)  # ['Dpto', 'Minifabrica', 'Grupo', 'Caja', 'Ref', 'Uds']
    df['Grupo'] = np.NAN

    final_df = pd.DataFrame(columns=['Fiscal Month', 'Reference', 'Qty', 'Grupo'])

    # Eliminar las referencias de las cajas de desglose que ya estan en el df
    box_refs = df_desgloses['Ref'].to_list()
    for ref in set(box_refs):
        df = df[df['Reference'] != ref]

    for index in df.index:
        reference = str(df['Reference'][index])
        qty = int(df['Qty'][index])
        month = df['Fiscal Month'][index]
        row: pd.DataFrame = df_desgloses.loc[df_desgloses['Caja'] == reference]
        if row.empty:
            final_df = final_df.append({'Fiscal Month': month, 'Reference': reference, 'Qty': qty, 'Grupo': np.NaN},
                                       ignore_index=True)
            continue
        row = row.drop(columns=['Dpto', 'Minifabrica', 'Caja'])
        row['Qty'] = row['Uds'] * int(qty)
        row['Fiscal Month'] = month
        row = row.rename(columns={'Ref': 'Reference'})
        row = row.drop(columns=['Uds'])
        final_df = final_df.append(row, ignore_index=True)

    # Agrupar las referencias que se hacen en el mismo mes
    final_df = final_df.reset_index(drop=True)
    final_df = final_df.groupby(['Fiscal Month', 'Reference']).sum().reset_index()

    # Transformar la columna de grupo para que sea mas legible
    groups = set(df_desgloses['Grupo'].tolist())
    final_df['Grupo'] = final_df.apply(lambda row: split_groups(row['Grupo'], groups), axis=1)

    # Agregar columna de fechas en texto de mes fiscal
    final_df['Text Fiscal Month'] = final_df.apply(lambda row: get_text_fiscal_month(row['Fiscal Month']), axis=1)

    final_df: pd.DataFrame
    save_path = os.path.join(resources_folder, 'orders_table.xlsx')
    final_df.to_excel(save_path)

    return final_df


def get_fiscal_month(date, fiscal_calendar_df: pd.DataFrame):
    fiscal_month: pd.DataFrame = fiscal_calendar_df.loc[fiscal_calendar_df['Date'] == date]
    fiscal_month: datetime.date = fiscal_month['FiscalMonth'][fiscal_month.index[0]]
    return fiscal_month


def split_groups(group, groups: set):
    if group == 0:
        return None
    res = []
    for g in groups:
        if g in group:
            res.append(g)
    return res


def get_text_fiscal_month(date: datetime.date):
    return date.strftime('%b-%y')


if __name__ == '__main__':
    # ref: DE20877 --> cantidad 716 --> CE18212 | CE21493 | CE18213 | CE21494
    # 31-oct hasta el 27-nov
    dff = get_orders_table()
