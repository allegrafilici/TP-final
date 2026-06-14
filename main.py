import numpy as np
import pygame as py
import random

from blinky import *
from pinky import *
from clyde import *
from inky import *
from patan import Patan
from negui import Negui
from mapa import *
from pacman import pacman
from fantasmas import *
from render import Renderer


# inicialización
py.init()
tamaño_celda = 20

config_tiles = {
    "X": {"tipo": "pared", "color": (0, 0, 255), "score": 0, "es_fijo": True, "es_solido": True},
    ".": {"tipo": "punto", "color": (255, 255, 255), "score": 10, "es_fijo": False, "es_solido": False},
    "o": {"tipo": "punto de poder", "color": (255, 255, 255), "score": 50, "es_fijo": False, "es_solido": False},
    " ": {"tipo": "pasillo vacio", "color": (0, 0, 0), "score": 0, "es_fijo": True, "es_solido": False},
    "G": {"tipo": "interior de la ghost house", "color": None, "score": 0, "es_fijo": True, "es_solido": False},
    "-": {"tipo": "puerta de la ghost house", "color": None, "score": 0, "es_fijo": True, "es_solido": True},
    "P": {"tipo": "posicion inicial del pacman", "color": None, "score": 0, "es_fijo": True, "es_solido": False},
    "T": {"tipo": "tunel lateral", "color": None, "score": 0, "es_fijo": True, "es_solido": False},
}

mapa = Mapa(config_tiles)

ui_altura = 40
ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana = (mapa.filas * tamaño_celda) + ui_altura

screen = py.display.set_mode((ancho_ventana, alto_ventana))

renderer = Renderer(screen, tamaño_celda)

score_manager = ScoreManager()

pos_pac, pos_bli, pos_pin, pos_ink, pos_cly, pos_patan, pos_negui = mapa.obtener_posiciones_iniciales()

# inicializamos Pac-Man
pacman = pacman(pos_pac)

# inicializamos fantasmas
blinky = Blinky(direccion=(1, 0), posicion=pos_bli, modo="scatter", vida=1)
pinky = Pinky(direccion=(0, -1), posicion=pos_pin, modo="scatter", vida=1)
inky = Inky(direccion=(1, 0), posicion=pos_ink, modo="scatter", vida=1)
clyde = Clyde(direccion=(-1, 0), posicion=pos_cly, modo="scatter", vida=1)
patan = Patan(direccion=(0, 1), posicion=pos_patan, modo="scatter", vida=1)
negui = Negui(direccion=(0, -1), posicion=pos_negui, modo="scatter", vida=1)

fantasmas = [blinky, pinky, inky, clyde, patan, negui]

# variables del modo asustado
modo_asustado = False
contador_tiempo_asustado = 0
duracion_modo_asustado = 8

# tiempo
reloj = py.time.Clock()
tiempo_acumulado = 0.0
tiempo_por_paso = 0.15

corriendo = True

while corriendo:
    dt = reloj.tick(60) / 1000.0

    for evento in py.event.get():
        if evento.type == py.QUIT:
            corriendo = False

        elif evento.type == py.KEYDOWN:
            if evento.key == py.K_UP:
                pacman.cambiar_direccion((0, -1))
            elif evento.key == py.K_DOWN:
                pacman.cambiar_direccion((0, 1))
            elif evento.key == py.K_LEFT:
                pacman.cambiar_direccion((-1, 0))
            elif evento.key == py.K_RIGHT:
                pacman.cambiar_direccion((1, 0))

    renderer.limpiar_pantalla()
    renderer.dibujar_mapa(mapa.grilla)

    tiempo_acumulado += dt

    if tiempo_acumulado >= tiempo_por_paso:

        # controlar duración del modo asustado
        if modo_asustado:
            contador_tiempo_asustado += tiempo_por_paso

            if contador_tiempo_asustado >= duracion_modo_asustado:
                modo_asustado = False
                contador_tiempo_asustado = 0

                for f in fantasmas:
                    f.cambiar_modo("scatter")

        # movimiento Pac-Man
        prox_col = pacman.posicion[0] + pacman.proxima_direccion[0]
        prox_fila = pacman.posicion[1] + pacman.proxima_direccion[1]

        if not mapa.es_solido(prox_fila, prox_col):
            pacman.direccion = pacman.proxima_direccion

        nueva_col = pacman.posicion[0] + pacman.direccion[0]
        nueva_fila = pacman.posicion[1] + pacman.direccion[1]

        if not mapa.es_solido(nueva_fila, nueva_col):
            pacman.movimiento()

            # comer puntos
            col_actual, fila_actual = pacman.posicion
            tile_actual = mapa.grilla[fila_actual, col_actual]

            if tile_actual == ".":
                score_manager.sumar_puntaje(mapa.tiles["."]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

            elif tile_actual == "o":
                score_manager.sumar_puntaje(mapa.tiles["o"]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

                # activar modo asustado
                modo_asustado = True
                contador_tiempo_asustado = 0

                for f in fantasmas:
                    f.cambiar_modo("asustado")

        # movimiento fantasmas
        for f in fantasmas:

            if f.modo == "asustado":
                direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                random.shuffle(direcciones)

                for direccion in direcciones:
                    nc = f.posicion[0] + direccion[0]
                    nf = f.posicion[1] + direccion[1]

                    if not mapa.es_solido(nf, nc):
                        f.cambiar_direccion(direccion)
                        break

            else:
                f.decidir_direccion(pacman, blinky if f.nombre == "Inky" else None)

            nc = f.posicion[0] + f.direccion[0]
            nf = f.posicion[1] + f.direccion[1]

            if not mapa.es_solido(nf, nc):
                f.movimiento()
            else:
                f.cambiar_direccion((-f.direccion[0], -f.direccion[1]))

        tiempo_acumulado -= tiempo_por_paso

    # render
    renderer.dibujar_pacman(pacman)
    renderer.dibujar_fantasmas(fantasmas)
    renderer.dibujar_hud(score_manager.puntaje, score_manager.high_score, score_manager.vidas, score_manager.nivel)
    renderer.actualizar_pantalla()

py.quit()
