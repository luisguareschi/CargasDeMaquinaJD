import tkinter as tk
from tkinter import ttk


class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        self.master = master
        super().__init__(master, **kw)
        self.bind('<Double-1>', self.on_double_click)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        vsb.pack(side=tk.RIGHT, expand=True, fill='y', anchor='e')
        self.configure(yscrollcommand=vsb.set)

    def on_double_click(self, event):
        # Obtener coordenadas
        x, y = event.x, event.y
        # identificar si se hizo click en usa celula
        region_clicked = self.identify_region(x, y)
        if region_clicked != 'cell':
            return
        # identificar celula donde se hizo click
        column = self.identify_column(x)
        column_index = int(column[1:]) - 1
        row = self.identify_row(y)
        selected_iid = self.focus()
        selected_values = self.item(selected_iid)
        selected_text = selected_values.get('values')[column_index]
        # crear entry encima de la celula seleccionada
        column_box = self.bbox(selected_iid, column)
        entry_edit = ttk.Entry(self.master, width=column_box[2])
        entry_edit.place(x=column_box[0], y=column_box[1], width=column_box[2], height=column_box[3])
        entry_edit.insert(tk.END, selected_text)
        entry_edit.select_range(0, tk.END)
        entry_edit.editing_column_index = column_index
        entry_edit.editing_item_iid = selected_iid
        entry_edit.focus()
        entry_edit.bind('<FocusOut>', self.on_focus_out)
        entry_edit.bind('<Escape>', self.on_focus_out)
        entry_edit.bind('<Return>', self.on_enter_pressed)

    def on_focus_out(self, event):
        event.widget.destroy()

    def on_enter_pressed(self, event):
        new_value = event.widget.get()
        iid = event.widget.editing_item_iid
        column_index = event.widget.editing_column_index
        current_values = self.item(iid).get('values')
        current_values[column_index] = new_value
        self.item(iid, values=current_values)
        event.widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    column_names = ['vehicle_type', 'vehicle_name', 'year', 'color']
    tree_view_vehicles = TreeviewEdit(root, columns=column_names, show='headings')
    # agregar encabezados
    for n, name in enumerate(column_names):
        tree_view_vehicles.heading(name, text=name)

    # agregar datos
    for i in range(0, 100):
        tree_view_vehicles.insert(parent='', index=tk.END, values=('Sedan', 'Nissan Versa', '2010', 'Silver'))
        tree_view_vehicles.insert(parent='', index=tk.END, values=('Coupe', 'Toyota Camry', '2022', 'Blue'))
    tree_view_vehicles.place(relx=0, rely=0, relwidth=1, relheight=1)

    root.mainloop()
