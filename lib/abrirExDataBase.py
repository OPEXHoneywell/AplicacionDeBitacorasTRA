import customtkinter
import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
import pyodbc

def abrir_bitacoras(master=None):
    if master is None:
        root = customtkinter.CTk()
        root.title("Visor de Bitácoras (Base de Datos)")
        container = root
    else:
        container = master
        for widget in container.winfo_children():
            widget.destroy()

    frame = customtkinter.CTkFrame(container)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    def mostrar_db_fecha_actual():
        headers = [
            "ID", "Fecha", "Edificio", "Area", "Lugar", "Hora", "Descripcion", "Compania", "Responsable",
            "Trabajo Caliente", "Espacios Confinados", "Trabajo en alturas", "Bloqueo/Etiquetado/Prueba",
            "Energia en vivo", "Interrupcion de tuberia", "Administracion del cambio", "Excavaciones",
            "Equipo de Levantamiento", "N/A", "Grado de riesgo", "Firmado por", "Estado"
        ]
        
        fecha_var = tk.StringVar(value=str(datetime.now().date()))
        headers = [
            "ID", "Fecha", "Edificio", "Area", "Lugar", "Hora", "Descripcion", "Compania", "Responsable",
            "Trabajo Caliente", "Espacios Confinados", "Trabajo en alturas", "Bloqueo/Etiquetado/Prueba",
            "Energia en vivo", "Interrupcion de tuberia", "Administracion del cambio", "Excavaciones",
            "Equipo de Levantamiento", "TRA Activo", "Seleccion_Boton_Matriz", "Firmado por", "Estado", "Inspector"
        ]
        fecha = fecha_var.get()
        # Usar la fecha directamente como DATE
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=MX29W1009;'
            'DATABASE=DB_BitacoraTRA;'
            'UID=PracticanteHSE;'
            'PWD=PracticanteHSE2025;'
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT tra_id, fecha, edificio, area, lugar, hora, descripcion, compania, responsable,trabajo_caliente, espacios_confinados, trabajo_en_alturas, bloqueo_etiquetado_prueba,energia_en_vivo, interrupcion_de_tuberia, administracion_del_cambio, excavaciones,equipo_de_levantamiento, tra_activo, seleccion_boton_matriz, firmado_por, estado, inspector FROM registros_tra WHERE fecha = ?", (fecha,))
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()
        for row in tree.get_children():
            tree.delete(row)
        tree["columns"] = ()
        tree["show"] = "headings"
        columnas = [f"Col{i+1}" for i in range(len(headers))]
        tree["columns"] = columnas
        for i, col in enumerate(headers):
            tree.heading(columnas[i], text=col)
            tree.column(columnas[i], width=120)
        for fila in filas:
            fila_modificada = list(fila)
            for idx in range(9, 19):
                if idx < len(fila_modificada):
                    if fila_modificada[idx] == 1:
                        fila_modificada[idx] = 'X'
                    elif fila_modificada[idx] == 0:
                        fila_modificada[idx] = ''
            # Cambiar el valor de seleccion_boton_matriz por texto de riesgo
            if len(fila_modificada) > 19:
                color = str(fila_modificada[19]).strip()
                if color == "#1DFF21":
                    fila_modificada[19] = "Bajo"
                elif color == "#FFF700":
                    fila_modificada[19] = "Medio"
                else:
                    fila_modificada[19] = "Alto"
            tree.insert("", "end", values=fila_modificada)

    def mostrar_popup_detalle(event):
        item = tree.selection()
        if not item:
            return
        valores = tree.item(item[0], "values")
        # Si el estado es 'Auditado' o 'Cancelado', no mostrar el pop-up
        if len(valores) > 21 and str(valores[21]).strip().lower() in ["auditado", "cancelado"]:
            return
        popup = customtkinter.CTkToplevel(container)
        popup.title(f"Registro de Auditoria - ID {valores[0]}")
        # Abrir el pop-up en modo maximizado (ventana normal ocupando toda la pantalla)
        try:
            popup.state('zoomed')  # Windows
        except Exception:
            popup.attributes('-zoomed', True)  # Otros sistemas
        # Rutas de imágenes para las tareas
        image_paths = [
            "PruebasDeFramesIMG/imgTrabajoCaliente.png",
            "PruebasDeFramesIMG/imgConfinados.png",
            "PruebasDeFramesIMG/imgAlturas.png",
            "PruebasDeFramesIMG/imgBloqueo.png",
            "PruebasDeFramesIMG/imgEnergia.png",
            "PruebasDeFramesIMG/imgTuberias.png",
            "PruebasDeFramesIMG/imgAdmCambios.png",
            "PruebasDeFramesIMG/imgExcavaciones.png",
            "PruebasDeFramesIMG/imgLevantamiento.png",
            "PruebasDeFramesIMG/imgRepAb.png"  # Para N/A
        ]
        tarea_labels = [
            "Trabajo Caliente", "Espacios Confinados", "Trabajo en alturas", "Bloqueo/Etiquetado/Prueba",
            "Energia en vivo", "Interrupción de tubería", "Administración del cambio", "Excavaciones",
            "Equipo de Levantamiento", "TRA Activo"
        ]
        # Mostrar campos generales
        customtkinter.CTkLabel(popup, text="TRA:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        customtkinter.CTkLabel(popup, text=valores[0], font=("Arial", 14,"bold")).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        customtkinter.CTkLabel(popup, text="Fecha:", font=("Arial", 14, "bold")).grid(row=0, column=2, sticky="e", padx=10, pady=5)
        customtkinter.CTkLabel(popup, text=valores[1], font=("Arial", 14)).grid(row=0, column=3, sticky="w", padx=10, pady=5)
        # Mostrar campos editables con Entry
        customtkinter.CTkLabel(popup, text="Edificio:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        entry_edificio = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_edificio.insert(0, valores[2])
        entry_edificio.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Área:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="e", padx=10, pady=5)
        entry_area = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_area.insert(0, valores[3])
        entry_area.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Lugar:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="e", padx=10, pady=5)
        entry_lugar = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_lugar.insert(0, valores[4])
        entry_lugar.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Hora:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="e", padx=10, pady=5)
        entry_hora = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_hora.insert(0, valores[5])
        entry_hora.grid(row=6, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Descripción:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="e", padx=10, pady=5)
        entry_descripcion = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_descripcion.insert(0, valores[6])
        entry_descripcion.grid(row=7, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Compañía:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky="e", padx=10, pady=5)
        entry_compania = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_compania.insert(0, valores[7])
        entry_compania.grid(row=8, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Responsable:", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky="e", padx=10, pady=5)
        entry_responsable = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_responsable.insert(0, valores[8])
        entry_responsable.grid(row=9, column=1, sticky="w", padx=10, pady=5)

        customtkinter.CTkLabel(popup, text="Revisiones realizadas", font=("Arial", 11,"bold")).grid(row=2, column=3, sticky="w", padx=10, pady=5)
        from PIL import Image
        check_vars = []
        img_refs = []
        for i, tarea in enumerate(tarea_labels):
            valor = valores[9 + i]
            row_idx = 3 + i
            customtkinter.CTkLabel(popup, text=tarea+":", font=("Arial", 10, "bold")).grid(row=row_idx, column=3, sticky="e", padx=10, pady=5)
            # Imagen
            if os.path.exists(image_paths[i]):
                img = Image.open(image_paths[i])
                ctk_img = customtkinter.CTkImage(light_image=img, size=(28, 28))
                img_refs.append(ctk_img)
                customtkinter.CTkLabel(popup, image=ctk_img, text="").grid(row=row_idx, column=4, sticky="w", padx=10, pady=5)
            else:
                customtkinter.CTkLabel(popup, text="[Imagen]", font=("Arial", 8)).grid(row=row_idx, column=4, sticky="w", padx=10, pady=5)
            # Checkbox solo habilitado si la tarea está marcada (valor == 'X')
            var = tk.IntVar(value=0)
            cb = customtkinter.CTkCheckBox(popup, text="", variable=var, state="normal" if valor == 'X' else "disabled", font=("Arial", 10))
            cb.grid(row=row_idx, column=2, padx=10, pady=5)
            check_vars.append(var)
            # Mostrar X si está marcada, vacío si no
            x_text = 'X' if valor == 'X' else ''
            customtkinter.CTkLabel(popup, text=x_text, font=("Arial", 10, "bold")).grid(row=row_idx, column=5, sticky="w", padx=10, pady=5)
        
        # Grado de riesgo y firmado por
        customtkinter.CTkLabel(popup, text="Grado de Riesgo:", font=("Arial", 11, "bold")).grid(row=1, column=2, sticky="e", padx=10, pady=5)
        valor_matriz = valores[19]
        color = str(valor_matriz).strip()
        if valor_matriz == "Bajo":
            color = "#1DFF21"
        elif valor_matriz == "Medio":
            color = "#FFF700"
        else:
            color = "#FF0000"
        color_matriz = str(color).strip()
        # Si es color hexadecimal válido
        if color_matriz.startswith("#") and (len(color_matriz) == 7 or len(color_matriz) == 4):
            bg_color = color_matriz
        else:
            # Mapear palabras comunes a colores
            colores_matriz = {
                "verde": "#1DFF21",
                "amarillo": "#FFF700",
                "rojo": "#FF0000",
                "azul": "#0000FF",
                "naranja": "#FFA500"
            }
            bg_color = colores_matriz.get(color_matriz.lower(), "#FFFFFF")
        # Para el label de color, usamos un CTkLabel y el argumento fg_color
        customtkinter.CTkLabel(popup, text="                                       ", font=("Arial", 12), fg_color=bg_color).grid(row=1, column=3, sticky="w", padx=10, pady=5)
        customtkinter.CTkLabel(popup, text="Firmado por:", font=("Arial", 10, "bold")).grid(row=13, column=0, sticky="e", padx=10, pady=5)
        entry_firmado = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_firmado.insert(0, valores[20])
        entry_firmado.grid(row=13, column=1, sticky="w", padx=10, pady=5)
        # Campo para razón de cancelación
        customtkinter.CTkLabel(popup, text="Razón de cancelación:", font=("Arial", 10, "bold")).grid(row=13, column=2, sticky="e", padx=10, pady=5)
        entry_razon_cancelacion = customtkinter.CTkEntry(popup, font=("Arial", 10))
        entry_razon_cancelacion.grid(row=13, column=3, sticky="w", padx=10, pady=5)
        # Campo para firmar auditoría
        customtkinter.CTkLabel(popup, text="Auditado por:", font=("Arial", 10, "bold")).grid(row=14, column=0, sticky="e", padx=10, pady=15)
        # --- Cargar nombres de auditadores desde la base de datos ---
        # Métodos para auditores usando SQL Server
        def cargar_nombres_auditadores():
            try:
                conexion = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=MX29W1009;'
                    'DATABASE=DB_BitacoraTRA;'
                    'UID=PracticanteHSE;'
                    'PWD=PracticanteHSE2025;'
                )
                cursor = conexion.cursor()
                cursor.execute('SELECT nombre FROM auditores')  # Sin ORDER BY para evitar error con tipos text/ntext
                nombres = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conexion.close()
                return nombres
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al cargar auditores: {str(e)}")
                return []

        def agregar_auditor_db(nombre):
            try:
                conexion = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=MX29W1009;'
                    'DATABASE=DB_BitacoraTRA;'
                    'UID=PracticanteHSE;'
                    'PWD=PracticanteHSE2025;'
                )
                cursor = conexion.cursor()
                # No comparar con WHERE nombre = ? si es tipo TEXT, solo intentar insertar y capturar error de duplicado
                try:
                    cursor.execute('INSERT INTO auditores (nombre) VALUES (?)', (nombre,))
                    conexion.commit()
                except Exception as insert_e:
                    # Si es error de duplicado, ignorar, si es otro, mostrar
                    if 'duplicate' not in str(insert_e).lower():
                        tk.messagebox.showerror("Error", f"Error al agregar auditor: {str(insert_e)}")
                cursor.close()
                conexion.close()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al agregar auditor: {str(e)}")

        def borrar_auditor_db(nombre):
            try:
                conexion = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=MX29W1009;'
                    'DATABASE=DB_BitacoraTRA;'
                    'UID=PracticanteHSE;'
                    'PWD=PracticanteHSE2025;'
                )
                cursor = conexion.cursor()
                cursor.execute('DELETE FROM auditores WHERE nombre = ?', (nombre,))
                conexion.commit()
                cursor.close()
                conexion.close()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al borrar auditor: {str(e)}")

        # Si la tabla está vacía, insertar los nombres iniciales
        nombres_iniciales = [
            "Avalos, Antonio", "Banuelos, Marco", "Cevallos, Alejandro", "Cruz, Alfonso Cruz", "Espinoza, Mariana", "Fonseca, Deniss", "Garcia, Cinthya Paola", "Leal Castro, Monserrat", "Ortiz, Jorge Alejandro", "Perez, Victor","Robles, Marialejandra","Valenzuela, Diana"
        ]
        try:
            conexion = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=MX29W1009;'
                'DATABASE=DB_BitacoraTRA;'
                'UID=PracticanteHSE;'
                'PWD=PracticanteHSE2025;'
            )
            cursor = conexion.cursor()
            cursor.execute('SELECT COUNT(*) FROM auditores')
            if cursor.fetchone()[0] == 0:
                for n in nombres_iniciales:
                    cursor.execute('INSERT INTO auditores (nombre) VALUES (?)', (n,))
                conexion.commit()
            cursor.close()
            conexion.close()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al inicializar auditores: {str(e)}")

        nombres_auditores = cargar_nombres_auditadores()
        entry_auditor = ttk.Combobox(popup, values=nombres_auditores, font=("Arial", 10))  # Permite escribir
        if nombres_auditores:
            entry_auditor.set(nombres_auditores[0])
        entry_auditor.grid(row=14, column=1, padx=10, pady=15)

        # Botón para agregar/borrar nombres de auditores con contraseña
        def actualizar_combobox():
            nuevos_nombres = cargar_nombres_auditadores()
            entry_auditor['values'] = nuevos_nombres
            if nuevos_nombres:
                entry_auditor.set(nuevos_nombres[0])

        def pedir_contrasena_y_modificar():
            def verificar():
                contrasena = entry_pass.get()
                if contrasena == "segura123":  # Cambia la contraseña aquí
                    popup_pass.destroy()
                    popup_modificar_nombre()
                else:
                    tk.messagebox.showerror("Error", "Contraseña incorrecta")
            popup_pass = tk.Toplevel(popup)
            popup_pass.title("Contraseña requerida")
            tk.Label(popup_pass, text="Introduce la contraseña:").pack(padx=10, pady=5)
            entry_pass = tk.Entry(popup_pass, show="*", width=20)
            entry_pass.pack(padx=10, pady=5)
            tk.Button(popup_pass, text="Aceptar", command=verificar).pack(pady=10)
            entry_pass.focus_set()

        def popup_modificar_nombre():
            win = tk.Toplevel(popup)
            win.title("Agregar/Borrar nombre de auditor")


            def refrescar_nombres():
                # Eliminar labels y botones previos si existen
                for widget in win.grid_slaves():
                    if int(widget.grid_info()["row"]) > 0:
                        widget.grid_forget()
                # Recargar nombres desde la base de datos
                nombres_actuales = cargar_nombres_auditadores()
                # Mostrar todos los nombres actuales con botón borrar
                for idx, nombre in enumerate(nombres_actuales):
                    def borrar_nombre(n=nombre):
                        borrar_auditor_db(n)
                        refrescar_nombres()
                        actualizar_combobox()
                        tk.messagebox.showinfo("Éxito", f"Nombre '{n}' borrado.")
                    btn = tk.Button(win, text="Borrar", command=borrar_nombre, width=7)
                    btn.grid(row=1+idx, column=0, padx=5, pady=2)
                    tk.Label(win, text=nombre, anchor="w").grid(row=1+idx, column=1, sticky="w", padx=5)

            tk.Label(win, text="Nombres actuales:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=(5,0))
            refrescar_nombres()

            def agregar():
                nombre = entry_nuevo.get().strip()
                if nombre:
                    if nombre not in cargar_nombres_auditadores():
                        agregar_auditor_db(nombre)
                        refrescar_nombres()
                        actualizar_combobox()
                        tk.messagebox.showinfo("Éxito", f"Nombre '{nombre}' agregado.")
                        win.destroy()
                    else:
                        tk.messagebox.showerror("Error", "El nombre ya existe.")
                else:
                    tk.messagebox.showerror("Error", "Nombre vacío.")

            row_offset = 1 + len(cargar_nombres_auditadores())
            tk.Label(win, text="Nombre a agregar:").grid(row=row_offset, column=0, padx=5, pady=5)
            entry_nuevo = tk.Entry(win, width=30)
            entry_nuevo.grid(row=row_offset, column=1, padx=5, pady=5)
            tk.Button(win, text="Agregar", command=agregar).grid(row=row_offset+1, column=0, columnspan=2, padx=5, pady=5)

        btn_agregar = tk.Button(popup, text="Agregar", font=("Arial", 9, "bold"), command=pedir_contrasena_y_modificar)
        btn_agregar.grid(row=14, column=2, padx=10, pady=5, sticky="w")

        def on_popup_close():
            popup.destroy()
            mostrar_db_fecha_actual()

        # Botón guardar auditoría (inicia deshabilitado)
        btn_guardar = tk.Button(popup, text="Guardar Auditoría", font=("Arial", 10, "bold"), state="disabled")
        btn_guardar.grid(row=15, column=0, columnspan=4, pady=20)
        tk.Button(popup, text="Cerrar", font=("Arial", 9), command=on_popup_close).grid(row=15, column=2, columnspan=4, pady=5)
        popup.img_refs = img_refs  # Referencia para evitar garbage collection
        popup.protocol("WM_DELETE_WINDOW", on_popup_close)

        # Checkbox para cancelar TRA
        cancelar_var = tk.IntVar(value=0)
        chk_cancelar = tk.Checkbutton(popup, text="Cancelar TRA", variable=cancelar_var, font=("Arial", 10, "bold"))
        chk_cancelar.grid(row=15, column=1, sticky="w", padx=10, pady=5)

        # Modificar puede_guardar para habilitar guardar si se cancela el TRA
        def puede_guardar():
            nombre_auditor = entry_auditor.get().strip()
            alguna_tarea = any(var.get() for var, tarea_val in zip(check_vars, valores[9:19]) if tarea_val == 'X')
            if cancelar_var.get() == 1:
                # Solo habilitar si hay razón de cancelación y firmado por
                if entry_firmado.get().strip() and entry_razon_cancelacion.get().strip():
                    btn_guardar.config(state="normal")
                else:
                    btn_guardar.config(state="disabled")
            elif nombre_auditor and alguna_tarea:
                btn_guardar.config(state="normal")
            else:
                btn_guardar.config(state="disabled")

        entry_auditor.bind('<KeyRelease>', lambda e: puede_guardar())
        for var in check_vars:
            var.trace_add('write', lambda *args: puede_guardar())
        cancelar_var.trace_add('write', lambda *args: puede_guardar())
        entry_firmado.bind('<KeyRelease>', lambda e: puede_guardar())
        entry_razon_cancelacion.bind('<KeyRelease>', lambda e: puede_guardar())

        def guardar_auditoria():
            if cancelar_var.get() == 1:
                # Cancelar el TRA: actualizar la columna 'estado' a 'Cancelado' y guardar razón y usuario
                try:
                    conexion = pyodbc.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server};'
                        'SERVER=MX29W1009;'
                        'DATABASE=DB_BitacoraTRA;'
                        'UID=PracticanteHSE;'
                        'PWD=PracticanteHSE2025;'
                    )
                    cursor = conexion.cursor()
                    # Actualizar el registro seleccionado
                    cursor.execute("""
                        UPDATE registros_tra
                        SET estado = ?, razon = ?, inspector = ?
                        WHERE tra_id = ? AND fecha = ?
                    """, (
                        "Cancelado",
                        entry_razon_cancelacion.get().strip(),
                        entry_auditor.get().strip(),
                        valores[0],  # tra_id
                        valores[1]   # fecha
                    ))
                    conexion.commit()
                    cursor.close()
                    conexion.close()
                    tk.messagebox.showinfo("Éxito", "TRA cancelado correctamente en la tabla de registros.")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"No se pudo cancelar el TRA: {str(e)}")
                on_popup_close()
                return
            

            # Validar campos antes de guardar auditoría
            nombre_auditor = entry_auditor.get().strip()
            if not nombre_auditor:
                tk.messagebox.showerror("Error", "Debes firmar la auditoría con un nombre.")
                return
            if not any(var.get() for var, tarea_val in zip(check_vars, valores[9:19]) if tarea_val == 'X'):
                tk.messagebox.showerror("Error", "Debes seleccionar al menos una tarea auditada.")
                return

            # Guardar auditoría en SQL Server (en la misma tabla, actualizando inspector, estado y tareas_auditadas)
            tareas_auditadas = [tarea_labels[i] for i, var in enumerate(check_vars) if var.get() and valores[9 + i] == 'X']
            tareas_str = ', '.join(tareas_auditadas)
            try:
                conexion = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=MX29W1009;'
                    'DATABASE=DB_BitacoraTRA;'
                    'UID=PracticanteHSE;'
                    'PWD=PracticanteHSE2025;'
                )
                cursor = conexion.cursor()
                # Si existe la columna tareas_auditadas, actualízala. Si no, solo actualiza inspector y estado
                try:
                    cursor.execute("""
                        UPDATE registros_tra
                        SET inspector = ?, estado = ?, tareas_auditadas = ?
                        WHERE tra_id = ? AND fecha = ?
                    """, (
                        nombre_auditor,
                        "Auditado",
                        tareas_str,
                        valores[0],  # tra_id
                        valores[1]   # fecha
                    ))
                except Exception:
                    # Si la columna tareas_auditadas no existe, solo actualiza inspector y estado
                    cursor.execute("""
                        UPDATE registros_tra
                        SET inspector = ?, estado = ?
                        WHERE tra_id = ? AND fecha = ?
                    """, (
                        nombre_auditor,
                        "Auditado",
                        valores[0],  # tra_id
                        valores[1]   # fecha
                    ))
                conexion.commit()
                cursor.close()
                conexion.close()
            except Exception as e:
                tk.messagebox.showerror("Error", f"No se pudo guardar la auditoría: {str(e)}")

            # Actualizar el registro en SQL Server: poner inspector y estado="Auditado"
            try:
                conexion = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=MX29W1009;'
                    'DATABASE=DB_BitacoraTRA;'
                    'UID=PracticanteHSE;'
                    'PWD=PracticanteHSE2025;'
                )
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE registros_tra
                    SET inspector = ?, estado = ?
                    WHERE tra_id = ? AND fecha = ?
                """, (
                    nombre_auditor,
                    "Auditado",
                    valores[0],  # tra_id
                    valores[1]   # fecha
                ))
                conexion.commit()
                cursor.close()
                conexion.close()
                tk.messagebox.showinfo("Éxito", "Auditoría guardada y registro TRA actualizado correctamente.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"La auditoría se guardó, pero no se pudo actualizar el estado/inspector en SQL Server: {str(e)}")
            on_popup_close()
        btn_guardar.config(command=guardar_auditoria)

    tree = ttk.Treeview(frame)
    tree.pack(fill="both", expand=True)

    #Scrollbar
    h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    h_scroll.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=h_scroll.set)

    v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    v_scroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=v_scroll.set)

    tree.bind("<Double-1>", mostrar_popup_detalle)
    mostrar_db_fecha_actual()

    if master is None:
        container.mainloop()

if __name__ == "__main__":
    abrir_bitacoras()