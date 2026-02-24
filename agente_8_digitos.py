class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self._siguiente = None
        self._anterior = None


class ListaDoblementeEnlazada:
    def __init__(self):
        self._inicio = None
        self._fin = None
        self._tamano = 0

    def agregar_al_final(self, valor):
        nuevo_nodo = Nodo(valor)
        if not self._fin:
            self._inicio = nuevo_nodo
            self._fin = nuevo_nodo
        else:
            nuevo_nodo._anterior = self._fin
            self._fin._siguiente = nuevo_nodo
            self._fin = nuevo_nodo
        self._tamano += 1

    def remover_del_inicio(self):
        retorno = None
        if self._inicio:
            retorno = self._inicio.valor
            if self._inicio is self._fin:
                self._inicio = None
                self._fin = None
            else:
                self._inicio = self._inicio._siguiente
                self._inicio._anterior = None
            self._tamano -= 1
        return retorno

    def __len__(self):
        return self._tamano


class Estado:
    def __init__(self, fichas):
        self.fichas = fichas
        self.anterior = None

    def __repr__(self):
        s = ""
        for i in range(len(self.fichas)):
            for j in range(len(self.fichas[i])):
                s += "{} ".format(self.fichas[i][j])
            s += "\n"
        return s

    def __eq__(self, otro):
        if not isinstance(otro, Estado):
            return False
        return self.fichas == otro.fichas

    def __hash__(self):
        return hash(tuple([tuple(x) for x in self.fichas]))

    def copiar(self):
        fichas_copia = []
        for i in range(len(self.fichas)):
            fichas_copia.append([])
            for j in range(len(self.fichas[i])):
                fichas_copia[i].append(self.fichas[i][j])
        return Estado(fichas_copia)

    def es_objetivo(self, fichas_objetivo):
        return self.fichas == fichas_objetivo

    def obtener_vecinos(self):
        N = len(self.fichas)
        vecinos = []
        fila = 0
        columna = 0

        for i in range(N):
            for j in range(N):
                if self.fichas[i][j] == " ":
                    fila = i
                    columna = j

        movimientos = [
            [fila - 1, columna],
            [fila + 1, columna],
            [fila, columna - 1],
            [fila, columna + 1]
        ]

        for [i, j] in movimientos:
            if 0 <= i < N and 0 <= j < N:
                nuevo_estado = self.copiar()
                nuevo_estado.fichas[fila][columna], nuevo_estado.fichas[i][j] = nuevo_estado.fichas[i][j], \
                nuevo_estado.fichas[fila][columna]
                vecinos.append(nuevo_estado)

        return vecinos

    def resolver(self, fichas_objetivo):
        frontera = ListaDoblementeEnlazada()
        frontera.agregar_al_final(self)

        en_frontera = set([self])
        visitados = set([])

        while len(frontera) > 0:
            vertice_actual = frontera.remover_del_inicio()
            visitados.add(vertice_actual)
            en_frontera.remove(vertice_actual)

            if vertice_actual.es_objetivo(fichas_objetivo):
                solucion = [vertice_actual]
                while vertice_actual.anterior:
                    vertice_actual = vertice_actual.anterior
                    solucion.append(vertice_actual)
                solucion.reverse()
                return solucion

            else:
                for vecino in vertice_actual.obtener_vecinos():
                    if vecino not in en_frontera and vecino not in visitados:
                        en_frontera.add(vecino)
                        vecino.anterior = vertice_actual
                        frontera.agregar_al_final(vecino)

        return None


if __name__ == '__main__':
    tablero_inicial = [
        [7, 2, 4],
        [5, " ", 6],
        [8, 3, 1]
    ]

    tablero_objetivo = [
        [" ", 1, 2],
        [3, 4, 5],
        [6, 7, 8]
    ]

    print("calculando solución")
    estado_inicial = Estado(tablero_inicial)

    solucion = estado_inicial.resolver(tablero_objetivo)

    if solucion:
        print(f"\nsolución encontrada en {len(solucion) - 1} movimientos\n")
        paso_num = 0
        for paso in solucion:
            print(f"Paso {paso_num}:")
            print(paso)
            paso_num += 1
    else:
        print("el tablero no tiene solución")