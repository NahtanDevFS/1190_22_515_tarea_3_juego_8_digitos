import tkinter as tk
from tkinter import messagebox
import threading
import copy

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
        n_filas = len(self.fichas)
        vecinos = []
        fila = 0
        columna = 0

        for i in range(n_filas):
            for j in range(n_filas):
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
            if 0 <= i < n_filas and 0 <= j < n_filas:
                nuevo_estado = self.copiar()
                nuevo_estado.fichas[fila][columna], nuevo_estado.fichas[i][j] = \
                    nuevo_estado.fichas[i][j], nuevo_estado.fichas[fila][columna]
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


class JuegoOchoDigitosGUI:
    def __init__(self, ventana_principal):
        self.ventana_principal = ventana_principal

        self.COLOR_FONDO = "#F0F0F0"
        self.COLOR_TEXTO = "#000000"
        self.COLOR_FICHA = "#E0E0E0"
        self.COLOR_FICHA_VACIA = "#C0C0C0"

        self.ventana_principal.title("Jonathan Franco 1190-22-515")
        self.ventana_principal.geometry("400x520")
        self.ventana_principal.configure(bg=self.COLOR_FONDO)

        self.tablero_inicial = [
            [7, 2, 4],
            [5, " ", 6],
            [8, 3, 1]
        ]
        self.tablero_objetivo = [
            [" ", 1, 2],
            [3, 4, 5],
            [6, 7, 8]
        ]

        self.tablero_actual = copy.deepcopy(self.tablero_inicial)
        self.botones_cuadricula = []
        self.bloquear_interfaz = False

        self._construir_interfaz()
        self._actualizar_vista()

    def _construir_interfaz(self):
        tk.Label(
            self.ventana_principal,
            text="Juego de los 8 dígitos",
            font=("Arial", 18, "bold"),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO
        ).pack(pady=(15, 5))

        tk.Label(
            self.ventana_principal,
            text="Jonathan Franco 1190-22-515",
            font=("Arial", 10),
            bg=self.COLOR_FONDO,
            fg="#555555"
        ).pack(pady=(0, 15))

        marco_tablero = tk.Frame(self.ventana_principal, bg=self.COLOR_FONDO)
        marco_tablero.pack(pady=10)

        for i in range(3):
            fila_botones = []
            for j in range(3):
                boton = tk.Button(
                    marco_tablero,
                    text="",
                    font=("Arial", 28, "bold"),
                    width=3,
                    height=1,
                    relief="raised",
                    command=lambda f=i, c=j: self.mover_ficha_usuario(f, c)
                )
                boton.grid(row=i, column=j, padx=2, pady=2)
                fila_botones.append(boton)
            self.botones_cuadricula.append(fila_botones)

        self.etiqueta_estado = tk.Label(
            self.ventana_principal,
            text="presiona resolver",
            font=("Arial", 10),
            bg=self.COLOR_FONDO, fg="blue"
        )
        self.etiqueta_estado.pack(pady=(15, 10))

        marco_controles = tk.Frame(self.ventana_principal, bg=self.COLOR_FONDO)
        marco_controles.pack(pady=10)

        self.boton_reiniciar = tk.Button(
            marco_controles,
            text="Reiniciar",
            font=("Arial", 10),
            command=self.reiniciar_juego,
            width=10
        )
        self.boton_reiniciar.grid(row=0, column=0, padx=10)

        self.boton_resolver = tk.Button(
            marco_controles,
            text="Resolver con agente",
            font=("Arial", 10),
            command=self.iniciar_resolucion_ia,
            width=18
        )
        self.boton_resolver.grid(row=0, column=1, padx=10)

    def _actualizar_vista(self):
        for i in range(3):
            for j in range(3):
                valor = self.tablero_actual[i][j]
                boton = self.botones_cuadricula[i][j]

                if valor == " ":
                    boton.configure(
                        text="",
                        bg=self.COLOR_FICHA_VACIA,
                        state=tk.DISABLED
                    )
                else:
                    boton.configure(
                        text=str(valor),
                        bg=self.COLOR_FICHA,
                        fg=self.COLOR_TEXTO,
                        state=tk.NORMAL if not self.bloquear_interfaz else tk.DISABLED
                    )

        if self.tablero_actual == self.tablero_objetivo:
            self.etiqueta_estado.configure(text="Rompecabezas resuelto con éxito", fg="green")
            self.bloquear_interfaz = True
            for fila in self.botones_cuadricula:
                for boton in fila:
                    boton.configure(state=tk.DISABLED)

    def mover_ficha_usuario(self, fila, columna):
        if self.bloquear_interfaz:
            return

        fila_vacia, columna_vacia = -1, -1
        for i in range(3):
            for j in range(3):
                if self.tablero_actual[i][j] == " ":
                    fila_vacia, columna_vacia = i, j

        es_adyacente = (abs(fila_vacia - fila) + abs(columna_vacia - columna)) == 1

        if es_adyacente:
            ficha_movida = self.tablero_actual[fila][columna]
            self.tablero_actual[fila_vacia][columna_vacia] = ficha_movida
            self.tablero_actual[fila][columna] = " "
            self._actualizar_vista()

    def reiniciar_juego(self):
        self.tablero_actual = copy.deepcopy(self.tablero_inicial)
        self.bloquear_interfaz = False
        self.etiqueta_estado.configure(text="Mueve las piezas o presiona resolver", fg="blue")
        self.boton_resolver.configure(state=tk.NORMAL)
        self._actualizar_vista()

    def iniciar_resolucion_ia(self):
        self.bloquear_interfaz = True
        self._actualizar_vista()
        self.boton_resolver.configure(state=tk.DISABLED)
        self.boton_reiniciar.configure(state=tk.DISABLED)
        self.etiqueta_estado.configure(text="IA procesando solución...", fg="orange")

        hilo_agente = threading.Thread(target=self._ejecutar_agente)
        hilo_agente.start()

    def _ejecutar_agente(self):
        estado_actual = Estado(self.tablero_actual)
        solucion = estado_actual.resolver(self.tablero_objetivo)

        if solucion:
            self.ventana_principal.after(0, self._preparar_animacion, solucion)
        else:
            self.ventana_principal.after(0, self._mostrar_error_solucion)

    def _mostrar_error_solucion(self):
        self.etiqueta_estado.configure(text="Error: No se encontró solución.", fg="red")
        self.boton_reiniciar.configure(state=tk.NORMAL)

    def _preparar_animacion(self, solucion):
        pasos = len(solucion) - 1
        self.etiqueta_estado.configure(
            text=f"Solución encontrada. Ejecutando {pasos} pasos...",
            fg="green"
        )
        self._animar_paso(solucion, 0, pasos)

    def _animar_paso(self, solucion, indice, total_pasos):
        if indice < len(solucion):
            estado_paso = solucion[indice].fichas
            self.tablero_actual = copy.deepcopy(estado_paso)
            self._actualizar_vista()

            self.ventana_principal.after(400, self._animar_paso, solucion, indice + 1, total_pasos)
        else:
            self.boton_reiniciar.configure(state=tk.NORMAL)
            messagebox.showinfo("Completado", f"El agente ha resuelto el tablero.\nSe alcanzó en {total_pasos} pasos.")

if __name__ == '__main__':
    raiz = tk.Tk()
    raiz.resizable(False, False)
    app = JuegoOchoDigitosGUI(raiz)
    raiz.mainloop()