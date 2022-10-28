import os.path

import pandas as pd
from Packages.constants import resources_folder


def get_numero_op(celula: str) -> float:
    """Funcion que calcula el numero de operarios
    disponibles en la celula indicada"""
    file_path = os.path.join(resources_folder, 'nro_operarios_celula.xlsx')
    data = pd.read_excel(file_path)
    df = pd.DataFrame(data, dtype=str)
    df = df.rename(columns={'CELULA ': 'CELULA'})
    try:
        nro_op = df.loc[df['CELULA'] == celula, 'OPERARIOS'].to_list()[0]
    except IndexError:
        print(f'Celula {celula} no tiene asignado un numero de operarios')
        nro_op = 1

    return float(nro_op)


if __name__ == '__main__':
    x = get_numero_op('147')
    print(x, type(x))
