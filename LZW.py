import os
def lzw_compress(uncompressed_string):
    """
    Algoritmo LZW Estándar de Compresión.
    Inicializa el diccionario con los primeros 256 caracteres ASCII (0-255).
    """
    # 1. Inicializar el diccionario con los caracteres individuales (bytes 0-255)
    dict_size = 256
    # Usamos un diccionario ordinario para buscar cadenas y obtener su código
    dictionary = {chr(i): i for i in range(256)}
    
    w = ""
    result_codes = []
    
    # 2. Iterar por cada uno de los caracteres del string de entrada
    for k in uncompressed_string:
        wk = w + k
        if wk in dictionary:
            w = wk
        else:
            # Emitir el código de 'w'
            result_codes.append(dictionary[w])
            # Agregar la nueva secuencia 'w + k' al diccionario
            dictionary[wk] = dict_size
            dict_size += 1
            w = k
            
    # 3. No olvidar emitir el código para la última cadena remanente en 'w'
    if w:
        result_codes.append(dictionary[w])
        
    return result_codes, dictionary

########################

def lzw_decompress(compressed_codes):
    """
    Algoritmo LZW Estándar de Descompresión.
    Reconstruye el texto original a partir de la lista de códigos.
    """
    if not compressed_codes:
        return ""

    # 1. Inicializar el diccionario de descompresión con los 256 caracteres ASCII
    # Aquí la búsqueda es inversa: del código numérico obtenemos el string
    dict_size = 256
    dictionary = {i: chr(i) for i in range(256)}

    # Tomar el primer código y convertirlo a carácter
    v = dictionary[compressed_codes[0]]
    result_string = [v]
    w = v

    # 2. Iterar sobre el resto de los códigos
    for k in compressed_codes[1:]:
        # CASO ESPECIAL LZW: Si el código K no está en el diccionario,
        # significa que es el caso especial donde la secuencia es W + W[0]
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError(f"Código de compresión corrupto o inválido: {k}")

        # Añadir la entrada al resultado final
        result_string.append(entry)

        # Agregar la nueva secuencia aprendida al diccionario
        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        # Actualizar W para la siguiente iteración
        w = entry

    return "".join(result_string)


#################################
import json

def generar_archivo_pistas_json(mensaje_original, codigos, diccionario_final, nombre_archivo="pistas_compresion.json"):
    """
    Genera el archivo JSON de pistas respetando el formato estricto del enunciado.
    Incluye secciones vacías para los otros algoritmos con el fin de despistar,
    tal como lo solicita la logística del torneo.
    """
    # 1. Reconstruir el diccionario inicial estándar (ASCII 0-255)
    
    diccionario_inicial = {chr(i): i for i in range(256) if chr(i).isalnum() or chr(i) in " ,.!"} 
    
    
    # 2. Filtrar el diccionario generado (solo las secuencias aprendidas, mayores o iguales a 256)
    diccionario_generado_lista = []
    for cadena, codigo in diccionario_final.items():
        if codigo >= 256:
            diccionario_generado_lista.append({
                "codigo": codigo,
                "cadena": cadena
            })
            
    # 3. Armar la estructura del LZW 
    estructura_lzw = {
        "diccionario_inicial": diccionario_inicial,
        "diccionario_generado": diccionario_generado_lista,
        "salida": codigos
    }
    
    # 4. Envoltura global exigida (incluye Huffman, LZ77, LZ78 vacíos para despistar)
    json_completo = {
        "compresion": [
            { "algoritmo": "Huffman", "estructura": {} },
            { "algoritmo": "LZ77", "estructura": {} },
            { "algoritmo": "LZ78", "estructura": {} },
            { "algoritmo": "LZW", "estructura": estructura_lzw }
        ]
    }
    
    # Guardar en disco
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(json_completo, f, indent=4, ensure_ascii=False)
    
    print(f"✔ Archivo de pistas guardado con éxito: '{nombre_archivo}'")

#####################
import struct

def guardar_archivo_binario(codigos, nombre_archivo="mensaje_comprimido.bin"):
    """
    Toma la lista de enteros del LZW y los guarda en un archivo binario puro
    utilizando bloques fijos de 16-bits (2 bytes por código, formato 'H' unsigned short).
    """
    with open(nombre_archivo, 'wb') as f:
        for codigo in codigos:
            # 'H' representa un entero de 16 bits sin signo (unsigned short)
            f.write(struct.pack('H', codigo))
    print(f"✔ Archivo binario generado con éxito: '{nombre_archivo}'")

