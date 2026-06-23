import random

def calcular_crc(bits_originales: str, polinomio: str) -> str:
    """Calcula el residuo CRC mediante división polinomial XOR."""
    grado = len(polinomio) - 1
    # Extender los bits con ceros al final según el grado del polinomio
    bits_extendidos = bits_originales + ('0' * grado)
    lista_bits = list(bits_extendidos)
    
    for i in range(len(bits_originales)):
        if lista_bits[i] == '1':  # Si el bit actual es 1, aplicamos XOR con el polinomio
            for j in range(len(polinomio)):
                lista_bits[i + j] = '1' if lista_bits[i + j] != polinomio[j] else '0'
                
    # El residuo son los últimos 'grado' bits
    residuo = "".join(lista_bits[-grado:]) if grado > 0 else ""
    return residuo

def aplicar_corrupcion_checksum(texto: str, cantidad_errores: int):
    """Corrompe el texto aplicando errores de bit único a caracteres aleatorios (Checksum)."""
    if cantidad_errores > len(texto):
        raise ValueError("La cantidad de errores no puede ser mayor que la longitud del texto.")

    segmentos_binarios = [format(ord(c), '08b') for c in texto]
    posiciones_a_corromper = random.sample(range(len(texto)), cantidad_errores)
    
    for pos in posiciones_a_corromper:
        segmento = list(segmentos_binarios[pos])
        bit_a_voltear = random.randint(0, 7)
        segmento[bit_a_voltear] = '1' if segmento[bit_a_voltear] == '0' else '0'
        segmentos_binarios[pos] = "".join(segmento)

    caracteres_corruptos = [chr(int(b, 2)) for b in segmentos_binarios]
    texto_corrupto_final = "".join(caracteres_corruptos)

    json_data = []
    for i, bits in enumerate(segmentos_binarios):
        json_data.append({
            "id": i + 1,
            "bits": bits,
            "checksum": ord(texto[i])
        })

    estructura_json_pistas = {
        "metadata": {
            "algorithm": "checksum_simple",
            "bits_por_segmento": 8
        },
        "data": json_data
    }

    return {
        "texto_corrupto": texto_corrupto_final,
        "json_pistas": estructura_json_pistas,
        "posiciones_afectadas": posiciones_a_corromper,
        "cantidad_errores_introducidos": cantidad_errores
    }

def aplicar_corrupcion_crc(texto: str, cantidad_errores: int, polinomio: str = "1101"):
    """
    Corrompe el texto usando CRC y genera el JSON
    """
    grado = len(polinomio) - 1
    
    #Convertir todo el texto original a una cadena binaria continua
    cadena_binaria_original = "".join([format(ord(c), '08b') for c in texto])
    
    # Calcular CRC original
    residuo_original = calcular_crc(cadena_binaria_original, polinomio)
    codigo_transmitido_original = cadena_binaria_original + residuo_original
    
    #Introducir errores en la cadena de bits que se va a transmitir
    lista_transmitida = list(codigo_transmitido_original)
    
    # Corromper bits aleatorios dentro de la sección de datos
    limite_errores = min(cantidad_errores, len(cadena_binaria_original))
    if limite_errores > 0:
        posiciones_a_corromper = random.sample(range(len(cadena_binaria_original)), limite_errores)
        for pos in posiciones_a_corromper:
            lista_transmitida[pos] = '1' if lista_transmitida[pos] == '0' else '0'
    else:
        posiciones_a_corromper = []
        
    codigo_corrupto_transmitido = "".join(lista_transmitida)
    datos_corruptos_recibidos = codigo_corrupto_transmitido[:len(cadena_binaria_original)]
    
    # Reconstruir el texto corrupto para mostrarlo en la GUI en caracteres
    caracteres_corruptos = []
    for i in range(0, len(datos_corruptos_recibidos), 8):
        bloque = datos_corruptos_recibidos[i:i+8]
        if len(bloque) == 8:
            caracteres_corruptos.append(chr(int(bloque, 2)))
    texto_corrupto_final = "".join(caracteres_corruptos)
    
    
    estructura_json_pistas = {
        "archivo": "mensaje.txt",
        "algoritmo": "CRC",
        "parametros": {
            "polinomio": polinomio,
            "grado": grado,
            "valor_inicial": "0" * grado,
            "xor_final": "0" * grado
        },
        "datos": {
            "original": cadena_binaria_original,
            "extendido": cadena_binaria_original + ('0' * grado),
            "residuo_crc": residuo_original
        },
        "verificacion": {
            "codigo_transmitido": codigo_corrupto_transmitido,
            "resultado_verificacion": "invalido" if cantidad_errores > 0 else "valido"
        },
        # Guardamos el respaldo del texto limpio 
        "texto_original_aux": texto 
    }
    
    return {
        "texto_corrupto": texto_corrupto_final,
        "json_pistas": estructura_json_pistas,
        "posiciones_afectadas": posiciones_a_corromper,
        "cantidad_errores_introducidos": cantidad_errores
    }