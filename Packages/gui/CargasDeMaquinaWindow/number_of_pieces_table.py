import time

import pandas as pd
from tkinter import ttk
import tkinter as tk
from Packages.calculate_carga_de_maquina import calculate_carga_de_maquina
from Packages.get_labor_days_calendar import get_labor_days_per_month
from Packages.gui.CalendarWindow.get_numero_operarios_celula import get_numero_op
from Packages.gui.CargasDeMaquinaWindow.sort_date import sort_list_by_date
import datetime as dt
from Packages.gui.ScrollableFrame import VerticalScrolledFrame


class NumberOfPiecesTable(ttk.Frame):
    def __init__(self, parent, cargas_de_maq):
        super().__init__(parent)
        self.absentismo = None
        self.n_celula_op = None
        self.n_operarios_celula = None
        self.productividad = None
        self.celula = None
        self.parent = parent
        # Crear frame que puede hacer scroll para colocar la tabla de cantidades adentroç
        self.top_frame = VerticalScrolledFrame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Variables importantes
        self.cargas_de_maq = cargas_de_maq
        # Obtener titulos de las columnas
        self.all_dates = set(self.cargas_de_maq['Text Fiscal Month'].to_list())
        self.all_dates = list(self.all_dates)
        self.all_dates = sort_list_by_date(self.all_dates)
        self.labor_days = get_labor_days_per_month(cell=self.celula, months=self.all_dates)
        self.headers = ['REFERENCIA', 'HRS STD'] + self.all_dates + ['TOTAL PZS', 'PIEZAS/DIA',
                                                                     'TOTAL HRS STD', 'MAX TURNO', 'AVG TURNO']
        # Insertar titulos de columnas en la gui
        col = 0
        for head in self.headers:
            lenght = len(head)
            label = ttk.Label(self.top_frame.interior, width=int(lenght * 1.3), text=head, bootstyle='inverse-primary',
                              anchor='center')
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
        self.total_std_entries = {}
        self.max_turno_entries = {}
        self.avg_turno_entries = {}
        self.monthly_parts_entries = {}
        self.monthly_std_entries = {}
        self.monthly_hrs_necestiadas_entries = {}
        self.monthly_labor_days_entries = {}
        self.monthly_available_hours_entries = {}
        self.monthly_available_op_entries = {}
        self.monthly_needed_operators_entries = {}
        self.yearly_totals_entries = {}

        # Calcular los datos
        self.calculate_data()

    def calculate_data(self):
        """Funcion que dibuja y recalcula todos los elementos visuales de la carga de maquina"""
        # Datos importantes para dibujar la tabla
        self.productividad = 1.05  # <<<<---- HACER CON TABLAS DESPUES (BLADE)
        self.n_operarios_celula = get_numero_op(self.celula)
        self.n_celula_op = 1
        self.absentismo = 0.13  # <<<<---- HACER CON TABLAS DESPUES (BLADE)
        self.labor_days = get_labor_days_per_month(cell=self.celula, months=self.all_dates)
        # Hacer primera tabla
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
            # -----------------------BIDNINGS (WIP)--------------------------
            self.bind_double_click(hrs_std_entry)
            # ----------------------------------------------------------
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
            total_qty_entry.grid(row=row_n, column=3 + col_n, sticky='ew')
            self.total_parts_entries[ref] = total_qty_entry

            # Escribir piezas por dia
            parts_per_day = self.calculate_parts_per_day(total_qty)
            part_per_day_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(parts_per_day)) * 1.2))
            part_per_day_entry.insert(tk.END, str(parts_per_day))
            part_per_day_entry.configure(state='readonly')
            part_per_day_entry.grid(row=row_n, column=4 + col_n, sticky='ew')
            self.parts_per_day_entries[ref] = part_per_day_entry

            # Escribir total Horas STD
            total_std = round((total_qty * hrs_std) / 100, 2)
            total_std_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(total_std)) * 1.2))
            total_std_entry.insert(tk.END, str(total_std))
            total_std_entry.configure(state='readonly')
            total_std_entry.grid(row=row_n, column=5 + col_n, sticky='ew')
            self.total_std_entries[ref] = total_std_entry

            # Escribir total Max Turno
            try:
                max_turno = int(round((8 * 1.42 * 100) / (hrs_std * self.n_celula_op), 0))
            except OverflowError:
                max_turno = 0
            max_turno_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(max_turno)) * 1.2))
            max_turno_entry.insert(tk.END, str(max_turno))
            max_turno_entry.configure(state='readonly')
            max_turno_entry.grid(row=row_n, column=6 + col_n, sticky='ew')
            self.max_turno_entries[ref] = max_turno_entry

            # Escribir total Avg Turno
            avg_turno = int(round(max_turno / self.productividad, 0))
            avg_turno_entry = ttk.Entry(self.top_frame.interior, width=int(len(str(avg_turno)) * 1.2))
            avg_turno_entry.insert(tk.END, str(avg_turno))
            avg_turno_entry.configure(state='readonly')
            avg_turno_entry.grid(row=row_n, column=7 + col_n, sticky='ew')
            self.avg_turno_entries[ref] = avg_turno_entry
            # Sumar una fila
            row_n += 1

        # Hacer segunda tabla con los otros datos
        # Propiedades de la 2da tabla
        self.table2_frame = ttk.Frame(self.parent)
        self.table2_frame.place(relx=0, rely=0.52, relwidth=.75, relheight=1 - 0.52)
        column_names = ['TOTAL PIEZAS', 'HRS STD', 'HRS NEC. PEDIDOS', 'DIAS HABILES', 'HRS DISPONIBLES',
                        'Nº OP. ACTUALES', 'Nº OP. NECESARIOS']

        for col_n, date in enumerate(self.all_dates + ['TOTAL']):
            lenght = len(date)
            label = ttk.Label(self.table2_frame, width=int(lenght * 1.3), text=date, bootstyle='inverse-primary',
                              anchor='center')
            label.grid(row=0, column=col_n + 1, sticky='ewns')
        for row_n, column_name in enumerate(column_names):
            lenght = len(column_name)
            label = ttk.Label(self.table2_frame, width=32, text=column_name, bootstyle='inverse-primary',
                              anchor='center')
            label.grid(row=row_n + 1, column=0, sticky='ewns')
            for col_n, date in enumerate(self.labor_days):
                fiscal_month = self.all_dates[col_n]
                if column_name == 'TOTAL PIEZAS':
                    monthly_qty = str(self.get_monthly_qty(fiscal_month))
                    entry = ttk.Entry(self.table2_frame, width=int(len(monthly_qty) * 1.2))
                    entry.insert(tk.END, monthly_qty)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_parts_entries[fiscal_month] = entry
                elif column_name == 'HRS STD':  # Calcular hrs std por mes
                    monthly_std = str(self.get_monthly_std(fiscal_month))
                    entry = ttk.Entry(self.table2_frame, width=int(len(monthly_std) * 1.2))
                    entry.insert(tk.END, monthly_std)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_std_entries[fiscal_month] = entry
                elif column_name == 'HRS NEC. PEDIDOS':  # Calcular hrs std por mes tomando en cuenta la prod.
                    monthly_std_necesario = str(round(self.get_monthly_std(fiscal_month) / self.productividad, 2))
                    entry = ttk.Entry(self.table2_frame, width=int(len(monthly_std_necesario) * 1.2))
                    entry.insert(tk.END, monthly_std_necesario)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_hrs_necestiadas_entries[fiscal_month] = entry
                elif column_name == 'DIAS HABILES':
                    labor_days = str(self.labor_days[date])
                    entry = ttk.Entry(self.table2_frame, width=int(len(labor_days) * 1.2))
                    entry.insert(tk.END, labor_days)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_labor_days_entries[fiscal_month] = entry
                elif column_name == 'HRS DISPONIBLES':
                    hrs_disp = str(round(
                        (self.n_operarios_celula * self.labor_days[date] * 8) / (1 + self.absentismo) * (
                                1 / self.n_celula_op), 2))
                    entry = ttk.Entry(self.table2_frame, width=int(len(hrs_disp) * 1.2))
                    entry.insert(tk.END, hrs_disp)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_available_hours_entries[fiscal_month] = entry
                elif column_name == 'Nº OP. ACTUALES':
                    n_op_actuales = str(self.n_operarios_celula)
                    entry = ttk.Entry(self.table2_frame, width=int(len(n_op_actuales) * 1.2))
                    entry.insert(tk.END, n_op_actuales)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_available_op_entries[fiscal_month] = entry
                elif column_name == 'Nº OP. NECESARIOS':
                    n_op_necesitados = str(
                        round(float(monthly_std_necesario) / (8 * self.labor_days[date] * (1 - self.absentismo)), 2))
                    entry = ttk.Entry(self.table2_frame, width=int(len(n_op_necesitados) * 1.2))
                    entry.insert(tk.END, n_op_necesitados)
                    entry.configure(state='readonly')
                    entry.grid(row=row_n + 1, column=1 + col_n, sticky='ew')
                    self.monthly_needed_operators_entries[fiscal_month] = entry

        for row_n, column_name in enumerate(column_names):
            last_col = 1 + len(self.labor_days)
            if column_name == 'TOTAL PIEZAS':
                q = str(self.get_yearly_total(self.monthly_parts_entries))
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'HRS STD':
                q = str(self.get_yearly_total(self.monthly_std_entries))
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'HRS NEC. PEDIDOS':
                q = str(self.get_yearly_total(self.monthly_hrs_necestiadas_entries))
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'DIAS HABILES':
                q = str(self.get_yearly_total(self.monthly_labor_days_entries))
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'HRS DISPONIBLES':
                q = str(self.get_yearly_total(self.monthly_available_hours_entries))
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'Nº OP. ACTUALES':
                q = str(self.n_operarios_celula)
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry
            elif column_name == 'Nº OP. NECESARIOS':
                q = str(self.calculate_needed_op())
                total_entry = ttk.Entry(self.table2_frame, width=int(len(q) * 1.2))
                total_entry.insert(tk.END, q)
                total_entry.configure(state='readonly')
                total_entry.grid(row=row_n + 1, column=last_col, sticky='ew')
                self.yearly_totals_entries[column_name] = total_entry

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
            total_std_entry: ttk.Entry = self.total_std_entries[ref]
            total_std_entry.grid_forget()
            max_turno: ttk.Entry = self.max_turno_entries[ref]
            max_turno.grid_forget()
            avg_turno: ttk.Entry = self.avg_turno_entries[ref]
            avg_turno.grid_forget()

        for fiscal_month in self.monthly_parts_entries:
            self.monthly_parts_entries[fiscal_month].grid_forget()
            self.monthly_std_entries[fiscal_month].grid_forget()
            self.monthly_hrs_necestiadas_entries[fiscal_month].grid_forget()
            self.monthly_labor_days_entries[fiscal_month].grid_forget()
            self.monthly_available_hours_entries[fiscal_month].grid_forget()
            self.monthly_available_op_entries[fiscal_month].grid_forget()
            self.monthly_needed_operators_entries[fiscal_month].grid_forget()

        for column_name in self.yearly_totals_entries:
            self.yearly_totals_entries[column_name].grid_forget()

        self.empty_entry_dicts()

    def empty_entry_dicts(self):
        self.reference_entries = {}
        self.hrs_std_entries = {}
        self.number_of_parts_entries = {}
        self.total_parts_entries = {}
        self.parts_per_day_entries = {}
        self.total_std_entries = {}
        self.max_turno_entries = {}
        self.avg_turno_entries = {}
        self.monthly_parts_entries = {}
        self.monthly_std_entries = {}
        self.monthly_hrs_necestiadas_entries = {}
        self.monthly_labor_days_entries = {}
        self.monthly_available_hours_entries = {}
        self.monthly_available_op_entries = {}
        self.monthly_needed_operators_entries = {}
        self.yearly_totals_entries = {}

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
        return str(round(total_qty / total_days, 2))

    def on_double_click(self, event):
        entry: ttk.Entry = event.widget
        entry.configure(state='default')
        entry.select_range(0, tk.END)

    def on_focus_out(self, event):
        entry: ttk.Entry = event.widget
        entry.delete(0, tk.END)
        entry.insert(tk.END, entry.previous_val)
        entry.configure(state='readonly')

    def on_enter(self, event):
        entry: ttk.Entry = event.widget
        entry.configure(state='readonly', bootstyle='danger')
        entry.previous_val = entry.get()

    def bind_double_click(self, entry: ttk.Entry):
        entry.previous_val = entry.get()
        entry.bind('<Double-1>', self.on_double_click)
        entry.bind('<FocusOut>', self.on_focus_out)
        entry.bind('<Escape>', self.on_focus_out)
        entry.bind('<Return>', self.on_enter)

    def get_monthly_std(self, date):
        monthly_std = 0
        for ref in self.hrs_std_entries:
            std_entry: ttk.Entry = self.hrs_std_entries[ref]
            std = float(std_entry.get())
            qty = self.number_of_parts_entries[ref][date].get()
            if qty == 'N/A':
                continue
            monthly_std = monthly_std + int(qty) * std

        return round(monthly_std / 100, 2)

    def get_monthly_qty(self, date):
        monthly_qty = 0
        for ref in self.number_of_parts_entries:
            qty = self.number_of_parts_entries[ref][date].get()
            if qty == 'N/A':
                continue
            monthly_qty = monthly_qty + int(qty)

        return monthly_qty

    def get_yearly_total(self, entries_dict):
        total = 0
        for fiscal_month in entries_dict:
            qty = entries_dict[fiscal_month].get()
            try:
                qty = float(qty)
            except ValueError:
                continue
            total = total + qty
        print()
        if int(total) == float(total):
            return int(total)
        return round(total, 2)

    def calculate_needed_op(self):
        total_hrs_nec = self.get_yearly_total(self.monthly_hrs_necestiadas_entries)
        total_labor_days = self.get_yearly_total(self.monthly_labor_days_entries)
        result = total_hrs_nec / ((1 - self.absentismo) * 8 * total_labor_days)
        return round(result, 2)


if __name__ == '__main__':
    cargas_maq = calculate_carga_de_maquina()
    NumberOfPiecesTable(None, cargas_de_maq=cargas_maq)
