"""
Interfaz grafica para el Reto 2
Tiene dos pestañas:
    - Cifrar: recibe un .txt con "mensaje:" y "clave:", genera el .bin
      y el .json de pistas para entregar a los demas grupos.
    - Descifrar: recibe el .bin y .json de otro grupo, ejecuta el
      criptoanalisis automatico y genera un .txt con el resultado
      (clave + mensaje recuperados) y 2 candidatos de respaldo.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

from Cifrado_XOR import (
    cifrar_xor,
    validar_parametros,
    leer_ciphertext_json,
    descifrar_sin_clave,
    descifrar_automatico,
)
from Formato_txt import leer_mensaje_y_clave, escribir_resultado_descifrado

class InterfazXOR: 
    def __init__(self, root):
        self.root = root
        self.root.title("Reto 2 - Cifrado XOR")
        self.root.geometry("700x560")
        self.root.resizable(False, False)
        
        # Prevenir que la ventana se cierre accidentalmente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Traer la ventana al frente y hacerla visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

        self.tab_control = ttk.Notebook(root)

        self.tab_cifrar = ttk.Frame(self.tab_control)
        self.tab_descifrar = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_cifrar, text=" Cifrar ")
        self.tab_control.add(self.tab_descifrar, text=" Descifrar ")
        self.tab_control.pack(expand=1, fill="both")

        self.setup_tab_cifrar()
        self.setup_tab_descifrar()
    
    def on_closing(self):
        """Manejador para cerrar la ventana correctamente"""
        self.root.quit()
        self.root.destroy()

    # Utilidades para seleccionar archivos y gestionar carpetas de salida
    def seleccionar_txt(self, entry_widget):
        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        dir_entrada = os.path.join(proyecto_dir, "Entrada")
        os.makedirs(dir_entrada, exist_ok=True)
        ruta = filedialog.askopenfilename(
            initialdir=dir_entrada,
            filetypes=[("Archivos de Texto", "*.txt")]
        )
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def seleccionar_bin(self, entry_widget):
        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        dir_salidas = os.path.join(proyecto_dir, "Salidas")
        os.makedirs(dir_salidas, exist_ok=True)
        ruta = filedialog.askopenfilename(
            initialdir=dir_salidas,
            filetypes=[("Archivos Binarios", "*.bin")]
        )
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def seleccionar_json(self, entry_widget):
        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        dir_salidas = os.path.join(proyecto_dir, "Salidas")
        os.makedirs(dir_salidas, exist_ok=True)
        ruta = filedialog.askopenfilename(
            initialdir=dir_salidas,
            filetypes=[("Archivos JSON", "*.json")]
        )
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def obtener_carpetas_salida(self):
        """
        Crea (si no existen) y devuelve las rutas de las carpetas usadas
        para guardar los archivos generados, junto al script.
        Estructura dentro de la carpeta "Reto 2":
            Entrada: el .txt a cifrar (entrada del usuario)
            Salidas: .bin y .json generados al cifrar
            Descifrado: .txt con el resultado al descifrar
        """
        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        dir_salidas = os.path.join(proyecto_dir, "Salidas")
        dir_descifrado = os.path.join(proyecto_dir, "Descifrado")
        os.makedirs(dir_salidas, exist_ok=True)
        os.makedirs(dir_descifrado, exist_ok=True)
        return dir_salidas, dir_descifrado

    #  PESTAÑA CIFRAR
    def setup_tab_cifrar(self):
        lbl_info = ttk.LabelFrame(self.tab_cifrar, text="  Cifrado XOR (Reto 2)  ")
        lbl_info.pack(fill="both", expand=True, padx=20, pady=15)

        texto_explicacion = (
            "El archivo .txt de entrada debe tener el siguiente formato:\n\n"
            "    mensaje: el texto que se quiere cifrar\n"
            "    clave: CLAVE123\n\n"
            "Restricciones: la clave debe tener entre 1 y 10 caracteres, el mensaje\n"
            "al menos el doble de caracteres que la clave, y ambos solo ASCII basico."
        )
        ttk.Label(lbl_info, text=texto_explicacion, justify="left", foreground="#444").pack(
            padx=15, pady=10, anchor="w"
        )

        frame_input = ttk.Frame(lbl_info)
        frame_input.pack(fill="x", padx=15, pady=10)
        ttk.Label(frame_input, text="Archivo .txt:", width=12, anchor="w").pack(side="left")
        self.ent_cifrar_txt = ttk.Entry(frame_input, width=42)
        self.ent_cifrar_txt.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(
            frame_input, text="Buscar .txt",
            command=lambda: self.seleccionar_txt(self.ent_cifrar_txt)
        ).pack(side="right")

        # Area donde se muestra el mensaje y clave leidos, para que el usuario confirme
        self.txt_preview_cifrar = tk.Text(
            lbl_info, height=6, width=65, bg="#f4f4f4", state="disabled", font=("Consolas", 10)
        )
        self.txt_preview_cifrar.pack(padx=15, pady=10)

        ttk.Button(
            lbl_info, text=" Cifrar y Generar Archivos ",
            command=self.ejecutar_cifrado, padding=10
        ).pack(pady=10)

    def mostrar_preview_cifrar(self, texto):
        self.txt_preview_cifrar.config(state="normal")
        self.txt_preview_cifrar.delete("1.0", tk.END)
        self.txt_preview_cifrar.insert(tk.END, texto)
        self.txt_preview_cifrar.config(state="disabled")

    def ejecutar_cifrado(self):
        ruta_txt = self.ent_cifrar_txt.get().strip()

        if not ruta_txt:
            messagebox.showwarning("Falta archivo", "Debes seleccionar un archivo .txt de entrada.")
            return

        try:
            mensaje, clave = leer_mensaje_y_clave(ruta_txt)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error al leer el archivo", str(e))
            return

        valido, error = validar_parametros(mensaje, clave)
        if not valido:
            messagebox.showerror("Restricciones no cumplidas", error)
            return

        self.mostrar_preview_cifrar(f"Mensaje leido:\n{mensaje}\n\nClave leida:\n{clave}")

        try:
            bytes_cifrados, estructura_json = cifrar_xor(mensaje, clave)

            dir_salidas, _ = self.obtener_carpetas_salida()
            nombre_base = os.path.splitext(os.path.basename(ruta_txt))[0]

            ruta_bin = os.path.join(dir_salidas, f"{nombre_base}_cifrado.bin")
            ruta_json = os.path.join(dir_salidas, f"{nombre_base}_xor.json")

            with open(ruta_bin, 'wb') as f:
                f.write(bytes_cifrados)
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(estructura_json, f, indent=4, ensure_ascii=False)

            messagebox.showinfo(
                "Cifrado completado",
                f"Archivos generados en la carpeta 'Salidas':\n\n"
                f"{os.path.basename(ruta_bin)}\n"
                f"{os.path.basename(ruta_json)}"
            )

        except Exception as e:
            messagebox.showerror("Error al cifrar", f"No se pudo completar el cifrado:\n{e}")

    #  PESTAÑA DESCIFRAR
    def setup_tab_descifrar(self):
        lbl_info = ttk.LabelFrame(self.tab_descifrar, text="  Descifrado XOR (Reto 2)  ")
        lbl_info.pack(fill="both", expand=True, padx=20, pady=15)

        ttk.Label(
            lbl_info,
            text="Selecciona el .bin y el .json a descifrar\n"
                 "El software analiza automaticamente y determina la clave y el mensaje.",
            justify="center", foreground="#444"
        ).pack(pady=10)

        frame_bin = ttk.Frame(lbl_info)
        frame_bin.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_bin, text="Archivo .bin:", width=12, anchor="w").pack(side="left")
        self.ent_descifrar_bin = ttk.Entry(frame_bin, width=42)
        self.ent_descifrar_bin.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(
            frame_bin, text="Buscar .bin",
            command=lambda: self.seleccionar_bin(self.ent_descifrar_bin)
        ).pack(side="right")

        frame_json = ttk.Frame(lbl_info)
        frame_json.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_json, text="Archivo .json:", width=12, anchor="w").pack(side="left")
        self.ent_descifrar_json = ttk.Entry(frame_json, width=42)
        self.ent_descifrar_json.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(
            frame_json, text="Buscar .json",
            command=lambda: self.seleccionar_json(self.ent_descifrar_json)
        ).pack(side="right")

        # Area donde se muestra el proceso de descifrado, resultados y candidatos de respaldo
        self.txt_diagnostico = tk.Text(
            lbl_info, height=12, width=65, bg="#f4f4f4", state="disabled", font=("Consolas", 10)
        )
        self.txt_diagnostico.pack(padx=15, pady=10)

        ttk.Button(
            lbl_info, text=" Ejecutar Descifrado Automatico ",
            command=self.ejecutar_descifrado, padding=10
        ).pack(pady=5)

    def log_descifrar(self, mensaje):
        self.txt_diagnostico.config(state="normal")
        self.txt_diagnostico.insert(tk.END, mensaje + "\n")
        self.txt_diagnostico.see(tk.END)
        self.txt_diagnostico.config(state="disabled")

    def ejecutar_descifrado(self):
        ruta_bin = self.ent_descifrar_bin.get().strip()
        ruta_json = self.ent_descifrar_json.get().strip()

        if not ruta_bin or not ruta_json:
            messagebox.showwarning("Faltan archivos", "Debes seleccionar tanto el .bin como el .json.")
            return

        self.txt_diagnostico.config(state="normal")
        self.txt_diagnostico.delete("1.0", tk.END)
        self.txt_diagnostico.config(state="disabled")

        self.log_descifrar("[Inicio] Leyendo archivos recibidos...")

        try:
            with open(ruta_bin, 'rb') as f:
                f.read()  # solo se valida que el archivo exista y se pueda abrir
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo .bin:\n{ruta_bin}")
            return

        try:
            bytes_json, metadata = leer_ciphertext_json(ruta_json)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error al leer el JSON", str(e))
            return

        pista_longitud = metadata.get("key_length_hint")
        if pista_longitud:
            self.log_descifrar(f"[Pista] El JSON incluye key_length_hint = {pista_longitud}")

        self.log_descifrar("[Analisis] Probando longitudes de clave del 1 al 10...")
        self.root.update_idletasks()

        try:
            candidatos = descifrar_sin_clave(bytes_json, pista_longitud=pista_longitud)
        except Exception as e:
            self.log_descifrar(f"[Error] Falló el criptoanálisis:\n{e}")
            messagebox.showerror("Error en el descifrado", str(e))
            return

        if not candidatos:
            self.log_descifrar("[Resultado] No se encontró ningún candidato válido.")
            messagebox.showwarning("Sin resultados", "No se pudo recuperar ningún mensaje legible.")
            return

        principal = {
            "clave": candidatos[0][1],
            "mensaje": candidatos[0][3],
            "longitud_clave": candidatos[0][0],
            "confianza": candidatos[0][2],
        }
        respaldo = candidatos[1:3]

        self.log_descifrar(f"\n[Resultado principal]")
        self.log_descifrar(f"  Clave    : {principal['clave']}")
        self.log_descifrar(f"  Mensaje  : {principal['mensaje']}")
        self.log_descifrar(f"  Confianza: {principal['confianza']:.2f}")

        if respaldo:
            self.log_descifrar(f"\n[Candidatos de respaldo]")
            for i, (long, clave, puntaje, texto) in enumerate(respaldo, 2):
                self.log_descifrar(f"  #{i} clave='{clave}' confianza={puntaje:.2f}")
                self.log_descifrar(f"      {texto}")

        try:
            _, dir_descifrado = self.obtener_carpetas_salida()
            nombre_base = os.path.splitext(os.path.basename(ruta_bin))[0]
            ruta_salida = os.path.join(dir_descifrado, f"{nombre_base}_descifrado.txt")

            escribir_resultado_descifrado(ruta_salida, principal, respaldo)

            self.log_descifrar(f"\n[Guardado] {os.path.basename(ruta_salida)}")
            messagebox.showinfo(
                "Descifrado completado",
                f"Resultado guardado en la carpeta 'Descifrado':\n{os.path.basename(ruta_salida)}\n\n"
                f"Clave probable: {principal['clave']}"
            )
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el resultado:\n{e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = InterfazXOR(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("Interfaz cerrada por el usuario")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")