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
                 "WHERE orders.Active = 1 AND orders.CalculatedPendingQty != 0"
    sql_query = pd.read_sql(text_query, connection)
    df = pd.DataFrame(sql_query)
    df = df.rename(columns={'CalculatedPendingQty': 'Qty'})

    # Descargar calendario fiscal
    data = pd.read_excel(
        r"\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\DOCUMENTOS COMUNES\CALENDARIO FISCAL.xlsx",
        sheet_name='Calendar')
    fiscal_calendar_df = pd.DataFrame(data)

    # Agrupar por fechas los valores en la tabla de Sergio
    df['Fiscal Month'] = df.apply(lambda row: get_fiscal_month(row['DeliveryDate'], fiscal_calendar_df), axis=1)
    df = df.groupby(['Fiscal Month', 'Reference']).sum().reset_index()

    # Aplicar desglose de cajas de Sergio
    data4 = pd.read_excel(os.path.join(resources_folder, 'desglose_piezas_engranajes_motor.xlsx'))
    df_desgloses_motor = pd.DataFrame(data4)  # ['Caja', 'Ref', 'Uds']
    df4 = pd.DataFrame(columns=['Fiscal Month', 'Reference', 'Qty', 'Grupo'])
    for index in df_desgloses_motor.index:
        ref_caja = df_desgloses_motor['Caja'][index]
        referencia_int = df_desgloses_motor['Ref'][index]
        uds = df_desgloses_motor['Uds'][index]
        group = np.NAN
        caja_df: pd.DataFrame = df.loc[df['Reference'] == ref_caja]  # [Fiscal Month, Reference, Qty]
        for index2 in caja_df.index:
            fiscal_month = caja_df['Fiscal Month'][index2]
            box_qty = caja_df['Qty'][index2]
            qty = box_qty*uds
            df4 = df4.append(
                {'Fiscal Month': fiscal_month, 'Reference': referencia_int, 'Qty': qty, 'Grupo': group},
                ignore_index=True)

    df = df.append(df4, ignore_index=True)

    # Obtener datos de las celulas de Laura
    query = open('sql/query_obtener_datos_de_laura.sql', 'r')
    df2 = pd.read_sql_query(query.read(), connection)
    df2 = df2.drop(columns=['Id', 'PlanificationId', 'Code', 'Date'])
    df2 = df2.loc[df2['Qty'] != 0]

    # Agrupar por fechas los valores en la tabla de Laura
    df2['Fiscal Month'] = df2.apply(lambda row: get_fiscal_month(row['DeliveryDate'], fiscal_calendar_df), axis=1)
    df2 = df2.groupby(['Fiscal Month', 'Reference']).sum().reset_index()

    # Reemplazar las cajas en las referencias a fabricar en cada dia usando desgloses
    # Ejemplo: x1 DE1234 --> x1 CE152 + x2 CE369
    data3 = pd.read_excel(os.path.join(resources_folder, 'desglose_piezas_engranajes_internos.xlsx'))
    df_desgloses = pd.DataFrame(data3)  # ['Dpto', 'Minifabrica', 'Grupo', 'Caja', 'Ref', 'Uds']
    df['Grupo'] = np.NAN

    # Eliminar las referencias de las cajas de desglose que ya estan en el df
    box_refs = df_desgloses['Ref'].to_list()
    for ref in set(box_refs):
        df = df[df['Reference'] != ref]

    # crear tabla de referencias dentro de las cajas
    df3 = pd.DataFrame(columns=['Fiscal Month', 'Reference', 'Qty', 'Grupo'])
    for index in df_desgloses.index:
        ref_caja = df_desgloses['Caja'][index]
        referencia_int = df_desgloses['Ref'][index]
        uds = df_desgloses['Uds'][index]
        group = df_desgloses['Grupo'][index]
        caja_df: pd.DataFrame = df2[df2['Reference'] == ref_caja]  # [Fiscal Month, Reference, Qty]
        for index2 in caja_df.index:
            fiscal_month = caja_df['Fiscal Month'][index2]
            box_qty = caja_df['Qty'][index2]
            qty = box_qty * uds
            df3 = df3.append(
                {'Fiscal Month': fiscal_month, 'Reference': referencia_int, 'Qty': qty, 'Grupo': group},
                ignore_index=True)

    # Unir los dos dataframes
    df: pd.DataFrame
    final_df = df.append(df3, ignore_index=True)
    final_df = final_df.groupby(['Fiscal Month', 'Reference']).sum().reset_index()
    # Agregar columna de fechas en texto de mes fiscal
    final_df['Text Fiscal Month'] = final_df.apply(lambda row: get_text_fiscal_month(row['Fiscal Month']), axis=1)
    final_df: pd.DataFrame
    # Guardar el df en la carpeta en linea
    save_path = os.path.join(resources_folder, 'orders_table.xlsx')
    final_df.to_excel(save_path)

    return final_df


def get_fiscal_month(date, fiscal_calendar_df: pd.DataFrame):
    fiscal_month: pd.DataFrame = fiscal_calendar_df.loc[fiscal_calendar_df['Date'] == date]
    try:
        fiscal_month: datetime.date = fiscal_month['FiscalMonth'][fiscal_month.index[0]]
    except IndexError:
        print(date)
        print(fiscal_month.to_string())
        return 'N/A'
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
    # ref: R120638 --> 10.000 +/-
    # 31-oct hasta el 27-nov
    dff = get_orders_table()
