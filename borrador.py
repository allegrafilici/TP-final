import numpy as np
import pygame as py
class Mapa:
    def __init__(self, tiles):
        self.tiles = tiles
        self.grilla = self.iniciar_mapa()
        self.filas, self.columnas = self.grilla.shape
    
    def iniciar_mapa(self):
        mapa = open("assets/mapa.txt", "r").read()
        """
        preguntarle a Mati por:
        with open("assets/mapa.txt", "r") as archivo:
            contenido = archivo.read()
        """
        lineas_mapa = mapa.split("\n")
        mapa_nuevo = []
        for linea in lineas_mapa:
            caracteres_de_fila = []
            for caracter in linea:
                caracteres_de_fila.append(caracter)
            mapa_nuevo.append(caracteres_de_fila)
        array_mapa = np.array(mapa_nuevo)
        return array_mapa
    
    def es_solido(self, fila, col):
        caracter = self.grilla[fila, col]
        return self.tiles[caracter]["es_solido"]
    
    def actualizar_celda(self, fila, col, nuevo_tile):
        self.grilla[fila, col] = nuevo_tile

class ScoreManager:
    def __init__(self):
        self.puntaje = 0 
        self.high_score = 0 
        self.vidas = 3 
        self.nivel = 1
    
    def sumar_puntaje(self, cantidad):
        self.puntaje += cantidad #cantidad como variable provisoria
        
    def restar_vidas(self):
        self.vidas -= 1

    #el siguiente método solo puede llamarse 1 vez por partida
    def sumar_vidas(self):
        self.vidas += 1

py.init()
#configuración de la ventana de pygame
screen = py.display.set_mode((800, 600))
py.display.set_caption("Pacman")
icon = py.image.load("assets/logo.png")  #<a href="https://www.flaticon.com/free-icons/pacman" title="pacman icons">Pacman icons created by iconfield - Flaticon</a>
#lo de arriba son unos crédicos que la pagína queria que pongamos por usar el logo
py.display.set_icon(icon)

reloj = py.time.Clock() #preguntarle a Mati por esta linea


#etiquetamiento de las tiles
tiles = {
    "X": {"tipo": "pared", "color": None, "score":0, "es_fijo": True, "es_solido": True},
    ".":{"tipo": "punto", "color": None, "score":10, "es_fijo": False, "es_solido": False},
    "o":{"tipo": "punto de poder", "color": None, "score":50, "es_fijo": False, "es_solido": False},
    " ":{"tipo":"pasillo vacio", "color": None, "score":0, "es_fijo": True, "es_solido": False},
    "G":{"tipo":"interior de la ghost house", "color": None, "score":0, "es_fijo": True, "es_solido": False},
    "-":{"tipo":"puerta de la ghost house", "color": None, "score":0, "es_fijo": True, "es_solido": True},
    "P":{"tipo": "posicion inicial del pacman", "color": None, "score":0, "es_fijo": True, "es_solido": False},
    "T":{"tipo":"tunel lateral", "color": None, "score":0, "es_fijo": True, "es_solido": False},
}
#hace flata definír los colores RGB a cada uno y así los imprimios rápido en la pantalla

#loop principal
juego = True
while juego == True:
    for event in py.event.get():
        if event.type == py.QUIT:
            juego = False
    
    py.display.flip()
    reloj.tick(60)
    