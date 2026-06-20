import json

def procesar_json_checksum(ruta_json: str):
    """
    Lee un archivo JSON de pistas  y reconstruye el mensaje original.
    el formato de Json debe ser:

    {
        "metadata": {
            "algorithm": "checksum_simple",
            "bits_por_segmento": 8
        },
        "data": [
            { "id": 1, "bits": "01001001", "checksum": 72 },
            { "id": 2, "bits": "01101111", "checksum": 111 },
            { "id": 3, "bits": "01111100", "checksum": 108 },
            { "id": 4, "bits": "01100001", "checksum": 97 }
        ]
    }

    """
    # Cargar el archivo JSON
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos_json = json.load(archivo)
    
    # Leer metadatos para validar el algoritmo
    metadata = datos_json.get("metadata", {})
    algoritmo = metadata.get("algorithm")
    bits_por_segmento = metadata.get("bits_por_segmento", 8)
    
    print(f"-----------------------------------------")
    print(f"Algoritmo detectado: {algoritmo}")
    print(f"Tamaño de segmento: {bits_por_segmento} bits\n")
    
    caracteres_reconstruidos = []
    errores_detectados = 0
    
    #Iterar por cada segmento en la lista "data"
    for segmento in datos_json.get("data", []):
        seg_id = segmento.get("id")
        bits_recibidos = segmento.get("bits")
        checksum_esperado = segmento.get("checksum")
        
        # Detección: Convertir los bits recibidos a número entero
        valor_decimal_recibido = int(bits_recibidos, 2)
        
        # Comparar el valor recibido con el checksum esperado
        if valor_decimal_recibido == checksum_esperado:
            # No hay error: convertimos los bits (o el checksum) a su carácter ASCII
            caracter_correcto = chr(checksum_esperado)
        else:
            # Si hay un error se guarda el caracter correcto
            errores_detectados += 1
            caracter_correcto = chr(checksum_esperado)
            

        caracteres_reconstruidos.append(caracter_correcto)
        

    mensaje_final = "".join(caracteres_reconstruidos)
    
    return {
    "mensaje_restaurado": mensaje_final,
    "errores_detectados": errores_detectados,
    "total_caracteres": len(caracteres_reconstruidos)
    }
