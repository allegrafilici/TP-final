import numpy as np
import pygame as py

class Mapa:
    def __init__(self, tiles):
        self.tiles = tiles
        self.grilla = self.iniciar_mapa()
        self.filas, self.columnas = self.grilla.shape

    def iniciar_mapa(self):
        """
        Lee el archivo mapa.txt y construye la grilla del juego.

        VALIDACIONES (lanza ValueError si algo falla):
            1. Todos los caracteres deben ser conocidos:
               X . o (espacio) G - P T
            2. Todas las filas deben tener el mismo largo.
            3. Debe existir exactamente una posicion de Pac-Man ('P').
            4. Debe existir al menos una puerta de ghost house ('-').

        Si el archivo no existe, Python lanza FileNotFoundError automaticamente.
        """
        with open("assets/mapa.txt", "r") as archivo:
            mapa_texto = archivo.read()

        lineas_mapa = mapa_texto.strip().split("\n")

        # Validacion 1: todas las filas tienen el mismo largo 
        largo_primera_fila = len(lineas_mapa[0])
        for numero_fila, linea in enumerate(lineas_mapa):
            if len(linea) != largo_primera_fila:
                raise ValueError(
                    f"Error en el mapa: la fila {numero_fila} tiene "
                    f"{len(linea)} columnas pero se esperaban "
                    f"{largo_primera_fila} (igual que la fila 0)."
                )

        # Validacion 2 y 3: caracteres validos, P y - presentes
        caracteres_validos = set("X.o G-PT")
        hay_pacman  = False
        hay_puerta  = False
        mapa_nuevo  = []

        for numero_fila, linea in enumerate(lineas_mapa):
            fila = []
            for numero_col, caracter in enumerate(linea):

                if caracter not in caracteres_validos:
                    raise ValueError(
                        f"Error en el mapa: caracter desconocido '{caracter}' "
                        f"en fila {numero_fila}, columna {numero_col}. "
                        f"Los caracteres validos son: X . o (espacio) G - P T"
                    )

                if caracter == "P":
                    hay_pacman = True
                if caracter == "-":
                    hay_puerta = True

                fila.append(caracter)
            mapa_nuevo.append(fila)

        if not hay_pacman:
            raise ValueError(
                "Error en el mapa: no se encontro la posicion inicial de "
                "Pac-Man ('P'). El mapa debe tener exactamente un tile 'P'."
            )

        if not hay_puerta:
            raise ValueError(
                "Error en el mapa: no se encontro la puerta de la ghost "
                "house ('-'). El mapa debe tener al menos un tile '-'."
            )

        return np.array(mapa_nuevo)

    def es_solido(self, fila, col):
        if fila < 0 or fila >= self.filas or col < 0 or col >= self.columnas:
            return True
        caracter = self.grilla[fila, col]
        if caracter in self.tiles:
            return self.tiles[caracter]["es_solido"]
        return True

    def actualizar_celda(self, fila, col, nuevo_tile):
        self.grilla[fila, col] = nuevo_tile

    def obtener_posiciones_iniciales(self):
        pos_pacman = (1, 1)
        pos_puerta = None

        for fila in range(self.filas):
            for col in range(self.columnas):
                if self.grilla[fila, col] == "P":
                    pos_pacman = (col, fila)
                elif self.grilla[fila, col] == "-" and pos_puerta is None:
                    pos_puerta = (col, fila)

        if pos_puerta is not None:
            col_p, fila_p = pos_puerta
            pos_blinky = (col_p,     fila_p - 1)
            pos_pinky  = (col_p,     fila_p + 2)
            pos_inky   = (col_p - 2, fila_p + 2)
            pos_clyde  = (col_p + 2, fila_p + 2)
            pos_patan  = (col_p - 1, fila_p + 2)
            pos_negui  = (col_p + 1, fila_p + 2)
        else:
            pos_blinky = pos_pinky = pos_inky = pos_clyde = pos_patan = pos_negui = (1, 1)

        return pos_pacman, pos_blinky, pos_pinky, pos_inky, pos_clyde, pos_patan, pos_negui


config_tiles = {
    "X": {"tipo": "pared",          "color": (0, 0, 255),     "score": 0,  "es_fijo": True,  "es_solido": True},
    ".": {"tipo": "punto",          "color": (255, 255, 255), "score": 10, "es_fijo": False, "es_solido": False},
    "o": {"tipo": "punto de poder", "color": (255, 255, 255), "score": 50, "es_fijo": False, "es_solido": False},
    " ": {"tipo": "pasillo vacio",  "color": (0, 0, 0),       "score": 0,  "es_fijo": True,  "es_solido": False},
    "G": {"tipo": "ghost house",    "color": None,            "score": 0,  "es_fijo": True,  "es_solido": False},
    "-": {"tipo": "puerta",         "color": None,            "score": 0,  "es_fijo": True,  "es_solido": True},
    "P": {"tipo": "pos pac",        "color": None,            "score": 0,  "es_fijo": True,  "es_solido": False},
    "T": {"tipo": "tunel",          "color": None,            "score": 0,  "es_fijo": True,  "es_solido": False},
}