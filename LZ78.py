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
    
    texto_salida = "" # Usamos un string para construir el formato de texto del profesor
    
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
            
            texto_salida += f"({indice_salida},{char})"
            
            indice_actual += 1
            cadena_actual = ""
            
    # Manejo del remanente final si lo hay
    if cadena_actual:
        indice_salida = diccionario_interno[cadena_actual]
        salida_json.append({"indice": indice_salida, "simbolo": ""})
        texto_salida += f"({indice_salida},)"

    # Convertimos a ASCII según el formato del profesor
    bytes_comprimidos = texto_salida.encode('ascii', errors='replace')

    # Estructura final para el JSON de pistas
    estructura_pista = {
        "algoritmo": "LZ78",
        "estructura": {
            "diccionario": diccionario_json,
            "salida": salida_json
        }
    }
    
    return bytes_comprimidos, estructura_pista

def descomprimir_lz78(datos_binarios):
    """
    Descomprime una secuencia de bytes empaquetados con LZ78 (formato ASCII del profesor).
    Retorna el string de texto recuperado.
    """
    texto = datos_binarios.decode('ascii', errors='replace').strip()
    diccionario_reconstruccion = {0: ""} 
    texto_recuperado = "" 
    siguiente_indice = 1
    
    i = 0
    while i < len(texto):
        if texto[i] == '(':
            comma_idx = texto.find(',', i)
            if comma_idx == -1: break
            
            close_paren = texto.find(')', comma_idx + 1)
            # Manejar el caso donde el caracter guardado era un parentesis de cierre
            if close_paren != -1 and close_paren == comma_idx + 1 and i + 1 < len(texto) and comma_idx + 2 < len(texto) and texto[comma_idx+2] == ')':
                close_paren = comma_idx + 2
                
            if close_paren == -1: break
            
            indice_str = texto[i+1:comma_idx].strip()
            indice_padre = int(indice_str) if indice_str else 0
            
            simbolo = texto[comma_idx+1:close_paren]
            # Si guardamos espacios, quitamos el espacio al inicio de haberlo
            if len(simbolo) > 0 and simbolo[0] == ' ' and close_paren > comma_idx + 2:
                simbolo = simbolo[1:]

            prefijo = diccionario_reconstruccion[indice_padre] 
            nueva_cadena = prefijo + simbolo
            texto_recuperado += nueva_cadena
            
            if simbolo != "": # Solo agregamos al diccionario si el símbolo no es vacío
                diccionario_reconstruccion[siguiente_indice] = nueva_cadena
                siguiente_indice += 1
                
            i = close_paren + 1
        else:
            i += 1
            
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
