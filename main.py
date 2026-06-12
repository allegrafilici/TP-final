import numpy as np
import pygame as py
from blinky import *
from pinky import *
from clyde import *
from inky import *
from mapa import *
from pacman import *
from fantasmas import *
from Ui import *


#inicialización
py.init()
tamaño_celda = 20

ui = uimanager()


#creamos un diccionario para la configuración inicial del mapa con toda la información necesaria
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

mapa = Mapa(config_tiles)
ui_altura = 40  
ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana = (mapa.filas * tamaño_celda) + ui_altura

screen = py.display.set_mode((ancho_ventana, alto_ventana))

score_manager = ScoreManager()
py.font.init()
fuente_score = py.font.SysFont("Arial", 24, bold=True)

pos_pac, pos_bli, pos_pin, pos_ink, pos_cly = mapa.obtener_posiciones_iniciales()


#iniclizamos el pacman
pacman = pacman(pos_pac)

#inicializamos los fantasmas
blinky = Blinky(direccion=(1, 0), posicion=pos_bli, modo="scatter", vida=1)
pinky = Pinky(direccion=(0, -1), posicion=pos_pin, modo="scatter", vida=1)
inky = Inky(direccion=(1, 0), posicion=pos_ink, modo="scatter", vida=1)
clyde = Clyde(direccion=(-1, 0), posicion=pos_cly, modo="scatter", vida=1)

fantasmas = [blinky, pinky, inky, clyde]



#defino el tiempo  
reloj = py.time.Clock()
tiempo_acumulado = 0.0
tiempo_por_paso = 0.15 #regulador del tiempo

corriendo = True

while corriendo:
    dt = reloj.tick(60) / 1000.0 #calulo para obtener segundos
    
    for evento in py.event.get():
        if evento.type == py.QUIT:
            corriendo = False
        # Captura de teclado
        elif evento.type == py.KEYDOWN:
            if evento.key == py.K_UP: pacman.cambiar_direccion((0, -1))
            elif evento.key == py.K_DOWN: pacman.cambiar_direccion((0, 1))
            elif evento.key == py.K_LEFT: pacman.cambiar_direccion((-1, 0))
            elif evento.key == py.K_RIGHT: pacman.cambiar_direccion((1, 0))

    #limpiamos la pantalla
    screen.fill((0, 0, 0))

    #dibujado del mapa
    for fila in range(mapa.filas):
        for columna in range(mapa.columnas):
            tile = mapa.grilla[fila, columna]
            x, y = columna * tamaño_celda, fila * tamaño_celda
            
            if tile in mapa.tiles and mapa.tiles[tile]["color"]:
                color = mapa.tiles[tile]["color"]
                tipo = mapa.tiles[tile]["tipo"]
                
                if tipo == "pared":
                    py.draw.rect(screen, color, (x, y, tamaño_celda, tamaño_celda))
                elif tipo == "punto":
                    py.draw.circle(screen, color, (x + tamaño_celda//2, y + tamaño_celda//2), 3)
                elif tipo == "punto de poder":
                    py.draw.circle(screen, color, (x + tamaño_celda//2, y + tamaño_celda//2), 7)

    #movimiento de personajes
    tiempo_acumulado += dt

    if tiempo_acumulado >= tiempo_por_paso:
        
        #movimiento Pacman
        prox_col = pacman.posicion[0] + pacman.proxima_direccion[0]
        prox_fila = pacman.posicion[1] + pacman.proxima_direccion[1]
        
        if not mapa.es_solido(prox_fila, prox_col): 
            pacman.direccion = pacman.proxima_direccion
        
        nueva_col = pacman.posicion[0] + pacman.direccion[0]
        nueva_fila = pacman.posicion[1] + pacman.direccion[1]
        
        if not mapa.es_solido(nueva_fila, nueva_col): 
            pacman.movimiento()
            
            #comer puntos
            col_actual, fila_actual = pacman.posicion
            tile_actual = mapa.grilla[fila_actual, col_actual]

            if tile_actual == ".":
                score_manager.sumar_puntaje(mapa.tiles["."]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")
            elif tile_actual == "o":
                score_manager.sumar_puntaje(mapa.tiles["o"]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

        #movimiento Fantasmas
        for f in fantasmas:
            f.decidir_direccion(pacman, blinky if f.nombre == "Inky" else None)
            nc = f.posicion[0] + f.direccion[0]
            nf = f.posicion[1] + f.direccion[1]
            
            if not mapa.es_solido(nf, nc): 
                f.movimiento()
            else: 
                f.cambiar_direccion((-f.direccion[0], -f.direccion[1]))
        
        # Reseteamos el acumulador restándole el tiempo que acabamos de consumir
        tiempo_acumulado -= tiempo_por_paso


    #renderizado
    
    #renderizamos el pacman
    x_pac = pacman.posicion[0] * tamaño_celda + 3
    y_pac = pacman.posicion[1] * tamaño_celda + 3
    screen.blit(pacman.imagen, (x_pac, y_pac))
    
    #renderizamos los fantasmas
    for f in fantasmas:
        x_fantasma = f.posicion[0] * tamaño_celda + 3
        y_fantasma = f.posicion[1] * tamaño_celda + 3
        screen.blit(f.imagen, (x_fantasma, y_fantasma))

    y_pos_ui = mapa.filas * tamaño_celda + 10
    texto_puntaje = fuente_score.render(f"SCORE: {score_manager.puntaje}", True, (255, 255, 255))
    screen.blit(texto_puntaje, (20, y_pos_ui))
    
    py.display.flip()

py.quit()

"""
blinky = Blinky((1, 0), (10, 14), "chase", 1)
pinky = Pinky((1, 0), (11, 14), "chase", 1)
clyde = Clyde((1, 0), (12, 14), "chase", 1)
inky = Inky((1, 0), (13, 14), "chase", 1)
fantasmas = [blinky, pinky, clyde, inky] #armamos una lista de fantasmas y en el loop podes recorrer todos
"""