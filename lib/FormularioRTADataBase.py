import customtkinter
from tkcalendar import Calendar
import tkinter as tk
from datetime import datetime
from PIL import Image
from functools import partial
from tkinter import messagebox
import pyodbc

# Configura los datos de tu servidor y base de datos
server = 'MX29W1009'
database = 'DB_BitacoraTRA'
username = 'PracticanteHSE'
password = 'PracticanteHSE2025'

COLOR_BASE = "transparent"  # Elige el color que prefieras

# Cadena de conexión para SQL Server
connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Intenta conectarse a la base de datos y listar las tablas
try:
    conexion = pyodbc.connect(connection_string)
    print('Conexión exitosa a SQL Server')
    cursor = conexion.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    print('Tablas en la base de datos:')
    for row in cursor:
        print(row[0])
    cursor.close()
    conexion.close()
except Exception as e:
    print(f'Error al conectar: {e}')

# Variables globales para almacenar los datos
Edificio = ""
Area = ""
Lugar = ""
Hora = ""
Descripcion = ""
Compania = ""
Responsable = ""
Fecha = ""  # Nueva variable global para la fecha
Tarea_con_Riesgo = []
Firmado_por = ""
Seleccion_Boton_Matriz = None

class MyCheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, values, image_paths, on_change_callback=None, fg_color=None):
        super().__init__(master)
        self.values = values
        self.image_paths = image_paths
        self.checkboxes = []
        self.images = []
        self.on_change_callback = on_change_callback
        self.fg_color = fg_color

        for i, (value, img_path) in enumerate(zip(self.values, self.image_paths)):
            image = customtkinter.CTkImage(light_image=Image.open(img_path), size=(30, 30))
            self.images.append(image)

            image_label = customtkinter.CTkLabel(self, image=image, text="")
            image_label.grid(row=i, column=0, padx=5, pady=5)

            checkbox = customtkinter.CTkCheckBox(self, text=value, command=self._on_checkbox_change)
            checkbox.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.checkboxes.append(checkbox)

        image = customtkinter.CTkImage(light_image=Image.open("PruebasDeFramesIMG/imgNA.png"), size=(30, 30))
        image_label = customtkinter.CTkLabel(self, image=image, text="")
        image_label.grid(row=0, column=2, padx=5, pady=5)

        self.checkboxNada = customtkinter.CTkCheckBox(self, text="N/A", command=self.toggle_checkboxes)
        self.checkboxNada.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    def _on_checkbox_change(self):
        if self.on_change_callback:
            self.on_change_callback()

    def get(self):
        seleccionados = [cb.cget("text") for cb in self.checkboxes if cb.get() == 1]
        if self.checkboxNada.get() == 1:
            seleccionados.append("TRA Activo")
        return seleccionados
    
    def get_num(self):
        data = {cb.cget("text"): cb.get() for cb in self.checkboxes}
        data["TRA Activo"] = self.checkboxNada.get()
        return data

    def has_selection(self):
        """Check if at least one checkbox is selected"""
        return any(cb.get() == 1 for cb in self.checkboxes) or self.checkboxNada.get() == 1

    def toggle_checkboxes(self):
        nada_selected = self.checkboxNada.get() == 1
        for checkbox in self.checkboxes:
            checkbox.configure(state="disabled" if nada_selected else "normal")
            if nada_selected:
                checkbox.deselect()
        
        # Trigger callback when TRA Activo changes
        if self.on_change_callback:
            self.on_change_callback()

