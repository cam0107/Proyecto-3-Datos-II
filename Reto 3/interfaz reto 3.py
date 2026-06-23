import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import sys

directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

from corrupción_archivos import aplicar_corrupcion_checksum, aplicar_corrupcion_crc
from corrección_checksum import procesar_json_checksum

class InterfazReto3:
    def __init__(self, root):
        self.root = root
        self.root.title("Reto 3 - Detección y Corrección de Errores (Checksum / CRC)")
        self.root.geometry("780x690")
        self.root.resizable(False, False)
        
        self.ruta_txt_original = ""
        self.ruta_json_pistas = ""
        
        self.notebook = ttk.Notebook(root)
        self.tab_corromper = ttk.Frame(self.notebook)
        self.tab_corregir = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_corromper, text="Corromper archivos")
        self.notebook.add(self.tab_corregir, text="Corregir archivos")
        self.notebook.pack(expand=True, fill="both")
        
        self.setup_pestana_corromper()
        self.setup_pestana_corregir()

    def setup_pestana_corromper(self):
        lbl_comp = ttk.LabelFrame(self.tab_corromper, text=" Configuración de Corrupción ")
        lbl_comp.pack(fill="x", padx=20, pady=15)
        
        # Selección de archivo
        frame_input = ttk.Frame(lbl_comp)
        frame_input.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_input, text="Archivo .txt original:", width=20, anchor="w").pack(side="left")
        self.ent_txt_in = ttk.Entry(frame_input, width=50, state="readonly")
        self.ent_txt_in.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(frame_input, text="Buscar TXT", command=self.seleccionar_archivo_txt).pack(side="right")
        
        # Selector de Algoritmo 
        frame_algo = ttk.Frame(lbl_comp)
        frame_algo.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_algo, text="Algoritmo de Verificación:", width=24, anchor="w").pack(side="left")
        self.combo_algoritmo = ttk.Combobox(frame_algo, values=["Checksum Simple", "CRC"], state="readonly", width=18)
        self.combo_algoritmo.set("Checksum Simple")
        self.combo_algoritmo.pack(side="left", padx=5)
        
        # Cantidad de errores
        frame_spin = ttk.Frame(lbl_comp)
        frame_spin.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_spin, text="Cantidad de errores (bits):", width=24, anchor="w").pack(side="left")
        self.spin_errores = ttk.Spinbox(frame_spin, from_=1, to=100, width=10)
        self.spin_errores.set(2)
        self.spin_errores.pack(side="left", padx=5)
        
        ttk.Button(lbl_comp, text="¡Corromper y Guardar!", command=self.ejecutar_corrupcion).pack(pady=10)
        
        # Visualización
        lbl_prev = ttk.LabelFrame(self.tab_corromper, text=" Previsualización de Datos ")
        lbl_prev.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        lbl_prev.columnconfigure(0, weight=1)
        lbl_prev.columnconfigure(1, weight=1)
        lbl_prev.rowconfigure(1, weight=1)
        
        ttk.Label(lbl_prev, text="Mensaje Original", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=(0, 5))
        ttk.Label(lbl_prev, text="Mensaje Corrupto", font=("Arial", 10, "bold")).grid(row=0, column=1, pady=(0, 5))
        
        self.txt_original = tk.Text(lbl_prev, height=16, width=35, bg="#f4f4f4", font=("Consolas", 10))
        self.txt_original.grid(row=1, column=0, padx=5, sticky="nsew")
        self.txt_original.config(state="disabled")
        
        self.txt_corrupto = tk.Text(lbl_prev, height=16, width=35, bg="#f4f4f4", font=("Consolas", 10))
        self.txt_corrupto.grid(row=1, column=1, padx=5, sticky="nsew")
        self.txt_corrupto.config(state="disabled")

    def seleccionar_archivo_txt(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt")])
        if ruta:
            self.ruta_txt_original = ruta
            self.ent_txt_in.config(state="normal")
            self.ent_txt_in.delete(0, tk.END)
            self.ent_txt_in.insert(0, ruta)
            self.ent_txt_in.config(state="readonly")
            
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.txt_original.config(state="normal")
                self.txt_original.delete("1.0", "end")
                self.txt_original.insert("end", contenido)
                self.txt_original.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{str(e)}")

    def ejecutar_corrupcion(self):
        if not self.ruta_txt_original:
            messagebox.showwarning("Advertencia", "Debe cargar un archivo de texto primero.")
            return
            
        try:
            try:
                cantidad = int(self.spin_errores.get())
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                return
                
            with open(self.ruta_txt_original, 'r', encoding='utf-8') as f:
                texto_original = f.read()
                
            # Ejecutar algoritmo según selección del Combobox
            algo_seleccionado = self.combo_algoritmo.get()
            
            if algo_seleccionado == "CRC":
                respuesta = aplicar_corrupcion_crc(texto_original, cantidad)
            else:
                if cantidad > len(texto_original):
                    messagebox.showerror("Error", "La cantidad de errores no puede exceder la longitud del mensaje.")
                    return
                respuesta = aplicar_corrupcion_checksum(texto_original, cantidad)
                
            texto_corrupto = respuesta["texto_corrupto"]
            diccionario_pistas = respuesta["json_pistas"]
            
            self.txt_corrupto.config(state="normal")
            self.txt_corrupto.delete("1.0", "end")
            self.txt_corrupto.insert("end", texto_corrupto)
            self.txt_corrupto.config(state="disabled")
            
            proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            dir_json = os.path.join(proyecto_dir, "json")
            
            os.makedirs(dir_salidas, exist_ok=True)
            os.makedirs(dir_json, exist_ok=True)
            
            nombre_base = os.path.splitext(os.path.basename(self.ruta_txt_original))[0]
            ruta_salida_txt = os.path.join(dir_salidas, f"{nombre_base}_corrupto.txt")
            ruta_salida_json = os.path.join(dir_json, f"{nombre_base}_pistas_reto3.json")
            
            with open(ruta_salida_txt, 'w', encoding='utf-8') as f_txt:
                f_txt.write(texto_corrupto)
                
            with open(ruta_salida_json, 'w', encoding='utf-8') as f_json:
                json.dump(diccionario_pistas, f_json, indent=4, ensure_ascii=False)
                
            messagebox.showinfo(
                "Éxito", 
                f"Archivos generados con ({algo_seleccionado}):\n\n"
                f"• Texto Corrupto: salidas/{os.path.basename(ruta_salida_txt)}\n"
                f"• Pistas de Verificación: json/{os.path.basename(ruta_salida_json)}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al aplicar corrupción:\n{str(e)}")

    def setup_pestana_corregir(self):
        lbl_arreglar = ttk.LabelFrame(self.tab_corregir, text=" Configuración de Restauración ")
        lbl_arreglar.pack(fill="x", padx=20, pady=15)
        
        frame_input = ttk.Frame(lbl_arreglar)
        frame_input.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_input, text="Archivo JSON de Pistas:", width=20, anchor="w").pack(side="left")
        self.ent_json_in = ttk.Entry(frame_input, width=50, state="readonly")
        self.ent_json_in.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(frame_input, text="Buscar JSON", command=self.seleccionar_archivo_json).pack(side="right")
        
        ttk.Button(lbl_arreglar, text="¡Restaurar y Arreglar!", command=self.ejecutar_correccion).pack(pady=10)
        
        self.frame_reporte = ttk.LabelFrame(self.tab_corregir, text=" Reporte y Mensaje Restaurado ")
        self.frame_reporte.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        stats_frame = ttk.Frame(self.frame_reporte)
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        self.lbl_algoritmo = ttk.Label(stats_frame, text="Algoritmo de Verificación: -", font=("Arial", 10))
        self.lbl_algoritmo.pack(anchor="w", pady=2)
        
        self.lbl_total = ttk.Label(stats_frame, text="Total de caracteres: -", font=("Arial", 10))
        self.lbl_total.pack(anchor="w", pady=2)
        
        self.lbl_errores = ttk.Label(stats_frame, text="Errores detectados y corregidos: -", font=("Arial", 10), foreground="red")
        self.lbl_errores.pack(anchor="w", pady=2)
        
        ttk.Label(self.frame_reporte, text="Mensaje Restaurado Limpio:", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.txt_restaurado = tk.Text(self.frame_reporte, height=12, bg="#f4f4f4", font=("Consolas", 10))
        self.txt_restaurado.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.txt_restaurado.config(state="disabled")

    def seleccionar_archivo_json(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON de Pistas", "*.json")])
        if ruta:
            self.ruta_json_pistas = ruta
            self.ent_json_in.config(state="normal")
            self.ent_json_in.delete(0, tk.END)
            self.ent_json_in.insert(0, ruta)
            self.ent_json_in.config(state="readonly")

    def ejecutar_correccion(self):
        if not self.ruta_json_pistas:
            messagebox.showwarning("Advertencia", "Debe cargar un archivo de pistas JSON primero.")
            return
            
        try:
            reporte = procesar_json_checksum(self.ruta_json_pistas)
            mensaje_restaurado = reporte["mensaje_restaurado"]
            errores = reporte["errores_detectados"]
            total = reporte["total_caracteres"]
            
            with open(self.ruta_json_pistas, 'r', encoding='utf-8') as f:
                datos_js = json.load(f)
            alg = datos_js.get("metadata", {}).get("algorithm") or datos_js.get("algoritmo", "Desconocido")
            
            self.lbl_algoritmo.config(text=f"Algoritmo de Verificación: {alg}")
            self.lbl_total.config(text=f"Total de caracteres: {total}")
            self.lbl_errores.config(
                text=f"Errores detectados y corregidos: {errores}",
                foreground="green" if errores == 0 else "red"
            )
            
            self.txt_restaurado.config(state="normal")
            self.txt_restaurado.delete("1.0", "end")
            self.txt_restaurado.insert("end", mensaje_restaurado)
            self.txt_restaurado.config(state="disabled")
            
            proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            os.makedirs(dir_salidas, exist_ok=True)
            
            nombre_base = os.path.splitext(os.path.basename(self.ruta_json_pistas))[0]
            if "_pistas_reto3" in nombre_base:
                nombre_base = nombre_base.replace("_pistas_reto3", "")
            
            ruta_salida_restaurado = os.path.join(dir_salidas, f"{nombre_base}_restaurado.txt")
            
            with open(ruta_salida_restaurado, 'w', encoding='utf-8') as f_out:
                f_out.write(mensaje_restaurado)
                
            messagebox.showinfo(
                "Restauración Completada", 
                f"El mensaje ha sido corregido y guardado con éxito:\n\n"
                f"• Archivo: salidas/{os.path.basename(ruta_salida_restaurado)}\n"
                f"• Errores corregidos: {errores}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al procesar y restaurar:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReto3(root)
    root.mainloop()