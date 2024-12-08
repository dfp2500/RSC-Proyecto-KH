import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import csv
from tkinter.font import Font


class InteractionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Interacciones")
        self.root.geometry("600x600")

        # Establecer el icono usando un archivo .ico
        self.root.iconbitmap(r"D:\Clase\RSC\P4\Kingdom_Hearts_logo.ico")

        # Estilo global para aumentar la letra y ajustar la altura de las filas
        style = ttk.Style()
        style.configure('.', font=('KHMenu', 14))  # Cambia el tamaño de la fuente global
        style.configure('Treeview.Heading', font=('KHMenu', 14))  # Tamaño y estilo de encabezados

        self.relationships = []
        self.is_saved = True  # Variable que indica si los cambios han sido guardados

        # Frame para los controles de entrada
        self.input_frame = ttk.Frame(root, padding=10)
        self.input_frame.pack(fill=X, padx=10, pady=10)

        self.input_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        self.input_frame.grid_columnconfigure(4, weight=1, uniform="equal")

        ttk.Label(self.input_frame, text="Personaje 1:", bootstyle="light").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.personaje1_entry = ttk.Entry(self.input_frame)
        self.personaje1_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W + E)

        ttk.Label(self.input_frame, text="Personaje 2:", bootstyle="light").grid(row=0, column=3, padx=5, pady=5, sticky=W)
        self.personaje2_entry = ttk.Entry(self.input_frame)
        self.personaje2_entry.grid(row=0, column=4, padx=5, pady=5, sticky=W + E)

        self.add_button = ttk.Button(self.input_frame, text="Agregar Relación", bootstyle="success-outline", command=self.add_relationship)
        self.add_button.grid(row=1, column=2, pady=10)

        # Campo para personajes de una escena
        ttk.Label(self.input_frame, text="Personajes de la escena (separados por comas):", bootstyle="light").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        self.scene_entry = ttk.Entry(self.input_frame)
        self.scene_entry.grid(row=3, column=0, columnspan=5, padx=5, pady=5, sticky=W + E)

        self.update_button = ttk.Button(self.input_frame, text="Actualizar Relaciones", bootstyle="info-outline", command=self.update_scene_relationships)
        self.update_button.grid(row=4, column=2, pady=10)

        # Campo de búsqueda
        ttk.Label(self.input_frame, text="Buscar:", bootstyle="light").grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.search_entry = ttk.Entry(self.input_frame)
        self.search_entry.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=W + E)
        self.search_entry.bind("<KeyRelease>", self.filter_table)  # Actualizar tabla al escribir

        # Frame para los botones + y -
        buttons_frame = ttk.Frame(self.input_frame)
        buttons_frame.grid(row=5, column=3, columnspan=2, padx=5, pady=5)

        self.increment_button = ttk.Button(buttons_frame, text="+", bootstyle="primary-outline", command=lambda: self.update_interactions(1))
        self.increment_button.pack(side="left", padx=2)

        self.decrement_button = ttk.Button(buttons_frame, text="-", bootstyle="danger-outline", command=lambda: self.update_interactions(-1))
        self.decrement_button.pack(side="left", padx=2)

        # Frame para los botones eliminar
        delete_frame = ttk.Frame(self.input_frame)
        delete_frame.grid(row=6, column=2, pady=10)

        self.delete_button = ttk.Button(delete_frame, text="Eliminar Seleccionados", bootstyle="danger", command=self.delete_selected_rows)
        self.delete_button.pack()

        # Frame para la lista de relaciones
        self.list_frame = ttk.Frame(root, padding=10)
        self.list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.relationship_list = ttk.Treeview(
            self.list_frame, columns=("Personaje 1", "Personaje 2", "Interacciones"), show="headings", bootstyle="info", selectmode="extended"
        )
        self.relationship_list.heading("Personaje 1", text="Personaje 1", anchor=CENTER)
        self.relationship_list.heading("Personaje 2", text="Personaje 2", anchor=CENTER)
        self.relationship_list.heading("Interacciones", text="Interacciones", anchor=CENTER)

        self.relationship_list.column("Personaje 1", anchor=CENTER, width=150)
        self.relationship_list.column("Personaje 2", anchor=CENTER, width=150)
        self.relationship_list.column("Interacciones", anchor=CENTER, width=100)

        # Se ajusta la altura de las filas al modificar el tamaño de la fuente
        style.configure("Treeview", font=('KHMenu', 8))  # Intentamos modificar la altura de las filas

        self.relationship_list.bind("<<TreeviewSelect>>", self.on_select)
        self.relationship_list.pack(fill=BOTH, expand=True, pady=5)

        # Frame para los botones CSV
        csv_frame = ttk.Frame(root, padding=10)
        csv_frame.pack(fill=X, padx=10, pady=10)

        self.save_button = ttk.Button(csv_frame, text="Guardar CSV", bootstyle="success", command=self.save_to_csv)
        self.save_button.pack(side="left", padx=5)

        self.load_button = ttk.Button(csv_frame, text="Cargar CSV", bootstyle="info", command=self.load_from_csv)
        self.load_button.pack(side="left", padx=5)

        # Bind de la tecla Enter para agregar una relación
        self.personaje2_entry.bind("<Return>", self.add_relationship)

        # Bind para confirmar el cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_lines(self, rows):
        lines = 1
        for row in rows:
            for cell in row:
                if cell.count('\n') >= lines:
                    lines = cell.count('\n') + 1
        return lines

    def add_relationship(self, event=None):
        personaje1 = self.personaje1_entry.get().strip()
        personaje2 = self.personaje2_entry.get().strip()

        if personaje1 and personaje2:
            if self.is_duplicate(personaje1, personaje2):
                messagebox.showwarning("Advertencia", "La relación ya existe.")
            else:
                relation = {"personaje1": personaje1, "personaje2": personaje2, "interacciones": 1}
                self.relationships.append(relation)
                self.update_table()
                self.personaje2_entry.delete(0, ttk.END)  # Limpiar solo Personaje 2 para agregar otro
                self.is_saved = False  # Indicamos que no se ha guardado

        else:
            messagebox.showwarning("Advertencia", "Por favor, ingrese ambos personajes.")

    def is_duplicate(self, personaje1, personaje2):
        for relation in self.relationships:
            if (
                (relation["personaje1"] == personaje1 and relation["personaje2"] == personaje2) or
                (relation["personaje1"] == personaje2 and relation["personaje2"] == personaje1)
            ):
                return True
        return False

    def on_select(self, event):
        # Selección múltiple
        selected = self.relationship_list.selection()
        self.selected_relations = []
        for item in selected:
            values = self.relationship_list.item(item, "values")
            for relation in self.relationships:
                if relation["personaje1"] == values[0] and relation["personaje2"] == values[1]:
                    self.selected_relations.append(relation)
                    break

    def update_interactions(self, delta):
        if self.selected_relations:
            for relation in self.selected_relations:
                relation["interacciones"] += delta
                if relation["interacciones"] < 0:
                    relation["interacciones"] = 0
            self.update_table()
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione al menos una relación para modificar.")

    def delete_selected_rows(self):
        selected = self.relationship_list.selection()
        if selected:
            for item in selected:
                values = self.relationship_list.item(item, "values")
                self.relationships = [
                    relation for relation in self.relationships if not (relation["personaje1"] == values[0] and relation["personaje2"] == values[1])
                ]
            self.update_table()

    def update_scene_relationships(self):
        scene_characters = self.scene_entry.get().strip().split(",")
        scene_characters = [char.strip() for char in scene_characters if char.strip()]

        if len(scene_characters) < 2:
            messagebox.showwarning("Advertencia", "Debe haber al menos dos personajes en la escena.")
            return

        # Actualizar las relaciones entre los personajes de la escena
        for i in range(len(scene_characters)):
            for j in range(i + 1, len(scene_characters)):
                personaje1 = scene_characters[i]
                personaje2 = scene_characters[j]
                found = False
                for relation in self.relationships:
                    if (
                        (relation["personaje1"] == personaje1 and relation["personaje2"] == personaje2) or
                        (relation["personaje1"] == personaje2 and relation["personaje2"] == personaje1)
                    ):
                        relation["interacciones"] += 1
                        found = True
                        break
                if not found:
                    self.relationships.append({"personaje1": personaje1, "personaje2": personaje2, "interacciones": 1})

        self.update_table()
        self.scene_entry.delete(0, ttk.END)  # Limpiar campo de escena
        self.is_saved = False  # Indicamos que no se ha guardado

    def save_to_csv(self):
        # Guardar el archivo principal CSV
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Guardar el CSV principal
                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Personaje 1", "Personaje 2", "Interacciones"])
                    for relation in self.relationships:
                        writer.writerow([relation["personaje1"], relation["personaje2"], relation["interacciones"]])

                # Guardar el archivo de nodos _nodes.csv
                nodes = {r["personaje1"] for r in self.relationships} | {r["personaje2"] for r in self.relationships}
                nodes_file_path = file_path.replace(".csv", "_nodes.csv")
                with open(nodes_file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Id", "Label"])
                    for idx, node in enumerate(nodes, 1):
                        writer.writerow([idx, node])

                # Guardar el archivo de aristas _edges.csv
                edges_file_path = file_path.replace(".csv", "_edges.csv")
                with open(edges_file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Source", "Target", "Type", "Weight"])
                    for relation in self.relationships:
                        source_id = list(nodes).index(relation["personaje1"]) + 1
                        target_id = list(nodes).index(relation["personaje2"]) + 1
                        writer.writerow([source_id, target_id, "Undirected", relation["interacciones"]])

                messagebox.showinfo("Éxito", "Datos guardados correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Hubo un error al guardar los datos: {e}")

    def load_from_csv(self):
        # Cargar un archivo CSV
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    next(reader)  # Saltar la fila de encabezados
                    self.relationships = [
                        {"personaje1": row[0], "personaje2": row[1], "interacciones": int(row[2])}
                        for row in reader
                    ]
                self.update_table()
                self.is_saved = True  # Marcamos que los cambios han sido guardados
            except Exception as e:
                messagebox.showerror("Error", f"Hubo un error al cargar el archivo: {e}")

    def update_table(self):
        # Limpiar la tabla
        for row in self.relationship_list.get_children():
            self.relationship_list.delete(row)
        # Agregar filas nuevas
        for relation in self.relationships:
            self.relationship_list.insert(
                "", "end", values=(relation["personaje1"], relation["personaje2"], relation["interacciones"])
            )

    def on_closing(self):
        if not self.is_saved:
            response = messagebox.askyesno("Confirmar", "¿No has guardado los cambios, deseas cerrar?")
            if response:
                self.root.destroy()
        else:
            self.root.destroy()

    def filter_table(self, event=None):
        search_term = self.search_entry.get().lower()
        filtered_relationships = [
            relation for relation in self.relationships
            if search_term in relation["personaje1"].lower() or search_term in relation["personaje2"].lower()
        ]
        self.relationship_list.delete(*self.relationship_list.get_children())
        for relation in filtered_relationships:
            self.relationship_list.insert("", "end", values=(relation["personaje1"], relation["personaje2"], relation["interacciones"]))



if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = InteractionApp(root)
    root.mainloop()
