import tkinter as tk
from tkinter import ttk
from typing import Callable, Any


class CellPickComboBox(tk.Frame):
    def __init__(self, parent, values: list, command: Callable[[], Any]):
        self.command = command
        tk.Frame.__init__(self, parent)
        empty_selection_text = 'Ninguna Celula Seleccionada'
        self.menubutton = ttk.Menubutton(self, text=empty_selection_text, style='dark-outline',
                                         width=len(empty_selection_text))
        self.menu = tk.Menu(self.menubutton, tearoff=False)
        self.menubutton.configure(menu=self.menu)
        self.menubutton.pack(padx=0, pady=0, expand=False, fill='x')

        self.choices = {}
        self.values = values
        for choice in self.values:
            self.choices[choice] = tk.IntVar(value=0)
            self.menu.add_checkbutton(label=choice, variable=self.choices[choice],
                                 onvalue=1, offvalue=0,
                                 command=self.update_values)

    def update_values(self):
        self.command()
        cells = self.get_selected_options()
        s = ''
        if len(cells) == 1:
            self.menubutton.configure(text=cells[0])
            return
        for cel_n, cell in enumerate(cells):
            if cel_n == 0:
                s = s + f'{cell} |'
            elif cel_n == len(cell):
                s = s + f' {cell}'
            else:
                s = s + f' {cell} |'
        if s == '':
            s = 'Ninguna Celula Seleccionada'
        self.menubutton.configure(text=s)

    def get_selected_options(self) -> list:
        selections = []
        for name, var in self.choices.items():
            if var.get() == 1:
                selections.append(name)
        return selections

    def force_values(self, values=None):
        if values is None and len(self.values) == 1:
            self.choices[self.values[0]].set(1)
            self.update_values()
            return True
        elif values is None:
            return False
        for value in values:
            self.choices[value].set(1)
            self.update_values()
        return False

