import json
import struct

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

    for idx, (offset, longitud, siguiente) in enumerate(tripletas):
        offset_val = "_" if idx == 0 else offset
        siguiente_val = "_" if (siguiente == "" or siguiente is None) else siguiente
        datos["compresion"][0]["estructura"]["tripletas"].append(
            {
                "offset": offset_val,
                "longitud": longitud,
                "siguiente": siguiente_val
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
    """
    tripletas = []
    
    compresiones = datos_json.get("compresion", [])
    
    if isinstance(compresiones, dict):
        compresiones = [compresiones]
        
    for bloque in compresiones:
        if isinstance(bloque, dict) and bloque.get("algoritmo") == "LZ77":
            estructura = bloque.get("estructura", {})
            for t in estructura.get("tripletas", []):
                offset_val = t["offset"]
                offset = 0 if offset_val == "_" or offset_val == 0 or not offset_val else int(offset_val)
                siguiente_val = t["siguiente"]
                if siguiente_val in ("_", "null", "None") or not siguiente_val:
                    siguiente = ""
                else:
                    siguiente = siguiente_val
                tripletas.append(
                    (
                        offset,
                        int(t["longitud"]),
                        siguiente
                    )
                )
            break

    return tripletas


def guardar(nombre, datos):
    contenido_lista = []
    for idx, (distancia, longitud, caracter) in enumerate(datos):
        dist_str = "_" if idx == 0 else str(distancia)
        caracter_str = "_" if (caracter == "" or caracter is None) else caracter
        contenido_lista.append(f"({dist_str},{longitud},{caracter_str})")
    contenido = "".join(contenido_lista)
    datos_binarios = contenido.encode('ascii', errors='replace')
    with open(nombre, "wb") as archivo:
        archivo.write(datos_binarios)


def cargar(nombre):
    datos = []
    with open(nombre, "rb") as archivo:
        bytes_data = archivo.read()
        
    if not bytes_data:
        return datos
        
    contenido = bytes_data.decode('ascii', errors='replace').strip()
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
                
            dist_str = contenido[i+1:first_comma].strip()
            distancia = 0 if dist_str == '_' or not dist_str else int(dist_str)
            
            len_str = contenido[first_comma+1:second_comma].strip()
            longitud = 0 if len_str == '_' or not len_str else int(len_str)
            
            caracter = contenido[second_comma+1:close_paren]
            if caracter in ("_", "null", "None") or not caracter:
                caracter = ""
                
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