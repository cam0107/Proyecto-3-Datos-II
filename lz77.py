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