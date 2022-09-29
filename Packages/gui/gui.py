import tkinter as tk
from tkinter import ttk
import ctypes
from Packages.constants import images_folder
import os
from ttkbootstrap import Style


class Gui:
    def __init__(self):
        """Ajustes iniciales de la app"""
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Aumenta la resolucion de la interfaz
        self.app_running = True
        self.root = tk.Tk()
        self.root.title('Cargas de Maquina JD')
        self.root.iconbitmap(os.path.join(images_folder, 'application.ico'))
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        style = Style(theme='flatly')
        self.root.resizable(True, True)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = screen_width
        window_height = screen_height
        self.root.state('zoomed')
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width,
                                                window_height, x_cordinate,
                                                y_cordinate))
        self.gui = None

    def create_windows(self, gui):
        """Funcion donde se crean las ventanas"""
        self.gui = gui

    def update(self):
        """Funcion que actualiza la parte visual de la GUI"""
        self.root.update_idletasks()
        self.root.update()

    def close_app(self):
        """Funcion para poder cerrar la aplicacion debidamente"""
        self.app_running = False
        self.root.destroy()




