import pandas as pd
from tkinter import ttk
import tkinter as tk
from Packages.calculate_carga_de_maquina import calculate_carga_de_maquina
from Packages.gui.CargasDeMaquinaWindow.sort_date import sort_list_by_date
import datetime as dt

from Packages.gui.ScrollableFrame import VerticalScrolledFrame


class NumberOfPiecesTable(ttk.Frame):
    def __init__(self, parent, cargas_de_maq):
        super().__init__(parent)
        # Crear frame que puede hacer scroll para colocar la tabla de cantidades adentroç
        self.top_frame = VerticalScrolledFrame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Variables importantes
        self.cargas_de_maq = cargas_de_maq
        self.celula = '235A'
        self.labor_days = {'Nov-22': 17, 'Dic-22': 14, 'Ene-23': 10, 'Feb-23': 12, 'Mar-23': 18, 'Abr-23': 18,
                           'May-23': 17, 'Jun-23': 20, 'Jul-23': 25, 'Ago-23': 0, 'Sep-23': 18, 'Oct-23': 22}  # Luego se hara automaticamente
        # Obtener titulos de las columnas
        self.all_dates = set(self.cargas_de_maq['Text Fiscal Month'].to_list())
        self.all_dates = list(self.all_dates)
        self.all_dates = sort_list_by_date(self.all_dates)
        self.headers = ['REFERENCIA', 'HRS STD'] + self.all_dates + ['TOTAL PZS', 'PIEZAS/DIA', 'TOTAL HRS STD']
        # Insertar titulos de columnas en la gui
        col = 0
        for head in self.headers:
            lenght = len(head)
            label = ttk.Label(self.top_frame.interior, width=int(lenght * 1.5), text=head, bootstyle='inverse-primary', anchor='center')
            label.grid(row=2, column=col, sticky='ew')
            col += 1
        self.title_label = tk.Label(self.top_frame.interior, text=f'CARGAS DE MAQUINA EYE: CELULA {self.celula}',
                               anchor='center', font=('Sans Serif', 20))
        self.title_label.grid(row=0, column=2, columnspan=len(self.all_dates), sticky='we')
        number_of_parts_label = ttk.Label(self.top_frame.interior, text='NUMERO DE PIEZAS', anchor='center',
                                          bootstyle='inverse-dark')
        number_of_parts_label.grid(row=1, column=2, columnspan=len(self.all_dates), sticky='we')
        # Variables donde se guardan los widgets
        self.reference_entries = {}
        self.hrs_std_entries = {}
        self.number_of_parts_entries = {}
        self.total_parts_entries = {}
        self.parts_per_day_entries = {}

        # Calcular los datos
        self.calculate_data()

    def calculate_data(self):
        self.title_label.configure(text=f'CARGAS DE MAQUINA EYE: CELULA {self.celula}')
        # Insertar datos
        self.selected_df: pd.DataFrame = self.cargas_de_maq.loc[self.cargas_de_maq['Celula'] == self.celula]
        print(self.selected_df.to_string())
        references = self.selected_df['ReferenciaSAP'].to_list()
        references = set(references)
        references = list(references)
        row_n = 3
        for ref in references:
            # Escribir nombre de referencia
            ref_entry = ttk.Entry(self.top_frame.interior)
            ref_entry.insert(tk.END, ref)
            ref_entry.configure(state='readonly')
            ref_entry.grid(row=row_n, column=0)
            self.reference_entries[ref] = ref_entry
            # Escribir Hrs STD
            hrs_std = self.selected_df.loc[self.selected_df['ReferenciaSAP'] == ref]['HorasSTD'].values[0]
            hrs_std_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(hrs_std)) * 1.2))
            hrs_std_entry.insert(tk.END, hrs_std)
            hrs_std_entry.configure(state='readonly')
            hrs_std_entry.grid(row=row_n, column=1, sticky='ew')
            self.hrs_std_entries[ref] = hrs_std_entry
            # Escribir las cantidades por mes
            quantities = {}
            for col_n, date in enumerate(self.all_dates):
                qty = self.selected_df.loc[
                    (self.selected_df['ReferenciaSAP'] == ref) & (self.selected_df['Text Fiscal Month'] == date)]
                try:
                    qty = int(qty['CalculatedQty'][qty.index[0]])
                except:
                    qty = 'N/A'
                qty_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(qty)) * 1.2))
                qty_entry.insert(tk.END, str(qty))
                qty_entry.configure(state='readonly')
                qty_entry.grid(row=row_n, column=2 + col_n, sticky='ew')
                quantities[date] = qty_entry
            self.number_of_parts_entries[ref] = quantities

            # Escribir total de cantidades mensuales
            total_qty = self.calculate_total_parts(ref)
            total_qty_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(total_qty)) * 1.2))
            total_qty_entry.insert(tk.END, str(total_qty))
            total_qty_entry.configure(state='readonly')
            total_qty_entry.grid(row=row_n, column=3+col_n, sticky='ew')
            self.total_parts_entries[ref] = total_qty_entry

            # Escribir piezas por dia
            parts_per_day = self.calculate_parts_per_day(total_qty)
            part_per_day_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(parts_per_day)) * 1.2))
            part_per_day_entry.insert(tk.END, str(parts_per_day))
            part_per_day_entry.configure(state='readonly')
            part_per_day_entry.grid(row=row_n, column=4 + col_n, sticky='ew')
            self.parts_per_day_entries[ref] = part_per_day_entry

            # Sumar una fila
            row_n += 1

    def delete_widgets(self):
        for ref in self.reference_entries:
            title: ttk.Entry = self.reference_entries[ref]
            title.grid_forget()
            hrs_std: ttk.Entry = self.hrs_std_entries[ref]
            hrs_std.grid_forget()
            dates = self.number_of_parts_entries[ref]
            for date in dates:
                d: ttk.Entry = dates[date]
                d.grid_forget()
            total_qty: ttk.Entry = self.total_parts_entries[ref]
            total_qty.grid_forget()
            part_per_day_entry: ttk.Entry = self.parts_per_day_entries[ref]
            part_per_day_entry.grid_forget()

    def calculate_total_parts(self, ref) -> int:
        quantities: dict = self.number_of_parts_entries[ref]
        total_qty = 0
        for entry in quantities.values():
            entry: ttk.Entry
            val = entry.get()
            try:
                val = int(float(val))
                total_qty = total_qty + val
            except ValueError:
                pass
        return total_qty

    def calculate_parts_per_day(self, total_qty) -> str:
        total_days = sum(self.labor_days.values())
        return str(round(total_qty/total_days, 2))


if __name__ == '__main__':
    cargas_maq = calculate_carga_de_maquina()
    NumberOfPiecesTable(None, cargas_de_maq=cargas_maq)
