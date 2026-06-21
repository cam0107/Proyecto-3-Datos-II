"""
Funciones para leer y escribir los archivos .txt con formato de etiquetas
usados por la interfaz del reto 2
Formato de entrada para cifrar (archivo .txt):
    mensaje: El texto que se quiere cifrar
    clave: CLAVE123
Formato de salida al descifrar (archivo .txt):
    Resultado principal (mas probable), seguido de 2 candidatos de respaldo.
"""

def leer_mensaje_y_clave(ruta_txt):
    """
    Lee un archivo .txt con formato de etiquetas y extrae el mensaje y la clave.
    Acepta lineas con el formato:
        mensaje: texto aqui
        clave: texto aqui
    No distingue mayusculas/minusculas en la etiqueta (Mensaje:, MENSAJE:, etc.
    funcionan igual). Si el mensaje ocupa varias lineas, todas las lineas
    despues de "mensaje:" y antes de "clave:" se consideran parte del mensaje.
    Parametros:
        ruta_txt (str): ruta al archivo .txt de entrada
    Retorna:
        tuple (str, str): (mensaje, clave)
        ValueError: si no se encuentran ambas etiquetas en el archivo
    """
    with open(ruta_txt, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    mensaje_partes = []
    clave = None
    modo_actual = None

    for linea in lineas:
        linea_sin_salto = linea.rstrip('\n')
        linea_lower = linea_sin_salto.strip().lower()

        if linea_lower.startswith("mensaje:"):
            modo_actual = "mensaje"
            contenido = linea_sin_salto.split(":", 1)[1].strip()
            if contenido:
                mensaje_partes.append(contenido)
        elif linea_lower.startswith("clave:"):
            modo_actual = "clave"
            clave = linea_sin_salto.split(":", 1)[1].strip()
        elif modo_actual == "mensaje" and linea_sin_salto.strip():
            mensaje_partes.append(linea_sin_salto.strip())

    mensaje = " ".join(mensaje_partes).strip()

    if not mensaje:
        raise ValueError("No se encontró la etiqueta 'mensaje:' con contenido en el archivo.")
    if clave is None or clave == "":
        raise ValueError("No se encontró la etiqueta 'clave:' con contenido en el archivo.")

    return mensaje, clave

def escribir_resultado_descifrado(ruta_txt, resultado_principal, candidatos_respaldo):
    """
    Escribe el archivo .txt de salida con el resultado del descifrado.
    Muestra primero el candidato principal (el de mayor puntaje, el que
    el software determina como mas probable), y debajo hasta 2 candidatos
    de respaldo por si el principal no fuera el correcto.
    Parametros:
        ruta_txt (str): ruta del archivo .txt a generar
        resultado_principal (dict): {"clave", "mensaje", "longitud_clave", "confianza"}
        candidatos_respaldo (list[tuple]): lista de (longitud, clave, puntaje, texto)
    """
    with open(ruta_txt, 'w', encoding='utf-8') as f:
        f.write("-" * 60 + "\n")
        f.write("RESULTADO PRINCIPAL (mayor probabilidad)\n")
        f.write("-" * 60 + "\n\n")
        f.write(f"clave: {resultado_principal['clave']}\n")
        f.write(f"mensaje: {resultado_principal['mensaje']}\n")
        f.write(f"confianza: {resultado_principal['confianza']:.2f}\n")

        if candidatos_respaldo:
            f.write("\n\n" + "-" * 60 + "\n")
            f.write("CANDIDATOS DE RESPALDO (por si el principal no es correcto)\n")
            f.write("-" * 60 + "\n")
            for i, (longitud, clave, puntaje, texto) in enumerate(candidatos_respaldo, 1):
                f.write(f"\nCandidato #{i+1}\n")
                f.write(f"  clave: {clave}\n")
                f.write(f"  mensaje: {texto}\n")
                f.write(f"  confianza: {puntaje:.2f}\n")