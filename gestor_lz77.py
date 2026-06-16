from lz77 import (
    LZ77,
    leer_texto,
    guardar_texto,
    guardar,
    cargar,
    generar_json_lz77,
    leer_json_lz77,
    obtener_tripletas
)

import json


def comprimir_archivo(
    ruta_entrada,
    ruta_bin,
    ruta_json
):

    lz = LZ77(ventana=20)

    texto = leer_texto(
        ruta_entrada
    )

    comprimido = lz.comprimir(
        texto
    )

    guardar(
        ruta_bin,
        comprimido
    )

    datos_json = generar_json_lz77(
        comprimido,
        lz.ventana
    )

    with open(
        ruta_json,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos_json,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    return comprimido


def descomprimir_archivo(
    ruta_bin,
    ruta_json,
    ruta_salida
):

    lz = LZ77()

    datos_json = leer_json_lz77(
        ruta_json
    )

    tripletas = obtener_tripletas(
        datos_json
    )

    texto = lz.descomprimir(
        tripletas
    )

    guardar_texto(
        ruta_salida,
        texto
    )

    return texto