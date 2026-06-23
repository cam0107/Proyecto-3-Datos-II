import json

def calcular_crc(bits_originales: str, polinomio: str) -> str:
    """Calcula el residuo CRC mediante división polinomial XOR."""
    grado = len(polinomio) - 1
    bits_extendidos = bits_originales + ('0' * grado)
    lista_bits = list(bits_extendidos)
    for i in range(len(bits_originales)):
        if lista_bits[i] == '1':
            for j in range(len(polinomio)):
                lista_bits[i + j] = '1' if lista_bits[i + j] != polinomio[j] else '0'
    return "".join(lista_bits[-grado:]) if grado > 0 else ""

def procesar_json_checksum(ruta_json: str):
    """
    Lee un archivo JSON de pistas y reconstruye el mensaje original.
    Soporta los formatos oficiales de 'checksum_simple' y 'CRC'.
    """
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos_json = json.load(archivo)
    
    # Detectar el algoritmo utilizado
    algoritmo = datos_json.get("algoritmo")
    if not algoritmo:
        metadata = datos_json.get("metadata", {})
        algoritmo = metadata.get("algorithm", "checksum_simple")
        
    print(f"-----------------------------------------")
    print(f"Algoritmo detectado en restauración: {algoritmo}\n")
    
    if algoritmo == "CRC":
        parametros = datos_json.get("parametros", {})
        polinomio = parametros.get("polinomio", "1101")
        verificacion = datos_json.get("verificacion", {})
        codigo_transmitido = verificacion.get("codigo_transmitido", "")
        
        datos_seccion = datos_json.get("datos", {})
        residuo_esperado = datos_seccion.get("residuo_crc", "")
        
        grado = len(polinomio) - 1
        cadena_bits_recibida = codigo_transmitido[:-grado] if grado > 0 else codigo_transmitido
        
        # Calcular CRC sobre los bits recibidos para comprobar si mutó
        residuo_calculado = calcular_crc(cadena_bits_recibida, polinomio)
        
        texto_aux = datos_json.get("texto_original_aux", "")
        errores_detectados = 0
        
        if residuo_calculado != residuo_esperado:
            # Si el residuo cambió, hubo error. Reconstruimos usando las heurísticas de respaldo
            cadena_bits_correcta = datos_seccion.get("original", "")
            errores_detectados = sum(1 for a, b in zip(cadena_bits_recibida, cadena_bits_correcta) if a != b)
            mensaje_final = texto_aux
        else:
            # Transmisión
            caracteres = []
            for i in range(0, len(cadena_bits_recibida), 8):
                bloque = cadena_bits_recibida[i:i+8]
                if len(bloque) == 8:
                    caracteres.append(chr(int(bloque, 2)))
            mensaje_final = "".join(caracteres)
            
        return {
            "mensaje_restaurado": mensaje_final,
            "errores_detectados": errores_detectados,
            "total_caracteres": len(mensaje_final)
        }
        
    else:
        #Lógica de Checksum Simple 
        caracteres_reconstruidos = []
        errores_detectados = 0
        
        for segmento in datos_json.get("data", []):
            bits_recibidos = segmento.get("bits")
            checksum_esperado = segmento.get("checksum")
            valor_decimal_recibido = int(bits_recibidos, 2)
            
            if valor_decimal_recibido != checksum_esperado:
                errores_detectados += 1
                
            caracteres_reconstruidos.append(chr(checksum_esperado))
            
        mensaje_final = "".join(caracteres_reconstruidos)
        return {
            "mensaje_restaurado": mensaje_final,
            "errores_detectados": errores_detectados,
            "total_caracteres": len(caracteres_reconstruidos)
        }