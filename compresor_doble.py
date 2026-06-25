import json
import os
import LZW
import huffman

def comprimir_lzw_mas_huffman(ruta_txt_ingreso, ruta_bin_salida, ruta_json_salida):
    # texto original
    with open(ruta_txt_ingreso, 'r', encoding='utf-8') as f:
        texto_original = f.read()
    
    if not texto_original:
        return

    # COMPRESIÓN LZW 
    # 
    codigos_lzw, diccionario_lzw = LZW.lzw_compress(texto_original)
    
    # Convertimos la lista de códigos LZW a un string de texto intermedio para que Huffman pueda leerlo
    
    texto_intermedio = " ".join(map(str, codigos_lzw))

    #COMPRESIÓN HUFFMAN 
    # Aplicamos Huffman sobre el string generado por LZW
    nodo_raiz_huffman = huffman.build_huffman_tree(texto_intermedio)
    codigos_huffman = huffman.generate_codes(nodo_raiz_huffman)
    bits_encriptados = huffman.encode_text(texto_intermedio, codigos_huffman)

    # GUARDAR ARCHIVO BINARIO (.bin)
    datos_binarios = bits_encriptados.encode('ascii', errors='replace')
    with open(ruta_bin_salida, 'wb') as f_bin:
        f_bin.write(datos_binarios)

    #GENERAR EL JSON DE PISTAS DOBLE
    # Estructura de pistas de Huffman
    pistas_huffman = huffman.generate_json_structure(nodo_raiz_huffman, codigos_huffman)
    # Estructura de pistas de LZW 
    pistas_lzw = {
        "algoritmo": "LZW",
        "estructura": {
            "salida": codigos_lzw,
            "diccionario": {str(k): v for k, v in diccionario_lzw.items()}
        }
    }

    # Unificamos ambas pistas en el arreglo "compresion" del JSON

    json_final = {
        "compresion": [
            pistas_huffman["compresion"][0],  # Bloque de Huffman
            pistas_lzw                        # Bloque de LZW
        ]
    }

    with open(ruta_json_salida, 'w', encoding='utf-8') as f_json:
        json.dump(json_final, f_json, indent=4, ensure_ascii=False)