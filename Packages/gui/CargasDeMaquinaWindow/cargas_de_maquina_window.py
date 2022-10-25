import datetime
import os.path
import tkinter as tk
from tkinter import ttk

import pandas as pd

from Packages.calculate_carga_de_maquina import calculate_carga_de_maquina
from Packages.get_orders_table import get_orders_table
from Packages.constants import resources_folder
from Packages.gui.CargasDeMaquinaWindow.number_of_pieces_table import NumberOfPiecesTable


class CargasDeMaquinaWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bootstyle='default')
        self.cargas_maq = calculate_carga_de_maquina()
        self.number_of_pieces_table = NumberOfPiecesTable(self, cargas_de_maq=self.cargas_maq)
        self.number_of_pieces_table.place(relx=0, rely=0, relwidth=.75, relheight=0.5)
        # ------------------------Filtros------------------------
        self.filters_frame = ttk.Labelframe(self, text='Filtros', padding=10)
        self.filters_frame.place(relx=.8, rely=0)
        ttk.Label(self.filters_frame, text='Celula:').grid(row=0, column=0, sticky='w')
        self.cells = set(self.cargas_maq['Celula'].to_list())
        self.cells = list(self.cells)
        self.cells.sort()
        self.cell_filter = ttk.Combobox(self.filters_frame, values=self.cells)
        self.cell_filter.bind("<<ComboboxSelected>>", self.cell_filter_selected)
        self.cell_filter.bind('<KeyRelease>', lambda e, lst=self.cells: self.filter_combobox(e, lst))
        self.cell_filter.grid(row=0, column=1, sticky='ew')
        self.cell_filter.set('235A')
        self.cell_filter_selected()

    def recalculate(self):
        self.number_of_pieces_table.cargas_de_maq = calculate_carga_de_maquina()
        self.number_of_pieces_table.delete_widgets()
        self.number_of_pieces_table.calculate_data()

    def filter_combobox(self, event, lst):
        value = event.widget.get()
        if value == '':
            event.widget['values'] = lst
            event.widget['bootstyle'] = 'default'
            cb: ttk.Combobox = event.widget
            self.cell_filter_selected()
            return
        else:
            data = []
            for item in lst:
                if value.lower() in item.lower():
                    data.append(item)
                    if value.upper() == item.upper():
                        cb: ttk.Combobox = event.widget
                        cb.set(item)
                        event.widget['bootstyle'] = 'default'
                        self.cell_filter_selected()
                        return
            event.widget['values'] = data
            if not data:
                event.widget['bootstyle'] = 'danger'
            else:
                event.widget['bootstyle'] = 'default'

    def cell_filter_selected(self, event=None):
        selected_cell = str(self.cell_filter.get())
        self.number_of_pieces_table.celula = selected_cell
        self.number_of_pieces_table.delete_widgets()
        self.number_of_pieces_table.calculate_data()