import os.path
import tkinter as tk
from tkinter import ttk
import pandas as pd
from Packages.get_master_table import get_master_table
from Packages.gui.ConfigurePercentagesWindow.cell_picker_combobox import CellPickComboBox
from Packages.gui.ScrollableFrame import VerticalScrolledFrame
from Packages.constants import resources_folder


class ConfigurePercentagesTable(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.changes_made = False
        # -----------------canvas for scrolling--------------
        self.inner_frame = VerticalScrolledFrame(self)
        self.inner_frame.pack(expand=True, fill='both')
        # -----------------Set headers-----------------------
        headers = ['Referencia', 'Tipo de Operacion', 'Celulas', 'Porcentaje de Pedidos']
        for col_n, head in enumerate(headers):
            if head == headers[-1]:
                ttk.Label(self.inner_frame.interior, text=head).grid(row=0, column=col_n, columnspan=10)
                continue
            ttk.Label(self.inner_frame.interior, text=head).grid(row=0, column=col_n)
        # -----------------Get values------------------------
        self.master_table = get_master_table()
        self.draw_table()

    def action(self, row_n, reference, op_type):
        cb = self.widgets_info[reference][op_type]['combobox']
        selected_cells = cb.get_selected_options()
        recent_values = {}
        # Clean selection before drawing
        try:
            for cell in self.widgets_info[reference][op_type]['labels']:
                label: ttk.Label = self.widgets_info[reference][op_type]['labels'][cell]
                entry: ttk.Entry = self.widgets_info[reference][op_type]['entries'][cell]
                recent_values[cell] = entry.get()
                label.destroy()
                entry.destroy()
        except KeyError:
            pass
        # Draw selected cells
        init_column = 3
        labels_info = {}
        entries_info = {}
        for cell in selected_cells:
            label = ttk.Label(self.inner_frame.interior, text=f'{cell}: ')
            label.grid(row=row_n, column=init_column, padx=5, sticky='w')
            val = ttk.Entry(self.inner_frame.interior)
            val.grid(row=row_n, column=init_column + 1)
            try:
                if recent_values[cell] not in (1, '1'):
                    val.insert(0, recent_values[cell])
            except KeyError:
                pass
            # Store values
            labels_info[cell] = label
            entries_info[cell] = val
            init_column += 2
        self.widgets_info[reference][op_type]['labels'] = labels_info
        self.widgets_info[reference][op_type]['entries'] = entries_info

    def draw_table(self):
        references = set(self.master_table['ReferenciaSAP'].tolist())
        references = list(references)
        references.sort()
        row_n = 1
        self.widgets_info = {}
        """Hierarchy: reference 
            --reference--> 
                op_type 
                    --op_type--> 
                        combobox, labels, entries, ref_title, op_type_entry 
                            --labels-->
                                celula
                            --entries-->
                                celula"""
        for reference in references:
            reference_info = {}
            ref_df = self.master_table.loc[self.master_table['ReferenciaSAP'] == reference]
            operation_types = ref_df['Tipo de Operacion'].tolist()
            operation_types = set(operation_types)
            operation_types = list(operation_types)
            for operation_type in operation_types:
                op_type_info = {}
                filtered_df = ref_df.loc[ref_df['Tipo de Operacion'] == operation_type]
                celulas_disp = filtered_df['Celula'].tolist()
                # print(reference, operation_type, celulas_disp)
                # Mostrar referencia
                ref_entry = ttk.Entry(self.inner_frame.interior)
                ref_entry.grid(row=row_n, column=0)
                ref_entry.insert(0, reference)
                ref_entry.config(state='readonly')
                # Mostrar Tipo de operacion
                op_type_entry = ttk.Entry(self.inner_frame.interior)
                op_type_entry.grid(row=row_n, column=1)
                op_type_entry.insert(0, operation_type)
                op_type_entry.config(state='readonly')
                # Mostrar celulas
                cell_combobox = CellPickComboBox(self.inner_frame.interior, values=celulas_disp,
                                                 command=lambda n=row_n, ref=reference, op_type=operation_type:
                                                 [self.action(n, ref, op_type)])
                cell_combobox.grid(row=row_n, column=2, sticky='ew')
                op_type_info['combobox'] = cell_combobox
                op_type_info['ref_entry'] = ref_entry
                op_type_info['op_type_entry'] = op_type_entry
                row_n += 1
                # Store values
                reference_info[f'{operation_type}'] = op_type_info
            self.widgets_info[f'{reference}'] = reference_info
            # break
        # AutoSelect the cell in the combobox if there is only one option
        for ref in self.widgets_info:
            for op_t in self.widgets_info[ref]:
                cb: CellPickComboBox = self.widgets_info[ref][op_t]['combobox']
                set_default_value = cb.force_values()
                if set_default_value:
                    for cell in self.widgets_info[ref][op_t]['entries']:
                        entry: ttk.Entry = self.widgets_info[ref][op_t]['entries'][cell]
                        entry.insert(0, '1')
        # pretty(self.widgets_info)

    def filter(self, reference=None, op_type=None):
        if reference is None and op_type is None:
            for ref in self.widgets_info:
                for op_t in self.widgets_info[ref]:
                    cb: CellPickComboBox = self.widgets_info[ref][op_t]['combobox']
                    ref_entry: ttk.Entry = self.widgets_info[ref][op_t]['ref_entry']
                    op_type_entry: ttk.Entry = self.widgets_info[ref][op_t]['op_type_entry']
                    cb.grid(), ref_entry.grid(), op_type_entry.grid()
                    try:
                        for cell in self.widgets_info[ref][op_t]['labels']:
                            label: ttk.Label = self.widgets_info[ref][op_t]['labels'][cell]
                            entry: ttk.Entry = self.widgets_info[ref][op_t]['entries'][cell]
                            label.grid(), entry.grid()
                    except KeyError:
                        pass

        if reference and op_type:
            for ref in self.widgets_info:
                for op_t in self.widgets_info[ref]:
                    if op_t != op_type or ref != reference:
                        cb: CellPickComboBox = self.widgets_info[ref][op_t]['combobox']
                        ref_entry: ttk.Entry = self.widgets_info[ref][op_t]['ref_entry']
                        op_type_entry: ttk.Entry = self.widgets_info[ref][op_t]['op_type_entry']
                        cb.grid_remove(), ref_entry.grid_remove(), op_type_entry.grid_remove()
                        try:
                            for cell in self.widgets_info[ref][op_t]['labels']:
                                label: ttk.Label = self.widgets_info[ref][op_t]['labels'][cell]
                                entry: ttk.Entry = self.widgets_info[ref][op_t]['entries'][cell]
                                label.grid_remove(), entry.grid_remove()
                        except KeyError:
                            pass

        elif reference:  # Si se filtra por referencia
            for ref in self.widgets_info:
                if ref != reference:
                    for op_t in self.widgets_info[ref]:
                        cb: CellPickComboBox = self.widgets_info[ref][op_t]['combobox']
                        ref_entry: ttk.Entry = self.widgets_info[ref][op_t]['ref_entry']
                        op_type_entry: ttk.Entry = self.widgets_info[ref][op_t]['op_type_entry']
                        cb.grid_remove(), ref_entry.grid_remove(), op_type_entry.grid_remove()
                        try:
                            for cell in self.widgets_info[ref][op_t]['labels']:
                                label: ttk.Label = self.widgets_info[ref][op_t]['labels'][cell]
                                entry: ttk.Entry = self.widgets_info[ref][op_t]['entries'][cell]
                                label.grid_remove(), entry.grid_remove()
                        except KeyError:
                            pass

        elif op_type:  # Si se filtra por tipo de operacion
            for ref in self.widgets_info:
                for op_t in self.widgets_info[ref]:
                    if op_t != op_type:
                        cb: CellPickComboBox = self.widgets_info[ref][op_t]['combobox']
                        ref_entry: ttk.Entry = self.widgets_info[ref][op_t]['ref_entry']
                        op_type_entry: ttk.Entry = self.widgets_info[ref][op_t]['op_type_entry']
                        cb.grid_remove(), ref_entry.grid_remove(), op_type_entry.grid_remove()
                        try:
                            for cell in self.widgets_info[ref][op_t]['labels']:
                                label: ttk.Label = self.widgets_info[ref][op_t]['labels'][cell]
                                entry: ttk.Entry = self.widgets_info[ref][op_t]['entries'][cell]
                                label.grid_remove(), entry.grid_remove()
                        except KeyError:
                            pass

    def save_settings(self, destination_folder: str = None):
        for ref in self.widgets_info:
            for op_type in self.widgets_info[ref]:
                combobox: CellPickComboBox = self.widgets_info[ref][op_type]['combobox']
                ref_entry: ttk.Entry = self.widgets_info[ref][op_type]['ref_entry']
                op_type_entry: ttk.Entry = self.widgets_info[ref][op_type]['op_type_entry']
                try:
                    for cell in self.widgets_info[ref][op_type]['labels']:
                        label: ttk.Label = self.widgets_info[ref][op_type]['labels'][cell]
                        entry: ttk.Entry = self.widgets_info[ref][op_type]['entries'][cell]
                        referencia = ref_entry.get()
                        celula = cell
                        operation_type = op_type_entry.get()
                        porcentaje = entry.get()
                        # print(f'{referencia}|{celula}|{operation_type}|{porcentaje}')
                        # USAR ESTOS DATOS PARA GUARDAR LOS AJUSTES EN EL DATAFRAME <<<<<--------
                        self.master_table.loc[
                            (self.master_table['ReferenciaSAP'] == referencia) &
                            (self.master_table['Celula'] == celula) &
                            (self.master_table['Tipo de Operacion'] == operation_type),
                            'Porcentaje de Pedidos'] = float(porcentaje)
                        # print(row)
                except KeyError:
                    pass
        if destination_folder is not None:
            save_file_path = os.path.join(destination_folder, 'master_configuration_table.xlsx')
            self.master_table.to_excel(save_file_path, index=False)
        self.changes_made = True

    def import_settings(self, file_path: str):
        data = pd.read_excel(file_path)
        imported_master_table = pd.DataFrame(data=data)
        for index in imported_master_table.index:
            referencia = imported_master_table['ReferenciaSAP'][index]
            celula = imported_master_table['Celula'][index]
            op_type = imported_master_table['Tipo de Operacion'][index]
            porcentaje = imported_master_table['Porcentaje de Pedidos'][index]
            filtered_row: pd.DataFrame = imported_master_table.loc[
                (imported_master_table['ReferenciaSAP'] == referencia) &
                (imported_master_table['Tipo de Operacion'] == op_type) &
                (imported_master_table['Porcentaje de Pedidos'] != 0)
                ]
            selected_cells = set(filtered_row['Celula'].tolist())
            selected_cells = list(selected_cells)
            if porcentaje == 0:
                continue
            combobox: CellPickComboBox = self.widgets_info[referencia][op_type]['combobox']
            combobox.force_values([celula])
            perc_entry: ttk.Entry = self.widgets_info[referencia][op_type]['entries'][celula]
            if perc_entry.get() != '':
                perc_entry.delete(0, tk.END)
            perc_entry.insert(0, str(porcentaje))


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


if __name__ == '__main__':
    pass
