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
        self.number_of_pieces_table.place(relx=0, rely=0)

    def recalculate(self):
        self.number_of_pieces_table.delete_widgets()
        self.number_of_pieces_table.calculate_data()
