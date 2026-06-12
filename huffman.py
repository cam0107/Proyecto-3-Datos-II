

import heapq

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
    Retorna el nodo raíz del árbol.
    """
    if not text:
        return None

    # Calcular frecuencias de caracteres
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1

    # Crear cola de prioridad (min-heap)
    heap = []
    counter = 0  # Desempate único para evitar comparar objetos HuffmanNode directamente
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
            left=node1, 
            right=node2
        )
        heapq.heappush(heap, (parent.frequency, counter, parent))
        counter += 1

    return heap[0][2]


def generate_codes(node, current_code="", codes=None):
    """
    Recorre el árbol de Huffman recursivamente para generar los códigos
    binarios de cada carácter.
    """
    if codes is None:
        codes = {}
        
    if node is None:
        return codes

    if node.is_leaf():
        # Si el árbol tiene un único carácter (la raíz es hoja), se le asigna "0"
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


def decode_bits(bit_string, root, total_chars):
    """
    Decodifica una cadena de bits utilizando el árbol de Huffman.
    Se detiene exactamente al decodificar la cantidad total de caracteres original,
    ignorando cualquier bit de relleno (padding) al final.
    """
    if not root or total_chars == 0:
        return ""

    decoded_chars = []
    current_node = root
    chars_decoded = 0

    for bit in bit_string:
        if chars_decoded >= total_chars:
            break

        if bit == '0':
            current_node = current_node.left
        else:
            if current_node.right is not None:
                current_node = current_node.right
            else:
                # Si es un árbol de un solo carácter, no hay nodo derecho.
                # Volver a evaluar o mantener el estado.
                pass

        if current_node is not None and current_node.is_leaf():
            decoded_chars.append(current_node.value)
            chars_decoded += 1
            current_node = root

    return "".join(decoded_chars)


def bits_to_bytes(bit_string):
    """
    Empaqueta una cadena de bits ('0' y '1') en un objeto de bytes.
    Añade ceros de relleno (padding) a la derecha en el último byte si es necesario.
    """
    padding_len = (8 - len(bit_string) % 8) % 8
    padded_bits = bit_string + '0' * padding_len
    
    byte_list = []
    for i in range(0, len(padded_bits), 8):
        byte_val = int(padded_bits[i:i+8], 2)
        byte_list.append(byte_val)
        
    return bytes(byte_list)


def bytes_to_bits(bytes_data):
    """
    Convierte un objeto de bytes en su representación de cadena de bits.
    """
    return "".join(f"{byte:08b}" for byte in bytes_data)


def serialize_tree(node):
    """
    Serializa recursivamente el árbol de Huffman a un diccionario compatible con JSON.
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
    Genera el formato JSON de pistas oficial requerido por el proyecto,
    poblando Huffman y creando estructuras vacías/despiste para LZ77, LZ78 y LZW.
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


if __name__ == "__main__":
    text = input("Ingrese el texto a comprimir: ")
    root = build_huffman_tree(text)
    codes = generate_codes(root)
    print("codigos",codes)

    encoded_text = encode_text(text, codes)
    bytes_data = bits_to_bytes(encoded_text)
    decoded_text = decode_bits(encoded_text, root, len(text))
    print("decoded_text",decoded_text)

    serialized_tree = generate_json_structure(root, codes)
    print("pistas:",serialized_tree)  
