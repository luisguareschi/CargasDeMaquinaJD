import pandas as pd
from tkinter import ttk
import tkinter as tk
from Packages.calculate_carga_de_maquina import calculate_carga_de_maquina
from Packages.gui.CargasDeMaquinaWindow.sort_date import sort_list_by_date
import datetime as dt


class NumberOfPiecesTable(ttk.Frame):
    def __init__(self, parent, cargas_de_maq):
        super().__init__(parent)
        self.cargas_de_maq = cargas_de_maq
        # Obtener titulos de las columnas
        self.all_dates = set(self.cargas_de_maq['Text Fiscal Month'].to_list())
        self.all_dates = list(self.all_dates)
        self.all_dates = sort_list_by_date(self.all_dates)
        self.headers = ['REFERENCIA', 'HRS STD'] + self.all_dates + ['TOTAL PZS', 'PIEZAS/DIA', 'TOTAL HRS STD']
        # Insertar titulos de columnas en la gui
        col = 0
        for head in self.headers:
            lenght = len(head)
            label = ttk.Label(self, width=int(lenght * 1.5), text=head, bootstyle='inverse-primary', anchor='center')
            label.grid(row=1, column=col, sticky='ew')
            col += 1
        number_of_parts_label = ttk.Label(self, text='NUMERO DE PIEZAS', anchor='center',
                                          bootstyle='inverse-dark')
        number_of_parts_label.grid(row=0, column=2, columnspan=len(self.all_dates), sticky='we')
        # Variables donde se guardan los widgets
        self.reference_entries = {}
        self.hrs_std_entries = {}
        self.number_of_parts_entries = {}
        self.calculate_data()

    def calculate_data(self):
        # Insertar datos
        self.celulas = ['235A']
        self.selected_df: pd.DataFrame = self.cargas_de_maq.loc[(self.cargas_de_maq['Celula'].isin(self.celulas))]
        print(self.selected_df.to_string())
        references = self.selected_df['ReferenciaSAP'].to_list()
        references = set(references)
        references = list(references)
        row_n = 2
        for ref in references:
            # Escribir nombre de referencia
            ref_entry = ttk.Entry(self)
            ref_entry.insert(tk.END, ref)
            ref_entry.configure(state='readonly')
            ref_entry.grid(row=row_n, column=0)
            self.reference_entries[ref] = ref_entry
            hrs_std = self.selected_df.loc[self.selected_df['ReferenciaSAP'] == ref]['HorasSTD'].values[0]
            hrs_std_entry = ttk.Entry(self, width=int(len(str(hrs_std)) * 1.2))
            hrs_std_entry.insert(tk.END, hrs_std)
            hrs_std_entry.configure(state='readonly')
            hrs_std_entry.grid(row=row_n, column=1, sticky='ew')
            self.hrs_std_entries[ref] = hrs_std_entry
            quantities = {}
            for col_n, date in enumerate(self.all_dates):
                qty = self.selected_df.loc[
                    (self.selected_df['ReferenciaSAP'] == ref) & (self.selected_df['Text Fiscal Month'] == date)]
                try:
                    qty = qty['CalculatedQty'][qty.index[0]]
                except:
                    qty = 'N/A'
                qty_entry = ttk.Entry(self, width=int(len(str(qty)) * 1.2))
                qty_entry.insert(tk.END, str(qty))
                qty_entry.configure(state='readonly')
                qty_entry.grid(row=row_n, column=2 + col_n, sticky='ew')
                quantities[date] = qty_entry
            self.number_of_parts_entries[ref] = quantities
            row_n += 1

    def delete_widgets(self):
        for ref in self.reference_entries:
            self.reference_entries[ref].destroy()
            self.hrs_std_entries[ref].destroy()
            dates = self.number_of_parts_entries[ref]
            for date in dates:
                dates[date].destroy()



if __name__ == '__main__':
    cargas_maq = calculate_carga_de_maquina()
    NumberOfPiecesTable(None, cargas_de_maq=cargas_maq)
