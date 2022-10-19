import os.path
import tkinter as tk
from tkinter import ttk

import Packages.gui.gui
from Packages.constants import images_folder


class ToggleMenu(ttk.Frame):
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.parent = parent
        self.gui = gui
        self.configure(bootstyle="primary")
        self.button = ttk.Button(self, text='☰', command=self.open_window, padding=5)
        self.button.grid(row=0, column=0, sticky='news')

    def open_window(self):
        bstyle = 'success'
        self.window = ttk.Frame(self.parent, bootstyle=bstyle)
        self.window.place(relx=0, rely=0, relwidth=.2, relheight=1)
        self.button2 = ttk.Button(self.window, text='☰', command=self.close_window, bootstyle=bstyle, padding=5)
        self.button2.grid(row=0, column=0, sticky='nsw')
        b1 = ttk.Button(self.window, text='Cargas de Maquina', bootstyle=bstyle, command=self.cargas_maquina_clicked)
        b1.grid(row=1, column=0, sticky='we', pady=5)
        b2 = ttk.Button(self.window, text='Ajustes', bootstyle=bstyle, command=self.ajustes_clicked)
        b2.grid(row=2, column=0, sticky='we', pady=5)
        self.window.columnconfigure(0, weight=1)

    def close_window(self):
        self.window.destroy()

    def cargas_maquina_clicked(self):
        self.gui.cargas_maquina_window.tkraise()
        self.gui.cargas_maquina_window.recalculate()
        self.window.destroy()

    def ajustes_clicked(self):
        self.gui.configure_perc_window.tkraise()
        self.window.destroy()

