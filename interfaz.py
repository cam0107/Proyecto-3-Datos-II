import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

import gestor_lz77
import huffman
import LZW
import LZ78


class InterfazTorneoAutomatica:
    def __init__(self, root):
        self.root = root
        self.root.title("Torneo de Restauración Temporal - Motor Adaptativo")
        self.root.geometry("780x660")
        self.root.resizable(False, False)

        # Contenedor de pestañas
        self.tab_control = ttk.Notebook(root)

        # Inicializar Frames de pestañas
        self.tab_general = ttk.Frame(self.tab_control)      # Descompresor
        self.tab_doble = ttk.Frame(self.tab_control)        # Compresión Doble Seleccionable
        self.tab_lz77 = ttk.Frame(self.tab_control)
        self.tab_lz78 = ttk.Frame(self.tab_control)
        self.tab_lzw = ttk.Frame(self.tab_control)
        self.tab_huffman = ttk.Frame(self.tab_control)

        # Posicionar las pestañas principales
        self.tab_control.add(self.tab_general, text=" Descompresor General")
        self.tab_control.add(self.tab_doble, text=" Compresión Doble")
        self.tab_control.add(self.tab_lz77, text="LZ77")
        self.tab_control.add(self.tab_lz78, text="LZ78")
        self.tab_control.add(self.tab_lzw, text="LZW")
        self.tab_control.add(self.tab_huffman, text="Huffman")
        self.tab_control.pack(expand=1, fill="both")

        # Configurar las interfaces de cada pestaña
        self.setup_general_tab()
        self.setup_doble_tab()
        self.setup_lz77_tab()
        self.setup_lz78_tab()
        self.setup_lzw_tab()
        self.setup_huffman_tab()

    # --- UTILIDADES DE SELECCIÓN DE ARCHIVOS ---
    def seleccionar_txt(self, entry_widget):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt")])
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def seleccionar_bin(self, entry_widget):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos Binarios", "*.bin")])
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def seleccionar_json(self, entry_widget):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON de Pistas", "*.json")])
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def obtener_rutas_automaticas_compresion(self, ruta_origen, sufijo_algoritmo):
        directorio = os.path.dirname(ruta_origen)
        nombre_base, _ = os.path.splitext(os.path.basename(ruta_origen))
        ruta_bin = os.path.join(directorio, f"{nombre_base}_{sufijo_algoritmo}.bin")
        ruta_json = os.path.join(directorio, f"{nombre_base}_{sufijo_algoritmo}_pistas.json")
        return ruta_bin, ruta_json


    # =========================================================================
    #  DESCOMPRESOR GENERAL ADAPTATIVO UNIVERSAL (CUALQUIER ORDEN)
    # =========================================================================
    def setup_general_tab(self):
        lbl_desc = ttk.LabelFrame(self.tab_general, text="  Motor de Descompresión Adaptativo (Cualquier Combinación/Orden) ")
        lbl_desc.pack(fill="both", expand=True, padx=20, pady=15)

        lbl_info = ttk.Label(lbl_desc, text="Detecta y procesa de manera automática cualquier orden de algoritmos en cascada.\n"
                                            "Soporta decodificación segura por tuberías binarias, de texto y hexadecimales.",
                             justify="center", foreground="green")
        lbl_info.pack(pady=10)

        # Entrada de Archivo Binario (.bin)
        frame_bin = ttk.Frame(lbl_desc)
        frame_bin.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_bin, text="Archivo .bin:", width=15, anchor="w").pack(side="left")
        self.ent_general_bin = ttk.Entry(frame_bin, width=45)
        self.ent_general_bin.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(frame_bin, text="Buscar .bin", command=lambda: self.seleccionar_bin(self.ent_general_bin)).pack(side="right")

        # Entrada de Archivo de Pistas (.json)
        frame_json = ttk.Frame(lbl_desc)
        frame_json.pack(fill="x", padx=15, pady=5)
        ttk.Label(frame_json, text="Archivo .json:", width=15, anchor="w").pack(side="left")
        self.ent_general_json = ttk.Entry(frame_json, width=45)
        self.ent_general_json.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(frame_json, text="Buscar .json", command=lambda: self.seleccionar_json(self.ent_general_json)).pack(side="right")

        # Área de log de diagnóstico en tiempo real
        self.txt_diagnostico = tk.Text(lbl_desc, height=12, width=65, bg="#f4f4f4", state="disabled", font=("Consolas", 10))
        self.txt_diagnostico.pack(padx=15, pady=10)

        # Botón de ejecución
        ttk.Button(lbl_desc, text=" Ejecutar Descompresión Adaptativa Universal", 
                   command=self.ejecutar_descompresion_general_universal, padding=10).pack(pady=5)

    def log_general(self, mensaje):
        self.txt_diagnostico.config(state="normal")
        self.txt_diagnostico.insert(tk.END, mensaje + "\n")
        self.txt_diagnostico.see(tk.END)
        self.txt_diagnostico.config(state="disabled")

    def ejecutar_descompresion_general_universal(self):
        orig_bin = self.ent_general_bin.get()
        orig_json = self.ent_general_json.get()

        if not orig_bin or not orig_json:
            messagebox.showwarning("Faltan datos", "Debes seleccionar tanto el archivo .bin como el .json.")
            return

        self.txt_diagnostico.config(state="normal")
        self.txt_diagnostico.delete("1.0", tk.END)
        self.txt_diagnostico.config(state="disabled")

        self.log_general("[Inicio] Analizando topología de las pistas...")

        directorio = os.path.dirname(orig_bin)
        nombre_base = os.path.splitext(os.path.basename(orig_bin))[0]
        ruta_txt_out = os.path.join(directorio, f"{nombre_base}_RESTAURADO.txt")

        try:
            with open(orig_json, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
            
            compresiones = datos_json.get("compresion", [])
            
            capas_reales = []
            for bloque in compresiones:
                algoritmo = bloque.get("algoritmo")
                estructura = bloque.get("estructura", {})
                
                if algoritmo == "Huffman" and estructura.get("arbol") is not None:
                    capas_reales.append(bloque)
                elif algoritmo == "LZ77" and len(estructura.get("tripletas", [])) > 0:
                    capas_reales.append(bloque)
                elif (algoritmo in ["LZ78", "LZ8"]) and (len(estructura.get("diccionario", [])) > 0 or estructura.get("nodos") is not None or "salida" in estructura):
                    capas_reales.append(bloque)
                elif algoritmo == "LZW" and ("salida" in estructura or len(estructura.get("salida", [])) > 0):
                    capas_reales.append(bloque)

            if not capas_reales:
                raise ValueError("El JSON no contiene estructuras o capas de algoritmos válidas.")

            self.log_general(f"[Info] Se detectaron {len(capas_reales)} capa(s) válida(s) en las pistas.")

            # --- LEER LA ENVOLTURA MÁS EXTERNA ---
            with open(orig_bin, 'rb') as f_b:
                datos_actuales = f_b.read()

            # Descomprimir capa por capa de afuera hacia adentro
            for idx, capa in enumerate(capas_reales):
                algoritmo = capa.get("algoritmo")
                estructura = capa.get("estructura", {})
                self.log_general(f"[Capa {idx+1}/{len(capas_reales)}] Removiendo algoritmo: {algoritmo}")

                # --- CONTROL DE TRANSICIÓN INTEGRAL (DE-SERIALIZACIÓN) ---
                if isinstance(datos_actuales, bytes) and idx > 0:
                    try:
                        texto_str = datos_actuales.decode('utf-8', errors='ignore').strip()
                        # Si la capa intermedia fue codificada en hexadecimal seguro, la revertimos a bytes
                        if all(c in '0123456789abcdefABCDEF' for c in texto_str) and len(texto_str) % 2 == 0:
                            if algoritmo != "Huffman":
                                datos_actuales = bytes.fromhex(texto_str)
                    except Exception:
                        pass

                texto_descomprimido = ""

                # --- PROCESAMIENTO POR ALGORITMO ---
                if algoritmo == "Huffman":
                    if isinstance(datos_actuales, bytes):
                        bit_string = datos_actuales.decode('utf-8', errors='ignore').strip()
                    else:
                        bit_string = str(datos_actuales).strip()
                    
                    # Filtro absoluto para eliminar impurezas tipográficas residuales
                    bit_string = "".join([c for c in bit_string if c in ('0', '1')])
                    
                    root_node = huffman.deserialize_tree(estructura.get("arbol"))
                    texto_descomprimido = huffman.decode_bits(bit_string, root_node)

                elif algoritmo == "LZW":
                    codigos_lzw = []
                    if isinstance(datos_actuales, bytes):
                        try:
                            string_codigos = datos_actuales.decode('utf-8').strip()
                            codigos_lzw = list(map(int, string_codigos.split()))
                        except Exception:
                            codigos_lzw = []
                            for i in range(0, len(datos_actuales), 2):
                                if i+2 <= len(datos_actuales):
                                    codigos_lzw.append(int.from_bytes(datos_actuales[i:i+2], byteorder='big'))
                    else:
                        codigos_lzw = list(map(int, str(datos_actuales).strip().split()))

                    # Fallback defensivo: extraer códigos directamente del JSON de pistas si falló el parseo
                    if not codigos_lzw and "salida" in estructura:
                        codigos_lzw = estructura.get("salida", [])

                    texto_descomprimido = LZW.lzw_decompress(codigos_lzw)

                elif algoritmo in ["LZ78", "LZ8"]:
                    if isinstance(datos_actuales, str):
                        datos_actuales = datos_actuales.encode('utf-8')
                    texto_descomprimido = LZ78.descomprimir_lz78(datos_actuales)

                elif algoritmo == "LZ77":
                    if isinstance(datos_actuales, str):
                        datos_actuales = datos_actuales.encode('utf-8')
                        
                    r_t_bin, r_t_json, r_t_txt = "t_gen_lz77.bin", "t_gen_lz77.json", "t_gen_lz77.txt"
                    with open(r_t_bin, 'wb') as f_t: f_t.write(datos_actuales)
                    with open(r_t_json, 'w', encoding='utf-8') as f_j: json.dump({"compresion": [capa]}, f_j)
                    
                    gestor_lz77.descomprimir_archivo(r_t_bin, r_t_json, r_t_txt)
                    with open(r_t_txt, 'r', encoding='utf-8') as f_r: texto_descomprimido = f_r.read()
                    
                    for f_del in [r_t_bin, r_t_json, r_t_txt]:
                        if os.path.exists(f_del): os.remove(f_del)

                # --- CONTROL DE SALIDA DE CAPA ---
                if idx < len(capas_reales) - 1:
                    try:
                        # Si el texto es una representación hexadecimal intermedia, lo pasamos como bytes nativos
                        if all(c in '0123456789abcdefABCDEF' for c in texto_descomprimido) and len(texto_descomprimido) % 2 == 0:
                            datos_actuales = bytes.fromhex(texto_descomprimido)
                        else:
                            datos_actuales = texto_descomprimido.encode('utf-8')
                    except Exception:
                        datos_actuales = texto_descomprimido.encode('utf-8')
                else:
                    datos_actuales = texto_descomprimido.encode('utf-8')

            # --- ESCRITURA FINAL DE RESULTADOS ---
            with open(ruta_txt_out, 'w', encoding='utf-8') as f_out:
                f_out.write(datos_actuales.decode('utf-8', errors='ignore'))

            self.log_general(f"\n[Terminado] Archivo restaurado de forma exitosa.")
            self.log_general(f"[Salida] {os.path.basename(ruta_txt_out)}")
            messagebox.showinfo("¡Éxito Total!", f"Proceso Completado.\nGuardado como: {os.path.basename(ruta_txt_out)}")

        except Exception as e:
            self.log_general(f"[Fallo] Error en la cadena de descompresión: {e}")
            messagebox.showerror("Error de Pipeline", f"No se pudo restaurar el archivo:\n{e}")


    # =========================================================================
    # COMPRESIÓN DOBLE TOTALMENTE CONFIGURABLE (UNIVERSAL)
    # =========================================================================
    def setup_doble_tab(self):
        lbl_comp = ttk.LabelFrame(self.tab_doble, text="  Compresión Avanzada Configurable en Cascada (Universal) ")
        lbl_comp.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_explicacion = ttk.Label(lbl_comp, text="Selecciona libremente qué algoritmo aplicar primero y cuál aplicar sobre el anterior.\n"
                                                  "La interfaz adaptará el flujo de bytes usando un puente seguro para evitar pérdidas de datos.",
                                   justify="center", foreground="purple")
        lbl_explicacion.pack(pady=10)

        # Selección de Algoritmos
        frame_combos = ttk.Frame(lbl_comp)
        frame_combos.pack(pady=15)

        listado_algoritmos = ["LZW", "Huffman", "LZ77", "LZ78"]

        ttk.Label(frame_combos, text="1er Algoritmo (Interno - Se aplica primero): ").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cmb_algo1 = ttk.Combobox(frame_combos, values=listado_algoritmos, state="readonly", width=15)
        self.cmb_algo1.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_algo1.set("LZW")

        ttk.Label(frame_combos, text="2do Algoritmo (Externo - Se aplica de segundo): ").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.cmb_algo2 = ttk.Combobox(frame_combos, values=listado_algoritmos, state="readonly", width=15)
        self.cmb_algo2.grid(row=1, column=1, padx=5, pady=5)
        self.cmb_algo2.set("Huffman")

        # Selector de Archivo Origen
        frame_input = ttk.Frame(lbl_comp)
        frame_input.pack(fill="x", padx=15, pady=15)

        self.ent_doble_in = ttk.Entry(frame_input, width=50)
        self.ent_doble_in.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(frame_input, text="Seleccionar TXT", command=lambda: self.seleccionar_txt(self.ent_doble_in)).pack(side="right")

        ttk.Button(lbl_comp, text=" Ejecutar Compresión Doble en Cascada", 
                   command=self.ejecutar_compresion_doble_dinamica, padding=12).pack(pady=15)

    def ejecutar_compresion_doble_dinamica(self):
        orig = self.ent_doble_in.get()
        algo1 = self.cmb_algo1.get()
        algo2 = self.cmb_algo2.get()

        if not orig:
            messagebox.showwarning("Archivo faltante", "Por favor selecciona un archivo .txt para comprimir.")
            return

        try:
            sufijo = f"Doble_{algo1}_y_{algo2}"
            r_bin, r_json = self.obtener_rutas_automaticas_compresion(orig, sufijo)
            
            pistas_capa_1 = None
            pistas_capa_2 = None

            with open(orig, 'r', encoding='utf-8') as f:
                texto_original = f.read()

            # --- CAPA 1: EJECUTAR EL PRIMER ALGORITMO (INTERNO) ---
            string_puente_intermedio = ""

            if algo1 == "LZW":
                codigos, dicc = LZW.lzw_compress(texto_original)
                texto_salida = " ".join(map(str, codigos))
                string_puente_intermedio = texto_salida.encode('utf-8').hex()
                pistas_capa_1 = {
                    "algoritmo": "LZW",
                    "estructura": { "salida": codigos, "diccionario": {str(k): v for k, v in dicc.items()} }
                }
            elif algo1 == "Huffman":
                root = huffman.build_huffman_tree(texto_original)
                codes = huffman.generate_codes(root)
                string_puente_intermedio = huffman.encode_text(texto_original, codes)
                pistas_capa_1 = huffman.generate_json_structure(root, codes)["compresion"][0]
            elif algo1 == "LZ78":
                bytes_res, estructura = LZ78.comprimir_lz78(texto_original)
                string_puente_intermedio = bytes_res.hex()
                pistas_capa_1 = estructura
            elif algo1 == "LZ77":
                gestor_lz77.comprimir_archivo(orig, "t_c1.bin", "t_c1.json")
                with open("t_c1.bin", 'rb') as f_b: bytes_c1 = f_b.read()
                string_puente_intermedio = bytes_c1.hex()
                with open("t_c1.json", 'r', encoding='utf-8') as f_j: js_t = json.load(f_j)
                pistas_capa_1 = js_t["compresion"][0]
                for f_del in ["t_c1.bin", "t_c1.json"]: 
                    if os.path.exists(f_del): os.remove(f_del)

            # Guardamos el archivo puente temporal
            with open("temp_puente.txt", "w", encoding="utf-8") as f_p:
                f_p.write(string_puente_intermedio)

            # --- CAPA 2: EJECUTAR EL SEGUNDO ALGORITMO (EXTERNO) ---
            if algo2 == "LZW":
                codigos, dicc = LZW.lzw_compress(string_puente_intermedio)
                LZW.guardar_archivo_binario(codigos, r_bin)
                pistas_capa_2 = {
                    "algoritmo": "LZW",
                    "estructura": { "salida": codigos, "diccionario": {str(k): v for k, v in dicc.items()} }
                }
            elif algo2 == "Huffman":
                root = huffman.build_huffman_tree(string_puente_intermedio)
                codes = huffman.generate_codes(root)
                bits_finales = huffman.encode_text(string_puente_intermedio, codes)
                with open(r_bin, 'w', encoding='utf-8') as f_out: f_out.write(bits_finales)
                pistas_capa_2 = huffman.generate_json_structure(root, codes)["compresion"][0]
            elif algo2 == "LZ78":
                bytes_res, estructura = LZ78.comprimir_lz78(string_puente_intermedio)
                with open(r_bin, 'wb') as f_out: f_out.write(bytes_res)
                pistas_capa_2 = estructura
            elif algo2 == "LZ77":
                gestor_lz77.comprimir_archivo("temp_puente.txt", r_bin, "t_c2.json")
                with open("t_c2.json", 'r', encoding='utf-8') as f_j: js_t = json.load(f_j)
                pistas_capa_2 = js_t["compresion"][0]
                if os.path.exists("t_c2.json"): os.remove("t_c2.json")

            if os.path.exists("temp_puente.txt"): os.remove("temp_puente.txt")

            # Estructurar JSON Final (Manteniendo el orden inverso para el descompresor)
            json_final = {
                "compresion": [
                    pistas_capa_2,  
                    pistas_capa_1   
                ]
            }

            with open(r_json, 'w', encoding='utf-8') as f_j:
                json.dump(json_final, f_j, indent=4, ensure_ascii=False)

            messagebox.showinfo("¡Éxito!", f"Compresión en Cascada [{algo1} + {algo2}] generada con éxito.\n"
                                           f"Archivos guardados correctamente.")

        except Exception as e:
            messagebox.showerror("Error en Cascada", f"No se pudo completar la compresión elegida:\n{e}")


    # =========================================================================
    # PESTAÑAS INDIVIDUALES ESPECÍFICAS (MANTENIDAS POR COMPATIBILIDAD)
    # =========================================================================
    def setup_lz77_tab(self):
        lbl_comp = ttk.LabelFrame(self.tab_lz77, text=" Compresión ")
        lbl_comp.pack(fill="x", padx=15, pady=10)
        self.ent_lz77_in = ttk.Entry(lbl_comp, width=55)
        self.ent_lz77_in.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_comp, text="Buscar TXT", command=lambda: self.seleccionar_txt(self.ent_lz77_in)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_comp, text="¡Comprimir!", command=self.ejecutar_lz77_comp).grid(row=1, column=0, columnspan=2, pady=5)

        lbl_desc = ttk.LabelFrame(self.tab_lz77, text=" Descompresión Específica ")
        lbl_desc.pack(fill="x", padx=15, pady=10)
        self.ent_lz77_bin_d = ttk.Entry(lbl_desc, width=40)
        self.ent_lz77_bin_d.grid(row=0, column=0, padx=5, pady=10)
        ttk.Button(lbl_desc, text="Buscar .bin", command=lambda: self.seleccionar_bin(self.ent_lz77_bin_d)).grid(row=0, column=1, padx=2)
        self.ent_lz77_json_d = ttk.Entry(lbl_desc, width=40)
        self.ent_lz77_json_d.grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(lbl_desc, text="Buscar .json", command=lambda: self.seleccionar_json(self.ent_lz77_json_d)).grid(row=1, column=1, padx=2)
        ttk.Button(lbl_desc, text="¡Descomprimir!", command=self.ejecutar_lz77_desc).grid(row=2, column=0, columnspan=2, pady=5)

    def ejecutar_lz77_comp(self):
        orig = self.ent_lz77_in.get()
        if not orig: return
        try:
            r_bin, r_json = self.obtener_rutas_automaticas_compresion(orig, "LZ77")
            gestor_lz77.comprimir_archivo(orig, r_bin, r_json)
            messagebox.showinfo("Éxito", "LZ77 Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lz77_desc(self):
        b, j = self.ent_lz77_bin_d.get(), self.ent_lz77_json_d.get()
        if not b or not j: return
        try:
            r_out = os.path.splitext(b)[0] + "_restaurado.txt"
            gestor_lz77.descomprimir_archivo(b, j, r_out)
            messagebox.showinfo("Éxito", "Restaurado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def setup_lz78_tab(self):
        lbl_comp = ttk.LabelFrame(self.tab_lz78, text=" Compresión ")
        lbl_comp.pack(fill="x", padx=15, pady=10)
        self.ent_lz78_in = ttk.Entry(lbl_comp, width=55)
        self.ent_lz78_in.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_comp, text="Buscar TXT", command=lambda: self.seleccionar_txt(self.ent_lz78_in)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_comp, text="¡Comprimir!", command=self.ejecutar_lz78_comp).grid(row=1, column=0, columnspan=2, pady=5)

        lbl_desc = ttk.LabelFrame(self.tab_lz78, text=" Descompresión Específica ")
        lbl_desc.pack(fill="x", padx=15, pady=10)
        self.ent_lz78_bin_d = ttk.Entry(lbl_desc, width=55)
        self.ent_lz78_bin_d.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_desc, text="Buscar .bin", command=lambda: self.seleccionar_bin(self.ent_lz78_bin_d)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_desc, text="¡Descomprimir!", command=self.ejecutar_lz78_desc).grid(row=1, column=0, columnspan=2, pady=5)

    def ejecutar_lz78_comp(self):
        orig = self.ent_lz78_in.get()
        if not orig: return
        try:
            r_bin, r_json = self.obtener_rutas_automaticas_compresion(orig, "LZ78")
            with open(orig, 'r', encoding='utf-8') as f: texto = f.read()
            bytes_comp, estructura_pistas = LZ78.comprimir_lz78(texto)
            with open(r_bin, 'wb') as f_bin: f_bin.write(bytes_comp)
            with open(r_json, 'w', encoding='utf-8') as f_json: json.dump({"compresion": [estructura_pistas]}, f_json, indent=4)
            messagebox.showinfo("Éxito", "LZ78 Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lz78_desc(self):
        b = self.ent_lz78_bin_d.get()
        if not b: return
        try:
            r_out = os.path.splitext(b)[0] + "_restaurado.txt"
            with open(b, 'rb') as f_bin: bytes_leidos = f_bin.read()
            texto_recuperado = LZ78.descomprimir_lz78(bytes_leidos)
            with open(r_out, 'w', encoding='utf-8') as f_out: f_out.write(texto_recuperado)
            messagebox.showinfo("Éxito", "Restaurado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def setup_lzw_tab(self):
        lbl_comp = ttk.LabelFrame(self.tab_lzw, text=" Compresión ")
        lbl_comp.pack(fill="x", padx=15, pady=10)
        self.ent_lzw_in = ttk.Entry(lbl_comp, width=55)
        self.ent_lzw_in.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_comp, text="Buscar TXT", command=lambda: self.seleccionar_txt(self.ent_lzw_in)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_comp, text="¡Comprimir!", command=self.ejecutar_lzw_comp).grid(row=1, column=0, columnspan=2, pady=5)

        lbl_desc = ttk.LabelFrame(self.tab_lzw, text=" Descompresión Específica ")
        lbl_desc.pack(fill="x", padx=15, pady=10)
        self.ent_lzw_bin_d = ttk.Entry(lbl_desc, width=55)
        self.ent_lzw_bin_d.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_desc, text="Buscar .bin", command=lambda: self.seleccionar_bin(self.ent_lzw_bin_d)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_desc, text="¡Descomprimir!", command=self.ejecutar_lzw_desc).grid(row=1, column=0, columnspan=2, pady=5)

    def ejecutar_lzw_comp(self):
        orig = self.ent_lzw_in.get()
        if not orig: return
        try:
            r_bin, r_json = self.obtener_rutas_automaticas_compresion(orig, "LZW")
            with open(orig, 'r', encoding='utf-8') as f: texto = f.read()
            codigos, diccionario_final = LZW.lzw_compress(texto)
            LZW.guardar_archivo_binario(codigos, r_bin)
            LZW.generar_archivo_pistas_json(texto, codigos, diccionario_final, r_json)
            messagebox.showinfo("Éxito", "LZW Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lzw_desc(self):
        b = self.ent_lzw_bin_d.get()
        if not b: return
        try:
            r_out = os.path.splitext(b)[0] + "_restaurado.txt"
            codigos_extraidos = LZW.leer_archivo_binario(b)
            texto_restaurado = LZW.lzw_decompress(codigos_extraidos)
            with open(r_out, "w", encoding="utf-8") as f: f.write(texto_restaurado)
            messagebox.showinfo("Éxito", "Restaurado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def setup_huffman_tab(self):
        lbl_comp = ttk.LabelFrame(self.tab_huffman, text=" Compresión ")
        lbl_comp.pack(fill="x", padx=15, pady=10)
        self.ent_huff_in = ttk.Entry(lbl_comp, width=55)
        self.ent_huff_in.grid(row=0, column=0, padx=10, pady=15)
        ttk.Button(lbl_comp, text="Buscar TXT", command=lambda: self.seleccionar_txt(self.ent_huff_in)).grid(row=0, column=1, padx=5)
        ttk.Button(lbl_comp, text="¡Comprimir!", command=self.ejecutar_huffman_comp).grid(row=1, column=0, columnspan=2, pady=5)

        lbl_desc = ttk.LabelFrame(self.tab_huffman, text=" Descompresión Específica ")
        lbl_desc.pack(fill="x", padx=15, pady=10)
        self.ent_huff_bin_d = ttk.Entry(lbl_desc, width=40)
        self.ent_huff_bin_d.grid(row=0, column=0, padx=5, pady=10)
        ttk.Button(lbl_desc, text="Buscar .bin", command=lambda: self.seleccionar_bin(self.ent_huff_bin_d)).grid(row=0, column=1, padx=2)
        self.ent_huff_json_d = ttk.Entry(lbl_desc, width=40)
        self.ent_huff_json_d.grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(lbl_desc, text="Buscar .json", command=lambda: self.seleccionar_json(self.ent_huff_json_d)).grid(row=1, column=1, padx=2)
        ttk.Button(lbl_desc, text="¡Descomprimir!", command=self.ejecutar_huffman_desc).grid(row=2, column=0, columnspan=2, pady=5)

    def ejecutar_huffman_comp(self):
        orig = self.ent_huff_in.get()
        if not orig: return
        try:
            r_bin, r_json = self.obtener_rutas_automaticas_compresion(orig, "Huffman")
            with open(orig, 'r', encoding='utf-8') as f: texto = f.read()
            root_node = huffman.build_huffman_tree(texto)
            codes = huffman.generate_codes(root_node)
            encoded_text = huffman.encode_text(texto, codes)
            with open(r_bin, 'w', encoding='utf-8') as f_bin: f_bin.write(encoded_text)
            pistas = huffman.generate_json_structure(root_node, codes)
            with open(r_json, 'w', encoding='utf-8') as f_json: json.dump(pistas, f_json, indent=4)
            messagebox.showinfo("Éxito", "Huffman Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_huffman_desc(self):
        b, j = self.ent_huff_bin_d.get(), self.ent_huff_json_d.get()
        if not b or not j: return
        try:
            r_out = os.path.splitext(b)[0] + "_restaurado.txt"
            with open(b, 'r', encoding='utf-8') as f_bin: bit_string = f_bin.read()
            with open(j, 'r', encoding='utf-8') as f_json: datos_json = json.load(f_json)
            estructura_arbol = datos_json["compresion"][0]["estructura"]["arbol"]
            root_node = huffman.deserialize_tree(estructura_arbol)
            texto_recuperado = huffman.decode_bits(bit_string, root_node)
            with open(r_out, 'w', encoding='utf-8') as f_out: f_out.write(texto_recuperado)
            messagebox.showinfo("Éxito", "Restaurado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazTorneoAutomatica(root)
    root.mainloop()