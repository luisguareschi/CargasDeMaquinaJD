import os.path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Packages.gui.ConfigurePercentagesWindow.configure_percentages_table import ConfigurePercentagesTable
from Packages.constants import resources_folder, downloads_folder


class ConfigurePercentagesWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.table = ConfigurePercentagesTable(self)
        # self.table.pack(expand=True, fill='both')
        self.table.place(relx=0, rely=0, relheight=1, relwidth=.8)
        self.master_table = self.table.master_table
        references = set(self.master_table['ReferenciaSAP'].tolist())
        references = list(references)
        references.sort()
        references.append('Ver todos')
        tipos_de_op = set(self.master_table['Tipo de Operacion'].tolist())
        tipos_de_op = list(tipos_de_op)
        tipos_de_op.sort()
        tipos_de_op.append('Ver todos')
        # -----------------------Filtros-----------------------
        self.filter_frame = ttk.Labelframe(self, text='Ajustes de Filtros', padding=10)
        self.filter_frame.place(relx=.81, rely=0, relheight=.15)
        label1 = ttk.Label(self.filter_frame, text='Referencia: ')
        label1.grid(row=0, column=0)
        self.reference_filter = ttk.Combobox(self.filter_frame, values=references)
        self.reference_filter.bind("<<ComboboxSelected>>", self.filter_selected)
        self.reference_filter.bind('<KeyRelease>', lambda e, lst=references: self.filter_combobox(e, lst))
        self.reference_filter.grid(row=0, column=1)
        label2 = ttk.Label(self.filter_frame, text='Tipo de Operacion: ')
        label2.grid(row=1, column=0)
        self.op_type_filter = ttk.Combobox(self.filter_frame, values=tipos_de_op)
        self.op_type_filter.bind("<<ComboboxSelected>>", self.filter_selected)
        self.op_type_filter.bind('<KeyRelease>', lambda e, lst=tipos_de_op: self.filter_combobox(e, lst))
        self.op_type_filter.grid(row=1, column=1)
        # -----------------------Ajustes-----------------------
        self.settings_frame = ttk.Labelframe(self, text='Ajustes', padding=10)
        self.settings_frame.place(relx=.81, rely=.16)
        save_button = ttk.Button(self.settings_frame, text='Guardar Ajustes',
                                 command=lambda: [self.save_clicked()])
        save_button.grid(row=0, column=0, padx=5)
        import_button = ttk.Button(self.settings_frame, text='Importar Ajustes',
                                   command=lambda: [self.import_clicked()])
        import_button.grid(row=0, column=1, padx=5)
        export_button = ttk.Button(self.settings_frame, text='Exportar Ajustes',
                                   command=lambda: [self.export_clicked()])
        export_button.grid(row=1, column=0, padx=5, pady=5)
        # -----------------------importar tabla----------------
        self.table.import_settings(file_path=os.path.join(resources_folder, 'master_configuration_table.xlsx'))

    def filter_selected(self, event=None):
        reference = self.reference_filter.get()
        op_type = self.op_type_filter.get()
        if reference == 'Ver todos' or reference == '':
            reference = None
        if op_type == 'Ver todos' or op_type == '':
            op_type = None
        self.table.filter()  # Limpiar filtros anteriores primero
        self.table.filter(reference=reference, op_type=op_type)

    def filter_combobox(self, event, lst):
        value = event.widget.get()
        if value == '':
            event.widget['values'] = lst
            event.widget['bootstyle'] = 'default'
            cb: ttk.Combobox = event.widget
            self.filter_selected()
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
                        self.filter_selected()
                        return
            event.widget['values'] = data
            if not data:
                event.widget['bootstyle'] = 'danger'
            else:
                event.widget['bootstyle'] = 'default'

    def save_clicked(self):
        question = messagebox.askyesno(title='Guardar cambios',
                                       message='Estas seguro que quieres guardar los ajustes actuales? '
                                               '\nEsta accion no se puede revertir.')
        if question:
            self.table.save_settings(destination_folder=resources_folder)
            messagebox.showinfo(title='Cambios Guardados', message='Cambios guardados de manera exitosa.')

    def import_clicked(self):
        file_path = filedialog.askopenfilename(title='Importar ajustes', initialdir=downloads_folder,
                                                filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.table.import_settings(file_path)
            messagebox.showinfo(title='Ajustes Importados', message='Ajustes importados exitosamente.')

    def export_clicked(self):
        destination_folder = filedialog.askdirectory(initialdir=downloads_folder)
        if destination_folder:
            self.table.save_settings(destination_folder)
            messagebox.showinfo(title='Ajustes Exportados', message='Ajustes exportados exitosamente.')
