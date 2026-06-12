import numpy as np
import pygame as py

class Mapa:
    def __init__(self, tiles):
        self.tiles = tiles
        self.grilla = self.iniciar_mapa()
        self.filas, self.columnas = self.grilla.shape
    
    def iniciar_mapa(self):
        with open("assets/mapa.txt", "r") as archivo:
            mapa_texto = archivo.read()
            
        lineas_mapa = mapa_texto.strip().split("\n")
        mapa_nuevo = []
        for linea in lineas_mapa:
            caracteres_de_fila = []
            for caracter in linea:
                caracteres_de_fila.append(caracter)
            mapa_nuevo.append(caracteres_de_fila)
        
        array_mapa = np.array(mapa_nuevo)
        return array_mapa
    
    def es_solido(self, fila, col):
        #Validación de seguridad por si el cálculo de posición sale de la grilla
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

        #buscamos al pacman y la puerta de la ghost house
        for fila in range(self.filas):
            for col in range(self.columnas):
                if self.grilla[fila, col] == "P":
                    pos_pacman = (col, fila)
                elif self.grilla[fila, col] == "-" and pos_puerta is None:
                    pos_puerta = (col, fila)

        #usamos la posición de la puerta para calcular dinámicamente dónde va cada fantasma
        if pos_puerta is not None:
            col_p, fila_p = pos_puerta
            pos_blinky = (col_p, fila_p - 1)      
            pos_pinky = (col_p, fila_p + 2)      
            pos_inky = (col_p - 2, fila_p + 2)    
            pos_clyde = (col_p + 2, fila_p + 2)   
        else:
            #contemplamos el caso en el que el archivo no tuviese una puerta
            pos_blinky = pos_pinky = pos_inky = pos_clyde = (1, 1)

        return pos_pacman, pos_blinky, pos_pinky, pos_inky, pos_clyde
        

#etiquetamiento de las tiles
config_tiles = {
    "X": {"tipo": "pared", "color": (0, 0, 255), "score":0, "es_fijo": True, "es_solido": True},
    ".": {"tipo": "punto", "color": (255, 255, 255), "score":10, "es_fijo": False, "es_solido": False},
    "o": {"tipo": "punto de poder", "color": (255, 255, 255), "score":50, "es_fijo": False, "es_solido": False},
    " ": {"tipo": "pasillo vacio", "color": (0, 0, 0), "score":0, "es_fijo": True, "es_solido": False},
    "G": {"tipo": "interior de la ghost house", "color": None, "score":0, "es_fijo": True, "es_solido": False},
    "-": {"tipo": "puerta de la ghost house", "color": None, "score":0, "es_fijo": True, "es_solido": True},
    "P": {"tipo": "posicion inicial del pacman", "color": None, "score":0, "es_fijo": True, "es_solido": False},
    "T": {"tipo": "tunel lateral", "color": None, "score":0, "es_fijo": True, "es_solido": False},
}

