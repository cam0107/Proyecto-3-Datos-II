from gestor_lz77 import (
    comprimir_archivo,
    descomprimir_archivo
)

print("Comprimiendo...")

comprimir_archivo(
    "entradas/mensaje.txt",
    "comprimidos/mensaje_lz77.bin",
    "json/mensaje_lz77.json"
)

print("Descomprimiendo...")

texto = descomprimir_archivo(
    "comprimidos/mensaje_lz77.bin",
    "json/mensaje_lz77.json",
    "salidas/mensaje_recuperado.txt"
)

print("\nTexto recuperado:")
print(texto)

print("\nProceso completado")