import struct
import os
import json

def comprimir_lz78(texto_original):
    """
    Comprime un texto usando LZ78.
    Retorna:
      1. bytes_comprimidos: Los datos empaquetados en formato binario.
      2. estructura_json: El diccionario con las pistas para el reto.
    """
    #validar que el texto no contenga caracteres fuera de ascii simple
    try:
        texto_original.encode('ascii')
    except UnicodeEncodeError:
        raise ValueError("Error: El texto contiene caracteres especiales") 
    
    diccionario_interno = {} # Diccionario para crear la cadena de índices
    diccionario_json = [] # Lista para el JSON de pistas
    salida_json = [] # Lista para la salida de pistas (índice + símbolo)
    
    datos_binarios = bytearray() # Usamos bytearray para construir los bytes de salida de forma eficiente
    
    indice_actual = 1 # Comenzamos en 1 porque el índice 0 se reserva para la cadena vacía
    cadena_actual = "" 
    
    # Recorremos cada carácter del texto original
    for char in texto_original: 
        nueva_cadena = cadena_actual + char
        
        # Verificamos si la nueva cadena ya existe en el diccionario interno
        if nueva_cadena in diccionario_interno: 
            cadena_actual = nueva_cadena
        else:
            # Si no existe, necesitamos emitir la salida para la cadena actual y el nuevo carácter
            indice_salida = diccionario_interno[cadena_actual] if cadena_actual else 0 
            
            # Llenamos las estructuras para el JSON de pistas
            salida_json.append({"indice": indice_salida, "simbolo": char})
            diccionario_json.append({"indice": indice_actual, "cadena": nueva_cadena})
            diccionario_interno[nueva_cadena] = indice_actual
            
            datos_binarios.extend(struct.pack('>Hc', indice_salida, char.encode('ascii'))) # Empaquetamos el índice y el carácter en formato binario (2 bytes para el índice, 1 byte para el carácter)
            
            indice_actual += 1
            cadena_actual = ""
            
    # Manejo del remanente final si lo hay
    if cadena_actual:
        indice_salida = diccionario_interno[cadena_actual]
        salida_json.append({"indice": indice_salida, "simbolo": ""})
        datos_binarios.extend(struct.pack('>Hc', indice_salida, b'\x00')) # Usamos un byte nulo para indicar que no hay símbolo adicional

    # Estructura final para el JSON de pistas
    estructura_pista = {
        "algoritmo": "LZ78",
        "estructura": {
            "diccionario": diccionario_json,
            "salida": salida_json
        }
    }
    
    return bytes(datos_binarios), estructura_pista

def descomprimir_lz78(datos_binarios):
    """
    Descomprime una secuencia de bytes empaquetados con LZ78.
    Retorna el string de texto recuperado.
    """
    diccionario_reconstruccion = {0: ""} 
    texto_recuperado = "" 
    siguiente_indice = 1
    
    # Recorremos los bytes de 3 en 3 (porque guardamos 2 del índice y 1 del carácter)
    for i in range(0, len(datos_binarios), 3):
        bloque = datos_binarios[i:i+3]
        if len(bloque) < 3:
            break
            
        # Desempaquetamos los bytes a sus valores originales
        indice_padre, char_byte = struct.unpack('>Hc', bloque)
        
        # Si el carácter es el byte nulo, lo interpretamos como una cadena vacía
        simbolo = "" if char_byte == b'\x00' else char_byte.decode('ascii')
        
        prefijo = diccionario_reconstruccion[indice_padre] 
        nueva_cadena = prefijo + simbolo
        texto_recuperado += nueva_cadena
        
        if simbolo != "": # Solo agregamos al diccionario si el símbolo no es vacío
            diccionario_reconstruccion[siguiente_indice] = nueva_cadena
            siguiente_indice += 1
            
    return texto_recuperado

#  PRUEBAS
if __name__ == "__main__":
    print("PRUEBAS DE LZ78")

    # Crear carpeta de pruebas
    carpeta_pruebas = "pruebas_lz78"
    if not os.path.exists(carpeta_pruebas):
        os.makedirs(carpeta_pruebas)

    ruta_bin = os.path.join(carpeta_pruebas, "archivoLZ78_comprimido.bin")
    ruta_json = os.path.join(carpeta_pruebas, "pistasLZ78.json")

    # Definir texto de prueba
    texto_prueba = "EL GATO COME PESCADO Y EL PERRO COME HUESO"
    print(f"\nTexto original: '{texto_prueba}'")

    # Ejecutar función de compresión
    bytes_comprimidos, estructura_pistas = comprimir_lz78(texto_prueba)

    # Guardar archivos de salida
    with open(ruta_bin, 'wb') as f_bin:
        f_bin.write(bytes_comprimidos)

    # Guardar el JSON de pistas
    with open(ruta_json, 'w', encoding='utf-8') as f_json:
        # Envolvemos tu bloque en la lista principal que pide el enunciado
        json_final = {"compresion": [estructura_pistas]} 
        json.dump(json_final, f_json, indent=4, ensure_ascii=False)

    print(f"Archivos guardados físicamente en la carpeta '{carpeta_pruebas}'")

    # Leer el archivo binario y ejecutar la función de descompresión
    with open(ruta_bin, 'rb') as f_bin_lectura:
        bytes_leidos = f_bin_lectura.read()

    texto_recuperado = descomprimir_lz78(bytes_leidos)
    print(f"\nTexto recuperado: '{texto_recuperado}'")

    # Validación Final
    if texto_prueba == texto_recuperado:
        print("\n RESULTADO: ÉXITO. El ciclo completo funciona al 100%.")
    else:
        print("\n RESULTADO: ERROR. Hay discrepancias en la recuperación.")
