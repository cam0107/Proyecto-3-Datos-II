import json

class LZ77:

    def __init__(self, ventana=20):
        self.ventana = ventana

    def comprimir(self, texto):

        resultado = []
        i = 0

        while i < len(texto):

            mejor_distancia = 0
            mejor_longitud = 0

            inicio_ventana = max(0, i - self.ventana)

            for j in range(inicio_ventana, i):

                longitud = 0

                while (
                    i + longitud < len(texto)
                    and texto[j + longitud] == texto[i + longitud]
                ):

                    longitud += 1

                    if j + longitud >= i:
                        break

                if longitud > mejor_longitud:
                    mejor_longitud = longitud
                    mejor_distancia = i - j

            if mejor_longitud > 0:

                siguiente = ""

                if i + mejor_longitud < len(texto):
                    siguiente = texto[i + mejor_longitud]

                resultado.append(
                    (
                        mejor_distancia,
                        mejor_longitud,
                        siguiente
                    )
                )

                i += mejor_longitud + 1

            else:

                resultado.append(
                    (
                        0,
                        0,
                        texto[i]
                    )
                )

                i += 1

        return resultado

    def descomprimir(self, datos):

        texto = ""

        for distancia, longitud, siguiente in datos:

            if distancia == 0:

                texto += siguiente

            else:

                inicio = len(texto) - distancia

                texto += texto[inicio:inicio + longitud]

                texto += siguiente

        return texto


# GENERADOR DE JSON LZ77



def generar_json_lz77(
    tripletas,
    ventana
):
    """
    Genera el diccionario compatible con el JSON oficial (lista de compresiones).
    """
    datos = {
        "compresion": [
            {
                "algoritmo": "LZ77",
                "estructura": {
                    "tamano_buffer_busqueda": ventana,
                    "tamano_buffer_lectura": 10,
                    "tripletas": []
                }
            }
        ]
    }

    for offset, longitud, siguiente in tripletas:
        datos["compresion"][0]["estructura"]["tripletas"].append(
            {
                "offset": offset,
                "longitud": longitud,
                "siguiente": siguiente
            }
        )

    return datos


def leer_json_lz77(ruta):
    """
    Lee las pistas JSON desde un archivo.
    """
    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:
        datos = json.load(archivo)

    return datos


def obtener_tripletas(datos_json):
    """
    Extrae las tripletas de LZ77 buscando en la lista de compresiones.
    Soporta formato de lista (nuevo) y objeto (antiguo) para evitar crasheos.
    """
    tripletas = []
    
    compresiones = datos_json.get("compresion", [])
    
    # Manejo robusto de retrocompatibilidad
    if isinstance(compresiones, dict):
        compresiones = [compresiones]
        
    for bloque in compresiones:
        if isinstance(bloque, dict) and bloque.get("algoritmo") == "LZ77":
            estructura = bloque.get("estructura", {})
            for t in estructura.get("tripletas", []):
                tripletas.append(
                    (
                        t["offset"],
                        t["longitud"],
                        t["siguiente"]
                    )
                )
            break

    return tripletas


def guardar(nombre, datos):
    with open(nombre, "w", encoding="utf-8") as archivo:
        for distancia, longitud, caracter in datos:
            archivo.write(f"({distancia},{longitud},{caracter})")


def cargar(nombre):
    datos = []
    with open(nombre, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
    
    i = 0
    while i < len(contenido):
        if contenido[i] == '(':
            first_comma = contenido.find(',', i)
            if first_comma == -1:
                break
            second_comma = contenido.find(',', first_comma + 1)
            if second_comma == -1:
                break
            close_paren = contenido.find(')', second_comma + 1)
            if close_paren == -1:
                break
                
            distancia = int(contenido[i+1:first_comma])
            longitud = int(contenido[first_comma+1:second_comma])
            caracter = contenido[second_comma+1:close_paren]
            
            datos.append((distancia, longitud, caracter))
            i = close_paren + 1
        else:
            i += 1

    return datos


def leer_texto(ruta):
    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:
        return archivo.read()


def guardar_texto(
    ruta,
    texto
):
    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:
        archivo.write(texto)