class ButtonsFrames(customtkinter.CTkFrame):
    def __init__(self, master, on_select=None, fg_color=None):
        super().__init__(master)
        self.on_select = on_select
        self.fg_color = fg_color

        self.colors = [
            "#FF0000", "#FF0000", "#FF0000", "#FF0000",
            "#FFF700", "#FFF700", "#FF0000", "#FF0000",
            "#1DFF21", "#FFF700", "#FFF700", "#FF0000",
            "#1DFF21", "#1DFF21", "#FFF700", "#FF0000",
            "#1DFF21", "#1DFF21", "#FFF700", "#FFF700",
            "#1DFF21", "#1DFF21", "#FFF700", "#FFF700"
        ]
        
        self.botones=[]
        numDeBoton=0

        lbl1=customtkinter.CTkLabel(self, text="Seleccione el grado de riesgo de la tarea", font=("Arial", 16, "bold"))
        lbl1.grid(row=0, column=0, columnspan=4, padx=5, pady=5,sticky="e")

        riesgo=["Catastrofico", "Severo", "Serio", "Moderado","Menor", "Minimo"]
        prob_riesgo=["Poco Probable", "Posible", "Probable", "Certeza"]


        for i in range(6):
            self.grid_rowconfigure(i, weight=1)
            lbl2= customtkinter.CTkLabel(self, text=riesgo[i], font=("Arial", 10, "bold"))
            lbl2.grid(row=i+1, column=0, padx=5, pady=5)
            for j in range(4):
                colorDBoton = self.colors[numDeBoton]
                self.grid_columnconfigure(j, weight=1)
                #Usamos partial para pasar el número del botón
                comando = partial(self.seleccion, numDeBoton)
                button = customtkinter.CTkButton(
                    self, width=30, height=30, text="",
                    fg_color=colorDBoton, command=comando,
                    border_color="gray", border_width=1
                )
                button.grid(row=i+1, column=j+1, padx=5, pady=5)
                self.botones.append(button)
                numDeBoton += 1
        self.boton_anterior = None  # Para guardar el índice del último botón presionado
        for i in range(4):
            lbl3 = customtkinter.CTkLabel(self, text=prob_riesgo[i], font=("Arial", 10, "bold"))
            lbl3.grid(row=7, column=i+1, padx=5, pady=5, sticky="w")

    def has_selection(self):
        """Check if a button has been selected in the matrix"""
        return self.boton_anterior is not None
    
    def seleccion(self, numero):
        global Seleccion_Boton_Matriz

        if self.boton_anterior is not None:
            boton_viejo = self.botones[self.boton_anterior]
            boton_viejo.configure(border_color="gray", border_width=1)  # Borde normal

        boton_actual = self.botones[numero]
        boton_actual.configure(border_color="#00BFFF", border_width=4)  # Borde azul y ancho
        self.boton_anterior = numero

        # Guardar el color del botón seleccionado
        Seleccion_Boton_Matriz = self.colors[numero]

        if self.on_select:
            self.on_select(self.colors[numero])

# Función para validar si todos los campos están completos
def validar_formulario(edificio_entry, area_combobox, lugar_entry, hora_entry, descripcion_entry, compania_entry, responsable_entry, checkbox_frame, buttons_frame, firmado_entry=None):
    """Valida si todos los campos del formulario están completos"""
    # Verificar que todos los campos de texto tengan contenido
    campos_texto = [
        edificio_entry.get().strip(),
        area_combobox.get().strip(),
        lugar_entry.get().strip(),
        hora_entry.get().strip(),
        descripcion_entry.get().strip(),
        compania_entry.get().strip(),
        responsable_entry.get().strip()
    ]
    
    # Verificar que todos los campos tengan texto
    todos_campos_completos = all(campo for campo in campos_texto)
    
    # Verificar que haya al menos un checkbox seleccionado
    checkbox_seleccionado = checkbox_frame.has_selection()
    
    # Verificar que se haya seleccionado un botón en la matriz
    matriz_seleccionada = buttons_frame.has_selection()
    
    if firmado_entry is not None:
        firmado_texto = firmado_entry.get().strip()
        return todos_campos_completos and checkbox_seleccionado and matriz_seleccionada and bool(firmado_texto)
    return todos_campos_completos and checkbox_seleccionado and matriz_seleccionada

# Función para actualizar el estado de los botones
def actualizar_botones(guardar_button, excel_button, edificio_entry, area_combobox, lugar_entry, hora_entry, descripcion_entry, compania_entry, responsable_entry, checkbox_frame, buttons_frame, firmado_entry=None):
    """Actualiza el estado habilitado/deshabilitado de los botones"""
    formulario_completo = validar_formulario(edificio_entry, area_combobox, lugar_entry, hora_entry, descripcion_entry, compania_entry, responsable_entry, checkbox_frame, buttons_frame, firmado_entry)
    
    if formulario_completo:
        guardar_button.configure(state="normal")
    else:
        guardar_button.configure(state="disabled")
# Función para abrir el calendario en una ventana emergente
def open_calendar(root, label):
    popup = tk.Toplevel(root)
    popup.title("Seleccionar Fecha")

    cal = Calendar(popup, selectmode='day')
    cal.pack(pady=20)

    select_button = customtkinter.CTkButton(
        popup,
        text="Seleccionar Fecha",
        command=lambda: select_date(cal.get_date(), label, popup)
        
    )
    select_button.pack(pady=20)

