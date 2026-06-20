import random

def aplicar_corrupcion_checksum(texto: str, cantidad_errores: int):
    """
    Corrompe el texto aplicando errores de bit único a caracteres aleatorios.
    Devuelve un diccionario estructurado para que la GUI lo muestre y lo guarde.
    """
    if cantidad_errores > len(texto):
        raise ValueError("La cantidad de errores no puede ser mayor que la longitud del texto.")

    # Convertimos cada carácter del texto a su binario de 8 bits
    segmentos_binarios = [format(ord(c), '08b') for c in texto]
    
    # Seleccionamos posiciones aleatorias para corromper (sin repetir posiciones)
    posiciones_a_corromper = random.sample(range(len(texto)), cantidad_errores)
    
    # Aplicar la corrupción (Single-bit error) en los segmentos seleccionados
    for pos in posiciones_a_corromper:
        segmento = list(segmentos_binarios[pos])
        # Elegimos un bit al azar de los 8 bits (del 0 al 7) y lo volteamos
        bit_a_voltear = random.randint(0, 7)
        segmento[bit_a_voltear] = '1' if segmento[bit_a_voltear] == '0' else '0'
        segmentos_binarios[pos] = "".join(segmento)

    # Reconstruimos el texto corrupto final para mostrarlo en la GUI
    caracteres_corruptos = [chr(int(b, 2)) for b in segmentos_binarios]
    texto_corrupto_final = "".join(caracteres_corruptos)

    # Construimos el JSON de pistas 
    json_data = []
    for i, bits in enumerate(segmentos_binarios):
        json_data.append({
            "id": i + 1,
            "bits": bits,
            "checksum": ord(texto[i]) # El valor decimal original correcto
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