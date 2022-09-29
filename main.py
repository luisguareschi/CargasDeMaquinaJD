import pandas as pd
from multiprocessing import Process, Queue, freeze_support
from Packages.gui.gui import Gui


class App:
    def __init__(self):
        """Clase principal donse se ejecuta la aplicacion"""
        pd.options.mode.chained_assignment = None  # Para poder editar tablas en pandas mas facil
        freeze_support()
        self.gui = Gui()
        self.gui.create_windows(self.gui)
        while self.gui.app_running:
            self.gui.update()


if __name__ == '__main__':
    app = App()
