import heapq
import json

class HuffmanNode:
    """
    Representa un nodo en el árbol de Huffman.
    """
    def __init__(self, value=None, frequency=0, left=None, right=None):
        self.value = value
        self.frequency = frequency
        self.left = left
        self.right = right

    def is_leaf(self):
        """
        Determina si el nodo es una hoja (contiene un símbolo).
        """
        return self.left is None and self.right is None

    def __lt__(self, other):
        """
        Comparador para el heap de prioridad.
        """
        return self.frequency < other.frequency


def build_huffman_tree(text):
    """
    Construye el árbol de Huffman a partir de un texto de entrada.
    """
    if not text:
        return None

    # Calcular frecuencias de caracteres
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1

    # Crear cola de prioridad (min-heap)
    heap = []
    counter = 0  # Desempate único
    for char, freq in frequencies.items():
        node = HuffmanNode(value=char, frequency=freq)
        heapq.heappush(heap, (freq, counter, node))
        counter += 1

    # Manejo del caso especial de un único carácter único en el texto
    if len(heap) == 1:
        freq, _, single_node = heapq.heappop(heap)
        parent = HuffmanNode(value=None, frequency=freq)
        parent.left = single_node
        return parent

    # Combinar nodos hasta tener una sola raíz
    while len(heap) > 1:
        freq1, _, node1 = heapq.heappop(heap)
        freq2, _, node2 = heapq.heappop(heap)
        
        parent = HuffmanNode(
            value=None, 
            frequency=freq1 + freq2, 
            left=node2, 
            right=node1
        )
        heapq.heappush(heap, (parent.frequency, counter, parent))
        counter += 1

    return heap[0][2]


def generate_codes(node, current_code="", codes=None):
    """
    Recorre el árbol de Huffman para generar los códigos binarios.
    """
    if codes is None:
        codes = {}
        
    if node is None:
        return codes

    if node.is_leaf():
        codes[node.value] = current_code if current_code else "0"
    else:
        generate_codes(node.left, current_code + "0", codes)
        generate_codes(node.right, current_code + "1", codes)

    return codes


def encode_text(text, codes):
    """
    Convierte el texto original en su representación en bits (cadena de '0' y '1').
    """
    return "".join(codes[char] for char in text)


def decode_bits(bit_string, root):
    """
    Decodifica una cadena de bits utilizando el árbol de Huffman.
    Se detiene cuando la secuencia de bits termina, sin requerir longitud del texto
    ni caracteres especiales de parada.
    """
    if not root:
        return ""

    decoded_chars = []
    current_node = root

    for bit in bit_string:
        if bit == '0':
            current_node = current_node.left
        elif bit == '1':
            current_node = current_node.right

        if current_node is not None and current_node.is_leaf():
            decoded_chars.append(current_node.value)
            current_node = root

    return "".join(decoded_chars)


def serialize_tree(node):
    """
    Serializa el árbol de Huffman a un diccionario compatible con JSON.
    """
    if node is None:
        return None
    return {
        "valor": node.value,
        "frecuencia": node.frequency,
        "izquierda": serialize_tree(node.left),
        "derecha": serialize_tree(node.right)
    }


def deserialize_tree(data):
    """
    Deserializa un diccionario de datos JSON en un árbol de nodos HuffmanNode.
    """
    if data is None:
        return None
        
    node = HuffmanNode(
        value=data.get("valor"),
        frequency=data.get("frecuencia", 0)
    )
    node.left = deserialize_tree(data.get("izquierda"))
    node.right = deserialize_tree(data.get("derecha"))
    return node


def generate_json_structure(root, codes):
    """
    Genera la estructura JSON de pistas para Huffman.
    """
    huffman_struct = {
        "arbol": serialize_tree(root),
        "tabla_codigos": codes
    }
    return {
        "compresion": [
            {
                "algoritmo": "Huffman",
                "estructura": huffman_struct
            }
        ]
    }


def bitstring_to_bytes(bit_string):
    """
    Convierte una cadena de bits ("010101...") en un objeto bytes empaquetado.
    El primer byte almacena el número de bits de relleno (padding) añadidos.
    """
    padding = (8 - (len(bit_string) % 8)) % 8
    padded_bits = bit_string + ('0' * padding)
    
    byte_arr = bytearray()
    byte_arr.append(padding)
    for i in range(0, len(padded_bits), 8):
        byte_val = int(padded_bits[i:i+8], 2)
        byte_arr.append(byte_val)
    return bytes(byte_arr)


def bytes_to_bitstring(byte_data):
    """
    Convierte un objeto bytes empaquetado de Huffman de vuelta en una cadena de bits ("010101...").
    Utiliza el primer byte para eliminar los bits de relleno correspondientes.
    """
    if not byte_data:
        return ""
    padding = byte_data[0]
    bit_parts = []
    for b in byte_data[1:]:
        bit_parts.append(f"{b:08b}")
    full_bits = "".join(bit_parts)
    if padding > 0:
        full_bits = full_bits[:-padding]
    return full_bits


if __name__ == "__main__":
    text = input("Ingrese el texto a comprimir: ")
    if text:
        root = build_huffman_tree(text)
        codes = generate_codes(root)
        print("Tabla de códigos generada:", codes)

        # Generar secuencia de bits
        encoded_text = encode_text(text, codes)
        print("Cadena de bits comprimida (archivo.bin):", encoded_text)

        # Generación del JSON de pistas
        pistas = generate_json_structure(root, codes)
        print("JSON de pistas:", pistas)

        #Descompresión
        decoded_text = decode_bits(encoded_text, root)
        print("Texto recuperado:", decoded_text)

        # Verificación
        if text == decoded_text:
            print(" Descompresión exitosa")
        else:
            print(" Descompresión fallida")
