import datetime as dt
import os
import pandas as pd
from Packages.constants import resources_folder


def calculate_carga_de_maquina() -> pd.DataFrame:
    data = pd.read_excel(os.path.join(resources_folder, 'master_configuration_table.xlsx'))
    master_table = pd.DataFrame(data)
    data2 = pd.read_excel(os.path.join(resources_folder, 'orders_table.xlsx'))
    orders_table = pd.DataFrame(data2)
    orders_table = pd.merge(master_table, orders_table, how='left',
                            left_on='ReferenciaSAP', right_on='Reference')
    orders_table = orders_table.drop(columns=['Reference', 'Unnamed: 0'])
    orders_table['CalculatedQty'] = orders_table['Qty'] * orders_table['Porcentaje de Pedidos']
    today = dt.datetime.today()
    today = pd.to_datetime(today).floor('D')
    last_day = pd.to_datetime(today.replace(year=today.year+1)).floor('D')
    current_month = get_fiscal_month(date=today)
    last_month = get_fiscal_month(date=last_day)
    orders_table = orders_table[(last_month >= orders_table['Fiscal Month']) &
                                (orders_table['Fiscal Month'] > current_month)]
    return orders_table


def get_fiscal_month(date: dt.datetime.today()):
    data = pd.read_excel(
        r"\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\DOCUMENTOS COMUNES\CALENDARIO FISCAL.xlsx",
        sheet_name='Calendar')
    fiscal_calendar_df = pd.DataFrame(data)
    fiscal_calendar_df['Date'] = pd.to_datetime(fiscal_calendar_df['Date'])
    fiscal_month: pd.DataFrame = fiscal_calendar_df.loc[fiscal_calendar_df['Date'] == date]
    fiscal_month: dt.date = fiscal_month['FiscalMonth'][fiscal_month.index[0]]
    return fiscal_month


if __name__ == '__main__':
    orders_table = calculate_carga_de_maquina()
    row = orders_table.loc[(orders_table['ReferenciaSAP'] == 'R544004') & (orders_table['Celula'] == '235A')]
    print(row.to_string())