# Función para seleccionar la fecha y cerrar el pop-up
def select_date(selected_date, label, popup):
    global Fecha  # Guardamos la fecha en la variable global
    # Convertir la fecha del calendario al formato DATE (YYYY-MM-DD)
    try:
        # Parsear la fecha del calendario (formato MM/DD/YY o MM/DD/YYYY)
        try:
            fecha_obj = datetime.strptime(selected_date, "%m/%d/%y")
        except ValueError:
            fecha_obj = datetime.strptime(selected_date, "%m/%d/%Y")
        Fecha = fecha_obj.strftime("%Y-%m-%d")
    except Exception:
        Fecha = selected_date  # Si hay error, usar la fecha tal como viene
    if Fecha < datetime.now().strftime("%Y-%m-%d"):
        messagebox.showerror("Error", "La fecha seleccionada no puede ser anterior a la fecha actual.")
        Fecha = datetime.now().strftime("%Y-%m-%d")  # Reiniciar a la fecha actual
        return
    label.configure(text=f"Fecha seleccionada: {Fecha}")
    popup.destroy()

# Función para capturar los datos ingresados
def guardar_datos(edificio_entry, area_combobox, lugar_entry, hora_entry, descripcion_entry, compania_entry, responsable_entry, checkbox_frame, firmado_entry, on_guardar=None):
    global Edificio, Area, Lugar, Hora, Descripcion, Compania, Responsable, Fecha, Tarea_con_Riesgo, Firmado_por
    global Seleccion_Boton_Matriz
    
    Edificio = edificio_entry.get()
    Area = area_combobox.get()
    Lugar = lugar_entry.get()
    Hora = hora_entry.get()
    Descripcion = descripcion_entry.get()
    Compania = compania_entry.get()
    Responsable = responsable_entry.get()
    Tarea_con_Riesgo = checkbox_frame.get()
    Firmado_por = firmado_entry.get()
    checkbox_data = checkbox_frame.get_num()


    conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=MX29W1009;'
            'DATABASE=DB_BitacoraTRA;'
            'UID=PracticanteHSE;'
            'PWD=PracticanteHSE2025;'
        )
    #Le damos un TRA ID al registro que se va a insertar
    cursor = conexion.cursor()
    cursor.execute('SELECT COUNT(*) FROM registros_tra WHERE fecha = ?', (Fecha,))
    count = cursor.fetchone()[0]
    tra_id = count + 1


    # Insertar los datos
    estado = "Abierto"
    inspector = ""
    values = [
        tra_id, Fecha, Edificio, Area, Lugar, Hora, Descripcion, Compania, Responsable
    ] + list(checkbox_data.values()) + [Seleccion_Boton_Matriz, Firmado_por, estado, inspector]
    # Asegurarse de que la cantidad de valores coincida con la cantidad de columnas (24)
    # Columnas: tra_id, fecha, edificio, area, lugar, hora, descripcion, compania, responsable (9)
    # + 10 checkboxes (19)
    # + seleccion_boton_matriz (20), firmado_por (21), estado (22), inspector (23)
    # Total: 23 columnas (sin id)
    # Pero en la tabla CREATE hay 24 columnas (sin id), así que hay que revisar el número de checkboxes
    # Revisar que list(checkbox_data.values()) tenga 10 elementos (incluyendo tra_activo)
    # Si hay 9 checkboxes + tra_activo, entonces está correcto
    if len(list(checkbox_data.values())) != 10:
        messagebox.showerror("Error", f"Error interno: se esperaban 10 valores de checkbox, pero se obtuvieron {len(list(checkbox_data.values()))}.")
        cursor.close()
        conexion.close()
        return
    # Total de valores debe ser 23
    if len(values) != 23:
        messagebox.showerror("Error", f"Error interno: se esperaban 23 valores para el INSERT, pero se obtuvieron {len(values)}.")
        cursor.close()
        conexion.close()
        return
    cursor.execute(f'''
        INSERT INTO registros_TRA (
            tra_id, fecha, edificio, area, lugar, hora, descripcion, compania, responsable,
            trabajo_caliente, espacios_confinados, trabajo_en_alturas, bloqueo_etiquetado_prueba,
            energia_en_vivo, interrupcion_de_tuberia, administracion_del_cambio, excavaciones,
            equipo_de_levantamiento, tra_activo, seleccion_boton_matriz, firmado_por, estado, inspector
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', values)
    conexion.commit()
    cursor.close()
    conexion.close()
    messagebox.showinfo("Datos guardados TRA", f"Datos guardados TRA: {tra_id}")
    if on_guardar:
        on_guardar()

# Función principal de la aplicación
def app(master=None, on_guardar=None):
    global Fecha  # Inicializar la fecha global
    Fecha = datetime.now().strftime("%Y-%m-%d")  # Fecha actual por defecto en formato DATE (YYYY-MM-DD)

    if master is None:
        root = customtkinter.CTk()
        root.title("Formulario de Tarea")
        container = root
    else:
        container = master
        for widget in container.winfo_children():
            widget.destroy()

    main_frame = customtkinter.CTkFrame(container,fg_color=COLOR_BASE)
    main_frame.grid(row=0,column=0,padx=20, pady=20)

    # Frame de fecha
    fecha_frame = customtkinter.CTkFrame(main_frame,fg_color=COLOR_BASE)
    fecha_frame.pack(pady=10, fill="x")

    fecha_label = customtkinter.CTkLabel(fecha_frame, text=f"Fecha: {Fecha}")
    fecha_label.pack(pady=5)

    fecha_button = customtkinter.CTkButton(fecha_frame, text="Seleccionar Fecha", command=lambda: open_calendar(container, fecha_label))
    fecha_button.pack(pady=5)

    # Label de Tarea
    tarea_label = customtkinter.CTkLabel(main_frame, text="Tarea", font=customtkinter.CTkFont(size=16, weight="bold"))
    tarea_label.pack(pady=10)

    #Funcion para seleccionar el area del edificio
    def areaSelect(value):
        if value == "Planta 1":
            subopciones = ["1A 737", 
                            "1A Mix", 
                            "1AUD", 
                            "1C",
                            "1E",
                            "1H",
                            "1P",
                            "1S 737",
                            "1S Mix",
                            "1TS",
                            "2G",
                            "2M",
                            "3G",
                            "3M",
                            "4M",
                            "6A",
                            "A350 Acero",
                            "Almacen High Bay",
                            "Almacen Low Bay",
                            "Baños",
                            "Embarque",
                            "Exterior",
                            "F15",
                            "FT/PT",
                            "JSF",
                            "Laboratorio de Ingenieria",
                            "NPD High Bay",
                            "NPD Low Bay",
                            "Oficinas",
                            "Otros",
                            "Pasillos",
                            "R&O",
                            "Recepcion",
                            "Salas de juntas",
                            "Simulacion",
                            "Taller HOS"]
        elif value == "Planta 2":
            subopciones = ["1T", 
                           "2D",
                           "2P",
                           "R&O",
                           "A350 Aluminio",
                           "Almacen",
                           "Baños",
                           "Embarque",
                           "Exterior",
                           "FT/PT",
                           "Metrologia",
                           "Oficinas planta alta",
                           "Oficinas planta baja",
                           "Otros",
                           "Recepcion",
                           "Salas de juntas"]
        elif value == "MX80":
            subopciones = ["Almacen",
                           "Baños",
                           "ECOE",
                           "Exterior",
                           "E-Shop",
                           "Machine Shop",
                           "MAT LAB",
                           "Oficinas planta alta",
                           "Recepcion",
                           "Salas de juntas",
                           "SIL"]
        elif value == "Planta 3":
            subopciones = ["Exterior", 
                           "Otro"]
        else:
            subopciones = ["Otro"]
        area_combobox.set("")  # Limpia la selección anterior
        area_combobox.configure(values=subopciones)

    # Entradas de datos
    edificio_combobox = customtkinter.CTkComboBox(main_frame, values=[
        "Planta 1",
        "Planta 2",
        "MX80",
        "Planta 3",
        "Planta 4"
    ], command=areaSelect)
    edificio_combobox.pack(pady=5)

    area_combobox = customtkinter.CTkComboBox(main_frame, values=["1A 737", 
                            "1A Mix", 
                            "1AUD", 
                            "1C",
                            "1E",
                            "1H",
                            "1P",
                            "1S 737",
                            "1S Mix",
                            "1TS",
                            "2G",
                            "2M",
                            "3G",
                            "3M",
                            "4M",
                            "6A",
                            "A350 Acero",
                            "Almacen High Bay",
                            "Almacen Low Bay",
                            "Baños",
                            "Embarque",
                            "Exterior",
                            "F15",
                            "FT/PT",
                            "JSF",
                            "Laboratorio de Ingenieria",
                            "NPD High Bay",
                            "NPD Low Bay",
                            "Oficinas",
                            "Otros",
                            "Pasillos",
                            "R&O",
                            "Recepcion",
                            "Salas de juntas",
                            "Simulacion",
                            "Taller HOS"])
    area_combobox.pack(pady=5)

    lugar_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Lugar")
    lugar_entry.pack(pady=5)

    # Obtener hora actual del sistema en formato 12 horas con AM/PM
    hora_actual = datetime.now().strftime("%I:%M %p")
    hora_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Hora")
    hora_entry.insert(0, hora_actual)
    hora_entry.pack(pady=5)

    descripcion_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Descripción")
    descripcion_entry.pack(pady=5)

    compania_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Compañía")
    compania_entry.pack(pady=5)

    responsable_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Responsable TRA")
    responsable_entry.pack(pady=5)

    values = [
        "Trabajo Caliente",
        "Espacios Confinados",
        "Trabajo en alturas",
        "Bloqueo/Etiquetado/Prueba",
        "Energia en vivo",
        "Interrupcion de tuberia",
        "Administracion del cambio",
        "Excavaciones",
        "Equipo de Levantamiento"
    ]

    image_paths = [
        "PruebasDeFramesIMG/imgTrabajoCaliente.png", 
        "PruebasDeFramesIMG/imgConfinados.png",
        "PruebasDeFramesIMG/imgAlturas.png",
        "PruebasDeFramesIMG/imgBloqueo.png",
        "PruebasDeFramesIMG/imgEnergia.png",
        "PruebasDeFramesIMG/imgTuberias.png",
        "PruebasDeFramesIMG/imgAdmCambios.png",
        "PruebasDeFramesIMG/imgExcavaciones.png",
        "PruebasDeFramesIMG/imgLevantamiento.png"
    ]


    # --- CORRECCIÓN: crear los frames y asignarlos al contenedor ---
    def on_form_change():
        actualizar_botones(guardar_button, None, edificio_combobox, area_combobox, lugar_entry, hora_entry, descripcion_entry, compania_entry, responsable_entry, container.checkbox_frame, container.botones, firmado_entry)

    def on_matrix_select(selection):
        on_form_change()

    container.checkbox_frame = MyCheckboxFrame(container, values=values, image_paths=image_paths, on_change_callback=on_form_change,fg_color=COLOR_BASE)
    container.checkbox_frame.grid(row=0, column=1, padx=20, pady=20)
    container.seleccion_actual = None
    container.botones = ButtonsFrames(container, on_select=on_matrix_select, fg_color=COLOR_BASE)
    container.botones.grid(row=0, column=2, padx=10, pady=10)
    container.botones.configure(width=200, height=150)  # Ajusta estos valores según lo que necesites

    # --- CORRECCIÓN: actualizar eventos para usar el contenedor ---
    def bind_entry_events():
        lugar_entry.bind('<KeyRelease>', lambda e: on_form_change())
        hora_entry.bind('<KeyRelease>', lambda e: on_form_change())
        descripcion_entry.bind('<KeyRelease>', lambda e: on_form_change())
        compania_entry.bind('<KeyRelease>', lambda e: on_form_change())
        responsable_entry.bind('<KeyRelease>', lambda e: on_form_change())

    container.after(100, bind_entry_events)

    # Campo para 'Firmado por' (al final)
    firmado_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Firmado por")
    firmado_entry.pack(pady=10)

    def on_firmado_change(event=None):
        on_form_change()

    firmado_entry.bind('<KeyRelease>', on_firmado_change)

    # --- CORRECCIÓN: crear el botón de guardar con referencias correctas ---
    guardar_button = customtkinter.CTkButton(
        main_frame,
        text="Guardar Datos",
        state="disabled",
        command=lambda: guardar_datos(
            edificio_combobox,
            area_combobox,
            lugar_entry,
            hora_entry,
            descripcion_entry,
            compania_entry,
            responsable_entry,
            container.checkbox_frame,
            firmado_entry,
            on_guardar
        )
    )
    guardar_button.pack(pady=10)

    # Botón Cancelar (siempre habilitado)
    def cancelar():
        if master is None:
            container.destroy()
        else:
            for widget in container.winfo_children():
                widget.destroy()

    cancelar_button = customtkinter.CTkButton(
        main_frame,
        text="Cancelar",
        fg_color="red",
        hover_color="darkred",
        command=cancelar,
        state="normal"
    )
    cancelar_button.pack(pady=5)

    if master is None:
        container.mainloop()

# Ejecutar la aplicación solo si es principal
if __name__ == "__main__":
    app()