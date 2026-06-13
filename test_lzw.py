import os
import sys
import inspect

print("=" * 60)
print("   PROBADOR INTELIGENTE DE INTEGRACIÓN (LZW.py + LZW_tool.py)")
print("=" * 60)

# Importación 
try:
    import LZW
    print("✅ Módulo 'LZW.py' cargado.")
except ImportError:
    print("❌ Error: No se encontró 'LZW.py' en esta carpeta.")
    sys.exit(1)



def correr_prueba(archivo_texto):
    if not os.path.exists(archivo_texto):
        print(f"\n[!] Creando archivo '{archivo_texto}' para la prueba...")
        with open(archivo_texto, "w", encoding="utf-8") as f:
            f.write("EL GATO COME PESCADO Y EL PERRO COME HUESO")

    # Paso 1: Leer el TXT
    with open(archivo_texto, 'r', encoding='utf-8', errors='ignore') as f:
        texto_original = f.read()
    print(f"\n[1] Texto original leído con éxito ({len(texto_original)} caracteres).")

    # Paso 2: Comprimir con el algoritmo de LZW.py
    print("[2] Comprimiendo con LZW.lzw_compress()...")
    codigos, diccionario_final = LZW.lzw_compress(texto_original)

    # Nombres de archivos de salida
    nombre_base, _ = os.path.splitext(archivo_texto)
    archivo_binario = f"{nombre_base}.bin"
    archivo_pistas = "pistas_compresion.json"

    # Paso 3: Guardar el binario con LZW_tool.py
    print("[3] Guardando binario con LZW_tool.guardar_archivo_binario()...")
    LZW.guardar_archivo_binario(codigos, archivo_binario)

    # Paso 4: Guardar las pistas esquivando el AttributeError
    print("[4] Generando JSON de pistas de forma segura...")
    
    # Analizamos cuántos parámetros pide la función de tu LZW_tool.py
    firma = inspect.signature(LZW.generar_archivo_pistas_json)
    num_parametros = len(firma.parameters)

    if num_parametros >= 4:
        # pide(mensaje, codigos, diccionario, nombre)
        LZW.generar_archivo_pistas_json(texto_original, codigos, diccionario_final, archivo_pistas)
    else:
        #pide 
        LZW.generar_archivo_pistas_json(codigos, diccionario_final, archivo_pistas)
    print("    ✔ Archivo JSON de pistas guardado correctamente.")

    # Paso 5: Leer el binario 
    print("[5] Leyendo binario con LZW.leer_archivo_binario()...")
    codigos_recuperados = LZW.leer_archivo_binario(archivo_binario)

    # Paso 6: Descomprimir con el algoritmo de LZW
    print("[6] Descomprimiendo con LZW.lzw_decompress()...")
    texto_restaurado = LZW.lzw_decompress(codigos_recuperados)

    # Paso 7: Guardar el resultado final limpio
    archivo_salida_txt = f"{nombre_base}_restaurado.txt"
    with open(archivo_salida_txt, 'w', encoding='utf-8') as f:
        f.write(texto_restaurado)

    # Verificación final de bytes e integridad
    print("\n" + "="*45)
    print("      AUDITORÍA FINAL DEL TORNEO LZW")
    print("="*45)
    if texto_original == texto_restaurado:
        print(" ¡SISTEMA FUNCIONANDO")
        print(f"   -> Binario generado: {archivo_binario}")
        print(f"   -> Pistas generadas: {archivo_pistas}")
        print(f"   -> Texto restaurado: {archivo_salida_txt} (INTEGRO)")
    else:
        print(" ERROR: El texto recuperado no coincide con el original.")
    print("="*45)

if __name__ == "__main__":
    correr_prueba("prueba_torneo.txt")
