import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

import gestor_lz77
import huffman
import LZW
import LZ78


def detectar_algoritmo_real(datos, datos_json=None):
    """
    detectar qué algoritmo corresponde a los datos (bytes o string).
    Si datos_json está disponible, valida las firmas de los datos contra el JSON para evitar despistes.
    """
    algoritmos_disponibles = None
    if datos_json: # Extraemos los algoritmos disponibles del JSON para validar solo contra esos
        algoritmos_disponibles = {
            b.get("algoritmo")
            for b in datos_json.get("compresion", [])
            if isinstance(b, dict) and b.get("algoritmo")
        }

    if isinstance(datos, bytes) and datos_json: # Si tenemos datos JSON, validamos contra las estructuras de salida de cada algoritmo para evitar falsos positivos
        compresiones = datos_json.get("compresion", [])

        # Primero intentamos coincidencias exactas de las capas binarias.
        lzw_salida = None
        for b in compresiones:
            if b.get("algoritmo") == "LZW":
                lzw_salida = b.get("estructura", {}).get("salida")
                break
        if lzw_salida:
            import struct
            if len(datos) % 2 == 0:
                unpacked_lzw = []
                for i in range(0, len(datos), 2):
                    unpacked_lzw.append(struct.unpack('H', datos[i:i+2])[0])
                if unpacked_lzw == lzw_salida:
                    return "LZW"

        lz78_salida = None
        for b in compresiones:
            if b.get("algoritmo") == "LZ78":
                lz78_salida = b.get("estructura", {}).get("salida")
                break
        if lz78_salida:
            import struct
            if len(datos) % 3 == 0:
                unpacked_lz78 = []
                for i in range(0, len(datos), 3):
                    idx, sym_byte = struct.unpack('>Hc', datos[i:i+3])
                    sym = "" if sym_byte == b'\x00' else sym_byte.decode('utf-8', errors='ignore')
                    unpacked_lz78.append({"indice": idx, "simbolo": sym})
                if unpacked_lz78 == lz78_salida:
                    return "LZ78"



    try:
        if isinstance(datos, bytes):
            # Si contiene ceros y unos legibles en ASCII (Huffman en formato texto)
            if all(b_val in (0x30, 0x31, 0x0a, 0x0d, 0x20) for b_val in datos):
                text = datos.decode('utf-8', errors='ignore').strip()
            else:
                text = datos.decode('utf-8', errors='strict').strip()
        else:
            text = str(datos).strip()
            
        # 1. LZ77 check (parentesis y comas)
        if (algoritmos_disponibles is None or "LZ77" in algoritmos_disponibles) and (text.startswith('(') or '(' in text):
            if ',' in text and ')' in text:
                return "LZ77"
                
        # 2. Huffman check (solo '0' y '1')
        if (algoritmos_disponibles is None or "Huffman" in algoritmos_disponibles) and text and all(c in ('0', '1') for c in text):
            return "Huffman"
            
        # 3. LZW text check (enteros separados por espacio)
        if (algoritmos_disponibles is None or "LZW" in algoritmos_disponibles) and text and all(w.isdigit() for w in text.split()):
            return "LZW"
    except Exception:
        pass
        
    # 4. Binary check
    if isinstance(datos, bytes):
        length = len(datos)
        if length > 0:
            # Si tenemos datos_json, podemos validar con precisión del 100%
            if datos_json:
                compresiones = datos_json.get("compresion", [])
                
                # --- A. Verificar LZW ---
                lzw_salida = None
                for b in compresiones:
                    if b.get("algoritmo") == "LZW":
                        lzw_salida = b.get("estructura", {}).get("salida")
                        break
                if lzw_salida:
                    # Desempaquetar LZW (16-bit)
                    import struct
                    unpacked_lzw = []
                    for i in range(0, length, 2):
                        if i+2 <= length:
                            unpacked_lzw.append(struct.unpack('H', datos[i:i+2])[0])
                    if unpacked_lzw == lzw_salida:
                        return "LZW"
                
                # --- B. Verificar LZ78 ---
                lz78_salida = None
                for b in compresiones:
                    if b.get("algoritmo") == "LZ78":
                        lz78_salida = b.get("estructura", {}).get("salida")
                        break
                if lz78_salida:
                    # Desempaquetar LZ78 (3 bytes: Hc)
                    import struct
                    unpacked_lz78 = []
                    for i in range(0, length, 3):
                        if i+3 <= length:
                            idx, sym_byte = struct.unpack('>Hc', datos[i:i+3])
                            sym = "" if sym_byte == b'\x00' else sym_byte.decode('utf-8', errors='ignore')
                            unpacked_lz78.append({"indice": idx, "simbolo": sym})
                    if unpacked_lz78 == lz78_salida:
                        return "LZ78"
                
                # --- C. Verificar Huffman ---
                huffman_struct = None
                for b in compresiones:
                    if b.get("algoritmo") == "Huffman":
                        huffman_struct = b.get("estructura", {})
                        break
                if huffman_struct and "arbol" in huffman_struct and "tabla_codigos" in huffman_struct:
                    try:
                        root = huffman.deserialize_tree(huffman_struct.get("arbol"))
                        codes = huffman_struct.get("tabla_codigos", {})
                        bit_string = datos.decode('ascii', errors='replace').strip()
                        decoded_text = huffman.decode_bits(bit_string, root)
                        if huffman.encode_text(decoded_text, codes).encode('ascii', errors='replace') == datos:
                            return "Huffman"
                    except Exception:
                        pass



            # Si hay JSON disponible y no hubo coincidencia exacta, no adivinamos
            # por longitud: eso puede confundir texto plano con una capa comprimida.
            if datos_json:
                return None

            # Fallback si datos_json es None
            is_lz78_possible = (length % 3 == 0)
            is_lzw_possible = (length % 2 == 0)
            
            if is_lz78_possible and not is_lzw_possible:
                return "LZ78"
            if is_lzw_possible and not is_lz78_possible:
                return "LZW"
            if is_lz78_possible and is_lzw_possible:
                import struct
                codes = []
                for i in range(0, length, 2):
                    if i+2 <= length:
                        codes.append(struct.unpack('H', datos[i:i+2])[0])
                
                max_valid_code = 256 + len(codes)
                lzw_valid = True
                for c in codes:
                    if c >= max_valid_code:
                        lzw_valid = False
                        break
                if lzw_valid:
                    return "LZW"
                else:
                    return "LZ78"
            return "LZW" # Default fallback
            
    return None


