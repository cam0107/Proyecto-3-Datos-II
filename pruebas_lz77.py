from lz77 import (
    LZ77,
    guardar,
    cargar,
    leer_texto,
    guardar_texto,
    generar_json_lz77
)
import json

lz = LZ77(
    ventana=20
)

texto = leer_texto(
    "entradas/mensaje.txt"
)

print("Texto original:")
print(texto)

comprimido = lz.comprimir(texto)

print("\nDatos comprimidos:")
print(comprimido)

guardar(
    "comprimidos/mensaje_lz77.bin",
    comprimido
)

json_lz77 = generar_json_lz77(
    comprimido,
    lz.ventana
)

with open(
    "json/mensaje_lz77.json",
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        json_lz77,
        archivo,
        indent=4,
        ensure_ascii=False
    )

datos = cargar(
    "comprimidos/mensaje_lz77.bin"
)

resultado = lz.descomprimir(datos)

print("\nTexto recuperado:")
print(resultado)

print("\nValidación:")

if texto == resultado:
    print("Compresión correcta")
else:
    print("Error")

# ==========================
# ESTADÍSTICAS
# ==========================

print("\nEstadísticas")

print("Caracteres originales:", len(texto))
print("Tuplas generadas:", len(comprimido))
porcentaje = (
    (
        len(texto)
        - len(comprimido)
    )
    / len(texto)
) * 100

print(
    "Compresión aproximada:",
    round(porcentaje, 2),
    "%"
)

# ==========================
# PRUEBA DESDE JSON
# ==========================

from lz77 import leer_json_lz77
from lz77 import obtener_tripletas

datos_json = leer_json_lz77(
    "json/mensaje_lz77.json"
)

tripletas = obtener_tripletas(
    datos_json
)

resultado_json = lz.descomprimir(
    tripletas
)

print("\nPrueba desde JSON:")
print(resultado_json)

if resultado_json == texto:
    print("JSON correcto")
else:
    print("Error en JSON")