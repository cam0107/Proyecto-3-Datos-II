import os
import json
import itertools
from collections import Counter

# Palabras comunes en español para evaluar si el texto descifrado es legible
PALABRAS_ES = {
    "de","la","el","en","los","las","un","una","es","se","no",
    "te","le","da","su","por","con","que","son","hay","muy","fue","ser",
    "del","al","lo","si","pero","como","mas","ni","yo","tu","mi","me",
    "todo","toda","todos","todas","cada","este","esta","estos","estas",
    "ese","esa","esos","esas","bien","algo","aqui","ya","dos","tres",
    "hola","mundo","datos","dato","sistema","sistemas","algoritmos",
    "algoritmo","cifrado","cifrar","descifrar","texto","textos","binario",
    "codigo","archivo","archivos","compresion","mensaje","mensajes","clave",
    "claves","reto","proyecto","proyectos","ingenieria","ciencia","ciencias",
    "digital","informacion","computacion","computo","red","bit","byte",
    "bits","bytes","xor","para","una","uno","unos","unas","tan","tanto",
    "estar","han","ha","fueron","era","eran","otro","otra","otros","otras",
    "tecnologico","tecnologia","costa","rica","universidad","instituto",
    "informatica","estudiante","estudiantes","profesor","profesores",
    "curso","cursos","clase","clases","examen","examenes","grupo","grupos",
}

# Caracteres ASCII basicos
CHARS_IMPRIMIBLES = list(range(0, 128))

# Cantidad de candidatos a considerar por cada posicion de la clave durante
TOP_CANDIDATOS_POR_POSICION = 5

def cifrar_xor(texto_original, clave):
    """
    Cifra un texto usando el método XOR con una clave repetida.
    Parámetros:
        texto_original (str): mensaje a cifrar
        clave (str): clave secreta (1-10 caracteres)
    Retorna:
        bytes_cifrados (bytes): resultado del XOR en binario
        estructura_json (dict): estructura con metadata y ciphertext para el JSON
    """
    largo_clave = len(clave)
    valores_cifrados = []

    for i, caracter in enumerate(texto_original):
        byte_texto = ord(caracter)
        byte_clave = ord(clave[i % largo_clave])
        valores_cifrados.append(byte_texto ^ byte_clave)  # Operación XOR

    # Convertir cada byte cifrado a binario de 8 dígitos y concatenar
    cadena_bits = "".join(format(v, "08b") for v in valores_cifrados)

    estructura_json = {
        "metadata": {
            "encoding": "binario",
            "method": "XOR",
            "bits_por_segmento": 8,
            "descripcion": "Texto cifrado usando XOR con clave repetida"
        },
        "ciphertext": [cadena_bits]
    }

    return bytes(valores_cifrados), estructura_json

def descifrar_xor(datos_binarios, clave):
    """
    Descifra un archivo binario cifrado con XOR usando la clave dada.
    Parámetros:
        datos_binarios (bytes): bytes del archivo cifrado
        clave (str): clave usada para cifrar
    Retorna:
        str: texto descifrado
    """
    largo_clave = len(clave)
    texto_recuperado = ""

    for i, byte_cifrado in enumerate(datos_binarios):
        byte_clave = ord(clave[i % largo_clave])
        texto_recuperado += chr(byte_cifrado ^ byte_clave)

    return texto_recuperado

def validar_parametros(mensaje, clave):
    """
    Verifica que el mensaje y la clave cumplan las restricciones del reto:
        - La clave debe tener entre 1 y 10 caracteres
        - El mensaje debe tener al menos el doble de caracteres que la clave
        - Mensaje y clave deben usar solo ASCII básico (0-127)
    Parámetros:
        mensaje (str): texto a cifrar
        clave (str): clave secreta
    Retorna:
        tuple (bool, str): (es_valido, mensaje_de_error)
    """
    if len(clave) == 0 or len(clave) > 10:
        return False, f"La clave debe tener entre 1 y 10 caracteres (actual: {len(clave)})."

    minimo_mensaje = len(clave) * 2
    if len(mensaje) < minimo_mensaje:
        return False, (
            f"El mensaje tiene {len(mensaje)} caracteres. "
            f"Debe tener al menos {minimo_mensaje} (el doble de la clave)."
        )

    for caracter in mensaje:
        if ord(caracter) > 127:
            return False, f"El mensaje contiene '{caracter}', que no es ASCII básico (0-127)."

    for caracter in clave:
        if ord(caracter) > 127:
            return False, f"La clave contiene '{caracter}', que no es ASCII básico (0-127)."

    return True, ""

