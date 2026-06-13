def guardar(nombre, datos):

    with open(nombre, "w", encoding="utf-8") as archivo:

        for distancia, longitud, caracter in datos:

            archivo.write(
                f"{distancia}|{longitud}|{caracter}\n"
            )

def cargar(nombre):

    datos = []

    with open(nombre, "r", encoding="utf-8") as archivo:

        for linea in archivo:

            linea = linea.rstrip("\n")

            if linea == "":
                continue

            partes = linea.split("|")

            distancia = int(partes[0])
            longitud = int(partes[1])

            caracter = ""

            if len(partes) > 2:
                caracter = partes[2]

            datos.append(
                (distancia,
                 longitud,
                 caracter)
            )

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
 
def generar_pista():

    with open("pistas/pista_lz77.txt", "w", encoding="utf-8") as archivo:

        archivo.write("ALGORITMO=LZ77\n")
        archivo.write("VENTANA=20\n")
        archivo.write("FORMATO=(DISTANCIA,LONGITUD,SIGUIENTE)\n")