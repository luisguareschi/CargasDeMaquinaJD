import tkinter as tk
from tkinter import ttk


class CalendarWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bootstyle='success')