def leer_archivo_binario(nombre_archivo="mensaje_comprimido.bin"):
    """
    Lee el archivo binario del rival y extrae los códigos de 16-bits
    para poder pasárselos directamente al descompresor.
    """
    codigos = []
    with open(nombre_archivo, 'rb') as f:
        buffer = f.read(2) # Leer de 2 en 2 bytes
        while buffer:
            if len(buffer) == 2:
                codigo = struct.unpack('H', buffer)[0]
                codigos.append(codigo)
            buffer = f.read(2)
    return codigos








# --- Prueba de Ejecución Completa  Descomp---
if __name__ == "__main__":
    mensaje_original = "EL GATO COME PESCADO y EL PERRO COME_HUESOSSS"
    
    # 1. Comprimir
    codigos, _ = lzw_compress(mensaje_original)
    print(f"Códigos generados por el compresor: {codigos}\n")
    
    # 2. Descomprimir
    mensaje_recuperado = lzw_decompress(codigos)
    print(f"Mensaje Recuperado por el descompresor:")
    print(f"'{mensaje_recuperado}'\n")
    
    # 3. Validación de integridad
    if mensaje_original == mensaje_recuperado:
        print("¡ÉXITO! El algoritmo LZW es 100% simétrico y respeta el estándar.")
    else:
        print("ERROR: El mensaje recuperado no coincide con el original.")





# --- Prueba de Ejecución comp ---
if __name__ == "__main__":
    mensaje = "EL GATO COME PESCADO Y EL PERRO COME HUESO"
    
    codigos_comprimidos, diccionario_final = lzw_compress(mensaje)
    
    print(f"compression; Mensaje Original ({len(mensaje)} caracteres):")
    print(f"'{mensaje}'\n")
    
    print(f"Códigos LZW generados ({len(codigos_comprimidos)} códigos):")
    print(codigos_comprimidos)
    
    print("\nNuevas secuencias agregadas al diccionario (mayores a 255):")
    # Filtramos para ver solo lo que el algoritmo aprendió dinámicamente
    nuevas_entradas = {secuencia: codigo for secuencia, codigo in diccionario_final.items() if codigo >= 256}
    
    for seq, cod in list(nuevas_entradas.items())[:40]:
        print(f"  Código {cod} -> '{seq}'")



if __name__ == "__main__":
    print("=" * 60)
    print("       MÓDULO DE DESCOMPRESIÓN DIRECTA (LZW.py)")
    print("=" * 60)
    
    # Nombre del archivo binario que deseas abrir CAMBIARLO AL PROBAR
    archivo_binario_a_abrir = "prueba_torneo.bin"
    archivo_salida_restaurado = "mensaje_restaurado.txt"
    
    # 1. Verificar si el archivo binario existe en la carpeta
    if not os.path.exists(archivo_binario_a_abrir):
        print(f" Error: No se encontró el archivo '{archivo_binario_a_abrir}' en este directorio.")
        print("[!] Ejecutando una compresión rápida de emergencia para generar el archivo...")
        
        texto_emergencia = "EL GATO COME PESCADO Y EL PERRO COME HUESO"
        codigos_e, dict_e = lzw_compress(texto_emergencia)
        guardar_archivo_binario(codigos_e, archivo_binario_a_abrir)
        generar_archivo_pistas_json(texto_emergencia, codigos_e, dict_e, "pistas_compresion.json")
        print("-" * 60)

    # 2. Leer el archivo binario (Extrayendo los bloques fijos de 16-bits)
    print(f"[Paso 1] Leyendo datos binarios desde '{archivo_binario_a_abrir}'...")
    codigos_extraidos = leer_archivo_binario(archivo_binario_a_abrir)
    print(f"         -> Códigos numéricos recuperados: {codigos_extraidos}")
    
    # 3. Ejecutar el descompresor LZW nativo
    print("\n[Paso 2] Ejecutando descompresión con el algoritmo simétrico...")
    try:
        texto_restaurado = lzw_decompress(codigos_extraidos)
        
        # 4. Guardar el archivo de texto limpio
        print(f"\n[Paso 3] Guardando traducción limpia en '{archivo_salida_restaurado}'...")
        with open(archivo_salida_restaurado, "w", encoding="utf-8") as f:
            f.write(texto_restaurado)
            
        print("=" * 50)
        print("  ¡PROCESO DE DESCOMPRESIÓN COMPLETADO CON ÉXITO! ")
        print("=" * 50)
        print("CONTENIDO RECONSTRUIDO:")
        print(f"'{texto_restaurado}'")
        print("=" * 50)
        
    except ValueError as e:
        print(f"\n Error crítico durante la descompresión: {e}")
        print("El archivo binario está corrupto o no pertenece a un LZW estándar.")