def leer_ciphertext_json(ruta_json):
    """
    Lee el archivo JSON del grupo emisor y extrae los bytes cifrados.
    El ciphertext viene como una lista con una cadena larga de bits.
    Se separa cada 8 bits para reconstruir los bytes originales.
    Parámetros:
        ruta_json (str): ruta al archivo .json recibido
    Retorna:
        tuple (list[int], dict): (bytes cifrados como enteros, metadata del JSON)
    """
    with open(ruta_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    metadata = datos.get("metadata", {})
    cadena_bits = "".join(datos.get("ciphertext", []))

    bytes_cifrados = [
        int(cadena_bits[i:i+8], 2)
        for i in range(0, len(cadena_bits), 8)
        if len(cadena_bits[i:i+8]) == 8
    ]

    return bytes_cifrados, metadata

def puntaje_base(br):
    """
    Evalúa la "calidad" de un texto descifrado basándose en la frecuencia de caracteres.
    Parámetros:
        br (list[int]): bytes a evaluar
    Retorna:
        float: puntaje normalizado de 0.0 a 1.0
    """
    if not br:
        return 0.0
    letras_comunes = set(b"eEaAoOsSnNrRiIlLtTuU ")
    puntos = sum(
        1 + (2 if b in letras_comunes else 0) if 32 <= b <= 126
        else (1 if b in (10, 13) else -3)
        for b in br
    )
    return max(0.0, puntos / (len(br) * 3))

def puntaje_total(br):
    """
    Evalúa el texto completo descifrado: combina el puntaje de caracteres
    con un bonus por palabras reales en español y por palabras "limpias"
    (compuestas solo de letras, sin símbolos sueltos.
    Cualquier candidato que contenga al menos un byte no imprimible se
    descarta de inmediato (puntaje muy negativo).
    Se usa para elegir el mejor candidato entre los resultados finales.
    Parámetros:
        br (list[int]): bytes del texto completo descifrado
    Retorna:
        float: puntaje (muy negativo si hay bytes no imprimibles)
    """
    # un mensaje valido del reto es 100% ASCII imprimible
    if any(not (32 <= b <= 126) for b in br):
        return -1000.0

    base = puntaje_base(br)
    texto = "".join(chr(b) for b in br)
    palabras = texto.split()

    # Bonus por palabras reales del diccionario
    hits_diccionario = sum(1 for w in palabras if w.lower().strip(".,!?") in PALABRAS_ES)
    base += hits_diccionario * 2

    # Bonus fuerte por palabras "limpias" (solo letras, sin puntuacion)
    palabras_limpias = sum(1 for w in palabras if w.strip(".,!?;:").isalpha())
    base += palabras_limpias * 3

    return base

def adivinar_byte_clave(subsecuencia):
    """
    Determina los bytes de clave más probables para una subsecuencia
    cifrada con el mismo byte de clave, usando el puntaje_base para evaluar
    candidatos según puntaje_base.
    Parámetros:
        subsecuencia (list[int]): bytes cifrados con el mismo byte de clave
    Retorna:
        list[int]: los mejores bytes candidatos, ordenados de mejor a peor
    """
    resultados = []
    for k in CHARS_IMPRIMIBLES:
        p = puntaje_base([b ^ k for b in subsecuencia])
        resultados.append((k, p))

    resultados.sort(key=lambda x: -x[1])

    # Tomar los mejores N, mas todos los que empatan con el N-esimo puntaje
    top = resultados[:TOP_CANDIDATOS_POR_POSICION]
    puntaje_limite = top[-1][1]
    candidatos = [k for k, p in resultados if p >= puntaje_limite]

    return candidatos

def ataque_por_bloques(cifrado, longitud):
    """
    Recupera la clave dividiendo el ciphertext en subsecuencias independientes.
    Efectivo cuando hay suficientes repeticiones de la clave (texto largo).
    Parámetros:
        cifrado (list[int]): bytes del ciphertext
        longitud (int): longitud de clave a probar
    Retorna:
        list[tuple]: lista de (clave_str, puntaje, texto_descifrado),
                     una por cada combinación de clave evaluada
    """
    candidatos_por_posicion = [
        adivinar_byte_clave(cifrado[pos::longitud])
        for pos in range(longitud)
    ]

    # Limitar el total de combinaciones para que no se vuelva muy lento
    total_combinaciones = 1
    for c in candidatos_por_posicion:
        total_combinaciones *= len(c)

    if total_combinaciones > 100000:
        # Si hay demasiadas combinaciones, recortamos a menos candidatos
        candidatos_por_posicion = [c[:2] for c in candidatos_por_posicion]

    resultados = []
    for combo in itertools.product(*candidatos_por_posicion):
        resultado = [b ^ combo[i % longitud] for i, b in enumerate(cifrado)]
        puntaje = puntaje_total(resultado)
        texto = "".join(chr(b) if 32 <= b <= 126 else "?" for b in resultado)
        clave_str = "".join(chr(b) if 32 <= b <= 126 else "?" for b in combo)
        resultados.append((clave_str, puntaje, texto))

    return resultados


def fuerza_bruta(cifrado, longitud):
    """
    Prueba todas las combinaciones posibles de caracteres ASCII básicos
    para una clave de la longitud dada. 
    Necesario cuando el texto es corto y el ataque por bloques no tiene
    suficientes datos para distinguir
    Parámetros:
        cifrado (list[int]): bytes del ciphertext
        longitud (int): longitud de clave a probar (máximo 3)
    Retorna:
        list[tuple]: lista de (clave_str, puntaje, texto_descifrado),
    """
    mejor_p = -1
    empatados = []

    for combo in itertools.product(CHARS_IMPRIMIBLES, repeat=longitud):
        resultado = [b ^ combo[i % longitud] for i, b in enumerate(cifrado)]
        p = puntaje_total(resultado)

        if p > mejor_p:
            mejor_p = p
            empatados = [(
                "".join(chr(b) if 32 <= b <= 126 else "?" for b in combo),
                p,
                "".join(chr(b) if 32 <= b <= 126 else "?" for b in resultado)
            )]
        elif p == mejor_p:
            empatados.append((
                "".join(chr(b) if 32 <= b <= 126 else "?" for b in combo),
                p,
                "".join(chr(b) if 32 <= b <= 126 else "?" for b in resultado)
            ))

    return empatados

def descifrar_sin_clave(bytes_cifrados, pista_longitud=None):
    """
    Intenta recuperar el mensaje sin conocer la clave mediante criptoanálisis.
    Si el JSON incluye key_length_hint, los candidatos de esa longitud se
    priorizan en la lista.
    Parámetros:
        bytes_cifrados (list[int]): bytes del ciphertext
        pista_longitud (int | None): longitud sugerida por el JSON (opcional)
    Retorna:
        list[tuple]: candidatos (longitud, clave_str, puntaje, texto) ordenados
    """
    candidatos = []

    print("\n  Analizando longitudes de clave del 1 al 10...")
    for longitud in range(1, 11):
        # Usar fuerza bruta si el texto es corto y la clave candidata es pequeña
        suficientes_repeticiones = len(bytes_cifrados) >= longitud * 8

        if suficientes_repeticiones:
            # ataque_por_bloques tambien puede devolver varios empatados
            resultados = ataque_por_bloques(bytes_cifrados, longitud)
            for c, p, t in resultados:
                candidatos.append((longitud, c, p, t))
        elif longitud <= 3:
            empatados = fuerza_bruta(bytes_cifrados, longitud)
            for c, p, t in empatados:
                candidatos.append((longitud, c, p, t))
        else:
            resultados = ataque_por_bloques(bytes_cifrados, longitud)
            for c, p, t in resultados:
                candidatos.append((longitud, c, p, t))

    # Ordenar por puntaje descendente
    candidatos.sort(key=lambda x: -x[2])


    # Si el JSON incluye pista de longitud, moverla al frente
    if pista_longitud:
        for i, c in enumerate(candidatos):
            if c[0] == pista_longitud:
                candidatos.insert(0, candidatos.pop(i))
                print(f"  Pista de longitud {pista_longitud} encontrada en el JSON, se prioriza.")
                break

    return candidatos

def descifrar_automatico(bytes_cifrados, pista_longitud=None):
    """
    recibe el ciphertext y devuelve el mejor resultado encontrado
    Parámetros:
        bytes_cifrados (list[int]): bytes del ciphertext recibido
        pista_longitud (int | None): longitud sugerida por el JSON (opcional)
    Retorna:
        dict: {
            "clave": str,            clave recuperada
            "mensaje": str,          mensaje descifrado
            "longitud_clave": int,   longitud de clave usada
            "confianza": float       puntaje del resultado (mayor es mejor)
        }
    """
    candidatos = descifrar_sin_clave(bytes_cifrados, pista_longitud=pista_longitud)

    if not candidatos:
        return {
            "clave": "",
            "mensaje": "",
            "longitud_clave": 0,
            "confianza": 0.0
        }

    longitud, clave, puntaje, texto = candidatos[0]

    return {
        "clave": clave,
        "mensaje": texto,
        "longitud_clave": longitud,
        "confianza": puntaje
    }

#  PRUEBAS
if __name__ == "__main__":
    print("PRUEBAS DE CIFRADO/DESCIFRADO XOR")

    proyecto_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta_pruebas = os.path.join(proyecto_dir, "pruebas_xor")
    if not os.path.exists(carpeta_pruebas):
        os.makedirs(carpeta_pruebas)

    ruta_bin = os.path.join(carpeta_pruebas, "archivo_cifrado.bin")
    ruta_json = os.path.join(carpeta_pruebas, "archivo_xor.json")

    texto_prueba = "la caracatrepa trepa con cinco caracatrepitos, cuando la caracatrepa trepa ellos trepan"
    clave_prueba = "tec123"

    print(f"\nTexto original : '{texto_prueba}'")
    print(f"Clave          : '{clave_prueba}'")

    # Validar restricciones antes de cifrar
    valido, error = validar_parametros(texto_prueba, clave_prueba)
    if not valido:
        print(f"Error de validación: {error}")
        exit(1)

    # Cifrado
    print("\n--- Prueba de cifrado ---")
    bytes_cifrados, estructura_json = cifrar_xor(texto_prueba, clave_prueba)

    with open(ruta_bin, 'wb') as f:
        f.write(bytes_cifrados)
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(estructura_json, f, indent=4, ensure_ascii=False)

    print(f"  Archivos guardados en '{carpeta_pruebas}'")
    print(f"  Bytes cifrados: {len(bytes_cifrados)}")

    print("\n  Ejemplo del proceso XOR (primeros 5 caracteres):")
    print(f"  {'Char':<6} {'ASCII':<8} {'Clave':<6} {'ASCII K':<8} {'XOR':<6} {'Binario'}")
    print(f"  {'-'*52}")
    for i in range(min(5, len(texto_prueba))):
        c = texto_prueba[i]
        k = clave_prueba[i % len(clave_prueba)]
        xor_val = ord(c) ^ ord(k)
        print(f"  {c:<6} {ord(c):<8} {k:<6} {ord(k):<8} {xor_val:<6} {format(xor_val, '08b')}")

    # Prueba de descifrado con clave conocida
    print("\n--- Prueba de descifrado con clave conocida ---")
    with open(ruta_bin, 'rb') as f:
        bytes_leidos = f.read()

    texto_recuperado = descifrar_xor(bytes_leidos, clave_prueba)
    print(f"  Texto recuperado: '{texto_recuperado}'")

    if texto_prueba == texto_recuperado:
        print("\n  RESULTADO: ÉXITO. El ciclo completo funciona al 100%.")
    else:
        print("\n  RESULTADO: ERROR. Hay discrepancias en la recuperación.")

    # Prueba de descifrado sin clave (criptoanálisis)
    print("\n--- Prueba de descifrado sin clave (criptoanálisis) ---")
    bytes_json, metadata = leer_ciphertext_json(ruta_json)
    pista = metadata.get("key_length_hint")

    resultado = descifrar_automatico(bytes_json, pista_longitud=pista)

    print(f"\n  Clave recuperada   : '{resultado['clave']}'")
    print(f"  Longitud de clave  : {resultado['longitud_clave']}")
    print(f"  Mensaje descifrado : '{resultado['mensaje']}'")
    print(f"  Confianza          : {resultado['confianza']:.2f}")

    if resultado["mensaje"] == texto_prueba:
        print("\nRESULTADO: ÉXITO. Mensaje recuperado automáticamente, sin intervención del usuario.")
    elif resultado["mensaje"].lower() == texto_prueba.lower():
        print("\nRESULTADO: ÉXITO (clave equivalente). Mismo mensaje, diferencias menores de mayúsculas/minúsculas.")
    else:
        print("\nRESULTADO: Aproximación obtenida.")
        print(f"  Esperado : {texto_prueba}")
        print(f"  Obtenido : {resultado['mensaje']}")