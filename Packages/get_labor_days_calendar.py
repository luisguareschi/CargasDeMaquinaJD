import os.path
import warnings
import dateutil.parser
import pandas as pd
import datetime as dt
import json

from Packages.constants import no_labor_days_folder


def get_labor_days_calendar(general_no_labor_days: dict):
    # Estructura de ejemplo: general_no_labor_days = {'21-10-2022': 'Fiesta local'}
    data = pd.read_excel(
        r"\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\DOCUMENTOS COMUNES\CALENDARIO FISCAL.xlsx",
        sheet_name='Calendar')
    df = pd.DataFrame(data)
    df['Causa'] = ''
    for index in df.index:
        day = int(df['Day Number of Week'][index])
        if day not in (6, 7):
            df['habil'][index] = True
        elif day in (6, 7):
            df['habil'][index] = False
            df['Causa'][index] = 'Fin de Semana'

    for no_labor_date in general_no_labor_days.keys():
        date = dt.datetime.strptime(no_labor_date, '%d-%m-%Y')
        df.loc[df['Date'] == date, 'habil'] = False
        df.loc[df['Date'] == date, 'Causa'] = general_no_labor_days[no_labor_date]

    return df


def save_no_labor_days(no_labor_days: dict, cell=None):
    """:param no_labor_days: diccionario de los dias que no hay trabajo
    :param cell: si es None se guarda para el calendario general"""
    if cell is None:
        with open(os.path.join(no_labor_days_folder, 'general_no_labor_days.json'), 'w') as fp:
            json.dump(no_labor_days, fp)
    else:
        path = os.path.join(no_labor_days_folder, f'{cell}_no_labor_days.json')
        if os.path.isfile(path):
            with open(path, 'w') as fp:
                json.dump(no_labor_days, fp)
        else:
            with open(os.path.join(no_labor_days_folder, 'empty.json')) as f:
                data = json.load(f)
            with open(path, 'w') as f:
                json.dump(data, f)
            with open(path, 'w') as f:
                json.dump(no_labor_days, f)


def get_labor_days_per_month(cell: str, months: list) -> dict:
    # get general labor days first
    path = os.path.join(no_labor_days_folder, 'general_no_labor_days.json')
    with open(path) as json_file:
        general_no_labor_days = json.load(json_file)
    df = get_labor_days_calendar(general_no_labor_days)
    cell_path = os.path.join(no_labor_days_folder, f'{cell}_no_labor_days.json')
    if os.path.isfile(cell_path):
        with open(cell_path) as json_file:
            cell_no_labor_days = json.load(json_file)
        for no_labor_date in cell_no_labor_days.keys():
            date = dt.datetime.strptime(no_labor_date, '%d-%m-%Y')
            df.loc[df['Date'] == date, 'habil'] = False
            df.loc[df['Date'] == date, 'Causa'] = cell_no_labor_days[no_labor_date]
    labor_days = {}
    fiscal_month: pd.Timestamp = (df['FiscalMonth'][0])  # 2015-11-01 00:00:00
    for month in months:
        m = month[0:3] + '-01' + month[3:]
        date = dateutil.parser.parse(m, yearfirst=True, dayfirst=False)
        days = df.loc[(df['FiscalMonth'] == date) & (df['habil'] == True), 'habil'].sum()
        labor_days[month] = days

    return labor_days


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    # save_no_labor_days(no_labor_days={'01-01-2022':'Reyes magos'}, cell='235A')
    get_labor_days_per_month('235A', months=['Nov-22', 'Dec-22', 'Jan-23'])
