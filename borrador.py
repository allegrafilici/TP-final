import numpy as np
import pygame as py
from blinky import Blinky #traemos a blinky desde el archivo blinky
from pinky import Pinky
from clyde import Clyde
from inky import Inky


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

mapa = Mapa(tiles)
#hace flata definír los colores RGB a cada uno y así los imprimios rápido en la pantalla

tamaño_celda = 20 #tamaño de la casilla del mapa son 20 pixeles

blinky = Blinky((1, 0), (10, 14), "chase", 1)
pinky = Pinky((1, 0), (11, 14), "chase", 1)
clyde = Clyde((1, 0), (12, 14), "chase", 1)
inky = Inky((1, 0), (13, 14), "chase", 1)
fantasmas = [blinky, pinky, clyde, inky] #armamos una lista de fantasmas y en el loop podes recorrer todos
#loop principal
# loop principal
juego = True

juego = True
contador = 0

while juego == True:

    for event in py.event.get():
        if event.type == py.QUIT:
            juego = False

    screen.fill((0, 0, 0))

    for fila in range(mapa.filas): # for loop que va fila por fila 
        for columna in range(mapa.columnas): # por cada fila va columna por columna
            tile = mapa.grilla[fila, columna] # toma lo que haya en esta grilla, hay X, . , o
            x = columna * tamaño_celda # convertir esa posicion en pixeles 
            y = fila * tamaño_celda # le dice a pygame de donde dibujar en la pantalla
            
            if tile == "X": # si la casilla es una pared entonces dubujar un rectangulo azul
                py.draw.rect(
                screen,
                (0, 0, 255),
                (x, y, tamaño_celda, tamaño_celda)
            )
            
            elif tile == ".": # si la casilla es in punto enocnces va un circulo blanco chiquito
                py.draw.circle(
                screen,
                (255, 255, 255),
                (x + tamaño_celda // 2, y + tamaño_celda // 2),
                3
            )
            
            elif tile == "o": # si la casilla es power pallet dibujamos un circulo blanco mas grande
                py.draw.circle(
                screen,
                (255, 255, 255),
                (x + tamaño_celda // 2, y + tamaño_celda // 2),
                7 # para que el ciruclo quede en el cnetro y no la esquina
            )

    contador += 1

    for fantasma in fantasmas:

        columna, fila = fantasma.posicion

        nueva_columna = columna + fantasma.direccion[0]
        nueva_fila = fila + fantasma.direccion[1]

        # mover solo cada 15 frames
        if contador % 15 == 0:

            # si la proxima casilla NO es una pared
            if not mapa.es_solido(nueva_fila, nueva_columna):
                fantasma.movimiento()

            # si es una pared, rebota y cambia de direccion
            else:
                fantasma.cambiar_direccion(
                    (-fantasma.direccion[0], -fantasma.direccion[1])
                )

        x = columna * tamaño_celda
        y = fila * tamaño_celda

        py.draw.circle(
            screen,
            fantasma.color,
            (x + tamaño_celda // 2, y + tamaño_celda // 2),
            tamaño_celda // 2
        )

    py.display.flip()
    reloj.tick(60)