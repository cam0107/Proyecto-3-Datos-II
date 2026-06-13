import json


def generar_json_lz77(
    tripletas,
    ventana
):

    datos = {
        "compresion": {
            "algoritmo": "LZ77",
            "version": "1.0",
            "estructura": {
                "tamano_buffer_busqueda": ventana,
                "tamano_buffer_lectura": 10,
                "tripletas": []
            }
        }
    }

    for offset, longitud, siguiente in tripletas:

        datos["compresion"]["estructura"]["tripletas"].append(
            {
                "offset": offset,
                "longitud": longitud,
                "siguiente": siguiente
            }
        )

    return datos


def leer_json_lz77(ruta):

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:

        datos = json.load(archivo)

    return datos


def obtener_tripletas(datos_json):

    tripletas = []

    for t in datos_json["compresion"]["estructura"]["tripletas"]:

        tripletas.append(
            (
                t["offset"],
                t["longitud"],
                t["siguiente"]
            )
        )

    return tripletas