import tkinter as tk
import ctypes
from Packages.constants import images_folder
import os
from ttkbootstrap import Style

from Packages.gui.CalendarWindow.calendar_window import CalendarWindow
from Packages.gui.ConfigurePercentagesWindow.configure_percentages_window import ConfigurePercentagesWindow
from Packages.gui.toggle_menu import ToggleMenu
from Packages.gui.CargasDeMaquinaWindow.cargas_de_maquina_window import CargasDeMaquinaWindow


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
        self.toggle_menu = ToggleMenu(self.root, self.gui)
        self.toggle_menu.place(relx=0, rely=0, relheight=0.03, relwidth=1)
        self.cargas_maquina_window = CargasDeMaquinaWindow(self.root)
        self.cargas_maquina_window.place(relx=0, rely=0.03, relwidth=1, relheight=1-0.03)
        self.configure_perc_window = ConfigurePercentagesWindow(self.root)
        self.configure_perc_window.place(relx=0, rely=0.03, relwidth=1, relheight=1-0.03)
        self.calendar_window = CalendarWindow(self.root)
        self.calendar_window.place(relx=0, rely=0.03, relwidth=1, relheight=1-0.03)
        self.cargas_maquina_window.tkraise()

    def update(self):
        """Funcion que actualiza la parte visual de la GUI"""
        self.root.update_idletasks()
        self.root.update()

    def close_app(self):
        """Funcion para poder cerrar la aplicacion debidamente"""
        self.app_running = False
        self.root.destroy()