def generar_json_final_competicion(texto_original, pistas_reales=None):
    """
    Genera un JSON completo.
    Si un algoritmo está en pistas_reales, usa esa estructura real (que puede provenir de una capa intermedia).
    Para los algoritmos que no están en pistas_reales, genera su estructura en memoria a partir del texto_original.
    """
    if pistas_reales is None:
        pistas_reales = {}
        
    import huffman
    import lz77
    import LZ78
    import LZW

    # 1. Huffman
    if "Huffman" in pistas_reales:
        est_huffman = pistas_reales["Huffman"]
    else:
        try:
            root = huffman.build_huffman_tree(texto_original)
            codes = huffman.generate_codes(root)
            est_huffman = huffman.generate_json_structure(root, codes)["compresion"][0]["estructura"]
        except Exception:
            est_huffman = {}

    # 2. LZ77
    if "LZ77" in pistas_reales:
        est_lz77 = pistas_reales["LZ77"]
    else:
        try:
            lz_obj = lz77.LZ77(ventana=20)
            tripletas = lz_obj.comprimir(texto_original)
            est_lz77 = {
                "tamano_buffer_busqueda": 20,
                "tamano_buffer_lectura": 10,
                "tripletas": []
            }
            for idx, (offset, longitud, siguiente) in enumerate(tripletas):
                offset_val = "_" if idx == 0 else offset
                siguiente_val = "_" if (siguiente == "" or siguiente is None) else siguiente
                est_lz77["tripletas"].append({
                    "offset": offset_val,
                    "longitud": longitud,
                    "siguiente": siguiente_val
                })
        except Exception:
            est_lz77 = {}

    # 3. LZ78
    if "LZ78" in pistas_reales:
        est_lz78 = pistas_reales["LZ78"]
    else:
        try:
            _, est_lz78_wrapper = LZ78.comprimir_lz78(texto_original)
            est_lz78 = est_lz78_wrapper["estructura"]
        except Exception:
            est_lz78 = {}

    # 4. LZW
    if "LZW" in pistas_reales:
        est_lzw = pistas_reales["LZW"]
    else:
        try:
            codigos, diccionario_final = LZW.lzw_compress(texto_original)
            diccionario_inicial = {chr(i): i for i in range(256)}
            diccionario_generado_lista = []
            for cadena, codigo in diccionario_final.items():
                if codigo >= 256:
                    diccionario_generado_lista.append({
                        "codigo": codigo,
                        "cadena": cadena
                    })
            est_lzw = {
                "diccionario_inicial": diccionario_inicial,
                "diccionario_generado": diccionario_generado_lista,
                "salida": codigos
            }
        except Exception:
            est_lzw = {}

    return {
        "compresion": [
            { "algoritmo": "Huffman", "estructura": est_huffman },
            { "algoritmo": "LZ77", "estructura": est_lz77 },
            { "algoritmo": "LZ78", "estructura": est_lz78 },
            { "algoritmo": "LZW", "estructura": est_lzw }
        ]
    }


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
        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        nombre_base, _ = os.path.splitext(os.path.basename(ruta_origen))
        
        dir_bin = os.path.join(proyecto_dir, "comprimidos")
        dir_json = os.path.join(proyecto_dir, "json")
        
        os.makedirs(dir_bin, exist_ok=True)
        os.makedirs(dir_json, exist_ok=True)
        
        ruta_bin = os.path.join(dir_bin, f"{nombre_base}_{sufijo_algoritmo}.bin")
        ruta_json = os.path.join(dir_json, f"{nombre_base}_{sufijo_algoritmo}.json")
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

        proyecto_dir = os.path.dirname(os.path.abspath(__file__))
        dir_salidas = os.path.join(proyecto_dir, "salidas")
        os.makedirs(dir_salidas, exist_ok=True)
        nombre_base = os.path.splitext(os.path.basename(orig_bin))[0]
        ruta_txt_out = os.path.join(dir_salidas, f"{nombre_base}_restaurado.txt")

        try:
            with open(orig_json, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
            
            compresiones = datos_json.get("compresion", [])
            
            # --- LEER LA ENVOLTURA MÁS EXTERNA ---
            with open(orig_bin, 'rb') as f_b:
                datos_actuales = f_b.read()

            pasos_realizados = 0
            max_pasos = 2 # Se permite un máximo de 2 algoritmos de compresión en cascada según las reglas

            while pasos_realizados < max_pasos:
                algoritmo = detectar_algoritmo_real(datos_actuales, datos_json)
                if not algoritmo:
                    break
                
                # Buscar el bloque de estructura correspondiente en el JSON
                bloque_capa = None
                for bloque in compresiones:
                    if bloque.get("algoritmo") == algoritmo:
                        bloque_capa = bloque
                        break
                
                if not bloque_capa:
                    break
                
                estructura = bloque_capa.get("estructura", {})
                # Si la estructura del algoritmo está vacía en el JSON, significa que era de despiste
                if algoritmo == "Huffman" and "arbol" not in estructura:
                    break
                elif algoritmo == "LZ77" and "tripletas" not in estructura:
                    break
                elif algoritmo == "LZ78" and "diccionario" not in estructura and "salida" not in estructura:
                    break
                elif algoritmo == "LZW" and "salida" not in estructura:
                    break

                self.log_general(f"[Capa {pasos_realizados+1}] Removiendo algoritmo: {algoritmo}")

                texto_descomprimido = ""

                # --- PROCESAMIENTO POR ALGORITMO ---
                if algoritmo == "Huffman":
                    if isinstance(datos_actuales, bytes):
                        # Detectar si es ASCII legible de ceros y unos
                        if all(b_val in (0x30, 0x31, 0x0a, 0x0d, 0x20) for b_val in datos_actuales):
                            bit_string = datos_actuales.decode('utf-8', errors='ignore').strip()
                        else:
                            bit_string = datos_actuales.decode('ascii', errors='replace').strip()
                    else:
                        bit_string = str(datos_actuales).strip()
                    
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
                            import struct
                            codigos_lzw = []
                            for i in range(0, len(datos_actuales), 2):
                                if i+2 <= len(datos_actuales):
                                    codigos_lzw.append(struct.unpack('H', datos_actuales[i:i+2])[0])
                    else:
                        codigos_lzw = list(map(int, str(datos_actuales).strip().split()))

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
                    with open(r_t_json, 'w', encoding='utf-8') as f_j: json.dump({"compresion": [bloque_capa]}, f_j)
                    
                    gestor_lz77.descomprimir_archivo(r_t_bin, r_t_json, r_t_txt)
                    with open(r_t_txt, 'r', encoding='utf-8') as f_r: texto_descomprimido = f_r.read()
                    
                    for f_del in [r_t_bin, r_t_json, r_t_txt]:
                        if os.path.exists(f_del): os.remove(f_del)

                # --- CONTROL DE SALIDA DE CAPA ---
                next_algo = detectar_algoritmo_real(texto_descomprimido, datos_json)
                if next_algo == "Huffman" or next_algo == "LZ77":
                    datos_actuales = texto_descomprimido.encode('utf-8')
                else:
                    if all(c in '0123456789abcdefABCDEF' for c in texto_descomprimido) and len(texto_descomprimido) % 2 == 0:
                        try:
                            temp_bytes = bytes.fromhex(texto_descomprimido)
                            next_algo_decoded = detectar_algoritmo_real(temp_bytes, datos_json)
                            if next_algo_decoded in ["LZW", "LZ78", "LZ77"]:
                                datos_actuales = temp_bytes
                            else:
                                datos_actuales = texto_descomprimido.encode('utf-8')
                        except Exception:
                            datos_actuales = texto_descomprimido.encode('utf-8')
                    else:
                        datos_actuales = texto_descomprimido.encode('utf-8')

                pasos_realizados += 1

            # --- ESCRITURA FINAL DE RESULTADOS ---
            with open(ruta_txt_out, 'w', encoding='utf-8') as f_out:
                f_out.write(datos_actuales.decode('utf-8', errors='ignore'))

            self.log_general(f"\n[Terminado] Archivo restaurado de forma exitosa.")
            self.log_general(f"[Salida] {os.path.basename(ruta_txt_out)}")
            messagebox.showinfo("¡Éxito Total!", f"Proceso Completado.\nGuardado como: {os.path.basename(ruta_txt_out)}")

        except Exception as e:
            self.log_general(f"[Error] Falló la restauración:\n{e}")
            messagebox.showerror("Error General", f"No se pudo completar el proceso de descompresión:\n{e}")


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
                bytes_finales = bits_finales.encode('ascii', errors='replace')
                with open(r_bin, 'wb') as f_out: f_out.write(bytes_finales)
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

            # Estructurar JSON Final con todas las estructuras (torneo con despiste)
            pistas_reales = {
                algo1: pistas_capa_1.get("estructura") if (isinstance(pistas_capa_1, dict) and "estructura" in pistas_capa_1) else (pistas_capa_1.get("compresion", [{}])[0].get("estructura") if (isinstance(pistas_capa_1, dict) and "compresion" in pistas_capa_1) else pistas_capa_1),
                algo2: pistas_capa_2.get("estructura") if (isinstance(pistas_capa_2, dict) and "estructura" in pistas_capa_2) else (pistas_capa_2.get("compresion", [{}])[0].get("estructura") if (isinstance(pistas_capa_2, dict) and "compresion" in pistas_capa_2) else pistas_capa_2)
            }
            # Limpiar envolturas externas redundantes
            for a in [algo1, algo2]:
                if isinstance(pistas_reales.get(a), dict) and "estructura" in pistas_reales[a]:
                    pistas_reales[a] = pistas_reales[a]["estructura"]

            json_final = generar_json_final_competicion(texto_original, pistas_reales)

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
            with open(orig, 'r', encoding='utf-8') as f: texto = f.read()
            import lz77
            lz = lz77.LZ77(ventana=20)
            comprimido = lz.comprimir(texto)
            lz77.guardar(r_bin, comprimido)
            
            # Generar JSON unificado
            est_lz77 = {
                "tamano_buffer_busqueda": 20,
                "tamano_buffer_lectura": 10,
                "tripletas": []
            }
            for idx, (offset, longitud, siguiente) in enumerate(comprimido):
                offset_val = "_" if idx == 0 else offset
                siguiente_val = "_" if (siguiente == "" or siguiente is None) else siguiente
                est_lz77["tripletas"].append({
                    "offset": offset_val,
                    "longitud": longitud,
                    "siguiente": siguiente_val
                })
            json_final = generar_json_final_competicion(texto, {"LZ77": est_lz77})
            
            with open(r_json, 'w', encoding='utf-8') as f_json:
                json.dump(json_final, f_json, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Éxito", "LZ77 Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lz77_desc(self):
        b, j = self.ent_lz77_bin_d.get(), self.ent_lz77_json_d.get()
        if not b or not j: return
        try:
            proyecto_dir = os.path.dirname(os.path.abspath(__file__))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            os.makedirs(dir_salidas, exist_ok=True)
            r_out = os.path.join(dir_salidas, os.path.splitext(os.path.basename(b))[0] + "_restaurado.txt")
            
            import lz77
            lz = lz77.LZ77()
            with open(j, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
            
            from lz77 import obtener_tripletas
            tripletas = obtener_tripletas(datos_json)
            texto = lz.descomprimir(tripletas)
            
            with open(r_out, 'w', encoding='utf-8') as f_out:
                f_out.write(texto)
                
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
            
            # Generar JSON unificado
            json_final = generar_json_final_competicion(texto, {"LZ78": estructura_pistas["estructura"]})
            with open(r_json, 'w', encoding='utf-8') as f_json:
                json.dump(json_final, f_json, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Éxito", "LZ78 Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lz78_desc(self):
        b = self.ent_lz78_bin_d.get()
        if not b: return
        try:
            proyecto_dir = os.path.dirname(os.path.abspath(__file__))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            os.makedirs(dir_salidas, exist_ok=True)
            r_out = os.path.join(dir_salidas, os.path.splitext(os.path.basename(b))[0] + "_restaurado.txt")
            
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
            
            # Generar JSON unificado
            diccionario_inicial = {chr(i): i for i in range(256)}
            diccionario_generado_lista = []
            for cadena, codigo in diccionario_final.items():
                if codigo >= 256:
                    diccionario_generado_lista.append({
                        "codigo": codigo,
                        "cadena": cadena
                    })
            est_lzw = {
                "diccionario_inicial": diccionario_inicial,
                "diccionario_generado": diccionario_generado_lista,
                "salida": codigos
            }
            json_final = generar_json_final_competicion(texto, {"LZW": est_lzw})
            with open(r_json, 'w', encoding='utf-8') as f_json:
                json.dump(json_final, f_json, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Éxito", "LZW Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_lzw_desc(self):
        b = self.ent_lzw_bin_d.get()
        if not b: return
        try:
            proyecto_dir = os.path.dirname(os.path.abspath(__file__))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            os.makedirs(dir_salidas, exist_ok=True)
            r_out = os.path.join(dir_salidas, os.path.splitext(os.path.basename(b))[0] + "_restaurado.txt")
            
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
            bytes_finales = encoded_text.encode('ascii', errors='replace')
            with open(r_bin, 'wb') as f_bin: f_bin.write(bytes_finales)
            
            # Generar JSON unificado
            est_huffman = huffman.generate_json_structure(root_node, codes)["compresion"][0]["estructura"]
            json_final = generar_json_final_competicion(texto, {"Huffman": est_huffman})
            with open(r_json, 'w', encoding='utf-8') as f_json:
                json.dump(json_final, f_json, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Éxito", "Huffman Completado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_huffman_desc(self):
        b, j = self.ent_huff_bin_d.get(), self.ent_huff_json_d.get()
        if not b or not j: return
        try:
            proyecto_dir = os.path.dirname(os.path.abspath(__file__))
            dir_salidas = os.path.join(proyecto_dir, "salidas")
            os.makedirs(dir_salidas, exist_ok=True)
            r_out = os.path.join(dir_salidas, os.path.splitext(os.path.basename(b))[0] + "_restaurado.txt")
            
            with open(b, 'rb') as f_bin: bytes_data = f_bin.read()
            # Si el archivo tiene la Forma 2 (es ASCII legible de ceros y unos)
            if all(b_val in (0x30, 0x31, 0x0a, 0x0d, 0x20) for b_val in bytes_data):
                bit_string = bytes_data.decode('utf-8', errors='ignore').strip()
            else:
                bit_string = bytes_data.decode('ascii', errors='replace').strip()
                
            with open(j, 'r', encoding='utf-8') as f_json: datos_json = json.load(f_json)
            
            estructura_arbol = None
            for bloque in datos_json.get("compresion", []):
                if bloque.get("algoritmo") == "Huffman":
                    estructura_arbol = bloque["estructura"]["arbol"]
                    break
            
            if not estructura_arbol:
                raise ValueError("No se encontró estructura de Huffman en el JSON.")
                
            root_node = huffman.deserialize_tree(estructura_arbol)
            texto_recuperado = huffman.decode_bits(bit_string, root_node)
            with open(r_out, 'w', encoding='utf-8') as f_out: f_out.write(texto_recuperado)
            messagebox.showinfo("Éxito", "Restaurado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazTorneoAutomatica(root)
    root.mainloop()