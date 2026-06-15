import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pygame as py
import random
from collections import deque
from blinky import *
from pinky import *
from clyde import *
from inky import *
from patan import Patan
from negui import Negui
from mapa import *
from pacman import pacman
from fantasmas import *
from render import *
from nivel import verificar_nivel_completo, subir_nivel


#inicializamos tanto el motor gráfico como de sonido
py.init()
py.mixer.init()

tamaño_celda = 20
fuente_popup  = py.font.SysFont(None, 26)

#usamos un diccionario para almacenar información relevante de las tiles para cuando sean intterpretadas
config_tiles = {
    "X": {"tipo": "pared",          "color": (0,0,255),     "score": 0,  "es_fijo": True,  "es_solido": True},
    ".": {"tipo": "punto",          "color": (255,255,255), "score": 10, "es_fijo": False, "es_solido": False},
    "o": {"tipo": "punto de poder", "color": (255,255,255), "score": 50, "es_fijo": False, "es_solido": False},
    " ": {"tipo": "pasillo vacio",  "color": (0,0,0),       "score": 0,  "es_fijo": True,  "es_solido": False},
    "G": {"tipo": "ghost house",    "color": None,          "score": 0,  "es_fijo": True,  "es_solido": False},
    "-": {"tipo": "puerta",         "color": None,          "score": 0,  "es_fijo": True,  "es_solido": True},
    "P": {"tipo": "pos pac",        "color": None,          "score": 0,  "es_fijo": True,  "es_solido": False},
    "T": {"tipo": "tunel",          "color": None,          "score": 0,  "es_fijo": True,  "es_solido": False},
}



mapa = Mapa(config_tiles)

#definimos constantes a utilizar
ui_altura     = 40
ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana  = (mapa.filas * tamaño_celda) + ui_altura
screen        = py.display.set_mode((ancho_ventana, alto_ventana))
renderer      = Renderer(screen, tamaño_celda)
score_manager = ScoreManager()
pos_pac, pos_bli, pos_pin, pos_ink, pos_cly, pos_patan, pos_negui = mapa.obtener_posiciones_iniciales()

#velocidades (consigna: 100% = 7.5 tiles/segundo)
BASE              = 7.5
PASO_PAC_NORMAL   = 1.0 / (BASE * 0.80)
PASO_PAC_POWER    = 1.0 / (BASE * 0.90)
PASO_F_NORMAL     = 1.0 / (BASE * 0.75)
PASO_F_TUNEL      = 1.0 / (BASE * 0.40)
PASO_F_ASUSTADO   = 1.0 / (BASE * 0.50)
VEL_OJOS          = BASE * 1.50


#inicializamos a los personajes
pacman = pacman(pos_pac)
blinky = Blinky(direccion=(1, 0),  posicion=pos_bli,   modo="scatter", vida=1)
pinky  = Pinky (direccion=(0, -1), posicion=pos_pin,   modo="scatter", vida=1)
inky   = Inky  (direccion=(1, 0),  posicion=pos_ink,   modo="scatter", vida=1)
clyde  = Clyde (direccion=(-1, 0), posicion=pos_cly,   modo="scatter", vida=1)
patan  = Patan (direccion=(0, 1),  posicion=pos_patan, modo="scatter", vida=1)
negui  = Negui (direccion=(0, -1), posicion=pos_negui, modo="scatter", vida=1)

mapeo_instancias = {
    "Blinky": blinky, "Pinky": pinky, "Inky": inky,
    "Clyde": clyde,   "Patan": patan, "Negui": negui
}

fantasmas           = []
fantasmas_en_espera = []

def paso_pacman() -> float:
    return PASO_PAC_POWER if modo_asustado else PASO_PAC_NORMAL


def paso_fantasma(f: any) -> float:
    """
    Determina la velocidad actual de un fantasma
    
    Args:
        f (Any): La instancia del fantasma a evaluar
        
    Returns:
        float: El tiempo necesario para dar un paso según el modo del fantasma y su posición en el mapa
    """
    if f.modo == "asustado":
        return PASO_F_ASUSTADO
    col, fila = f.posicion
    col_real = col % mapa.columnas
    if 0 <= fila < mapa.filas and mapa.grilla[fila, col_real] == "T":
        return PASO_F_TUNEL
    return PASO_F_NORMAL



#definimos los cíclos que nos daba el enunciado (scatter/chase)
ciclo_modos = [
    ("scatter",  7),
    ("chase",   20),
    ("scatter",  7),
    ("chase",   20),
    ("scatter",  5),
    ("chase",   20),
    ("scatter",  5),
    ("chase",  None)
]

fase_modo   = 0
tiempo_modo = 0.0
modo_global = ciclo_modos[0][0]


#salida sector de los fantasmas
UMBRALES_SALIDA_BASE = [30, 60, 90]


#configuracion de seleccion
esquinas_nombres = ["Arriba-Izquierda", "Arriba-Derecha", "Abajo-Izquierda", "Abajo-Derecha"]

esquinas_scatter_coords = {
    "Arriba-Izquierda": (1, 1),
    "Arriba-Derecha":   (mapa.columnas - 2, 1),
    "Abajo-Izquierda":  (1, mapa.filas - 2),
    "Abajo-Derecha":    (mapa.columnas - 2, mapa.filas - 2)
}

esquina_actual          = 0
fantasmas_seleccionados = {}

fantasmas_info_UI = {
    "Blinky": {"color": (222, 0, 0),     "rect": py.Rect(60,  150, 200, 60)},
    "Pinky":  {"color": (255, 184, 222), "rect": py.Rect(300, 150, 200, 60)},
    "Inky":   {"color": (0, 222, 222),   "rect": py.Rect(60,  250, 200, 60)},
    "Clyde":  {"color": (222, 138, 0),   "rect": py.Rect(300, 250, 200, 60)},
    "Patan":  {"color": (0, 200, 0),     "rect": py.Rect(60,  350, 200, 60)},
    "Negui":  {"color": (170, 70, 220),  "rect": py.Rect(300, 350, 200, 60)}
}

todos_seleccionados = []
umbrales_salida     = []


# funciones auxiliares
def es_solido_para_fantasma(fila: int, col: int) -> bool:
    """
    Verifica si una celda es sólida para un fantasma pero pueden atravesar las puertas de la Ghost House
    
    Args:
        fila (int): Coordenada Y en la grilla
        col (int): Coordenada X en la grilla
        
    Returns:
        bool: True si la celda es un obstáculo para el fantasma, False en caso contrario
    """
    col %= mapa.columnas
    if fila < 0 or fila >= mapa.filas:
        return True
    if mapa.grilla[fila, col] == "-":
        return False
    return mapa.es_solido(fila, col)


def encontrar_camino(inicio: tuple, destino: tuple) -> list :
    """
    Busqueda para encontrar el camino más corto desde un punto de inicio hasta un destino en la grilla.
    
    Args:
        inicio (tuple): Coordenada (col, fila) de partida
        destino (tuple): Coordenada (col, fila) objetivo
        
    Returns:
        List(tuple): Lista de coordenadas que forman el camino hacia el destino
    """
    if inicio == destino:
        return [inicio]
    cola   = deque([inicio])
    padres = {inicio: None}
    while cola:
        actual    = cola.popleft()
        col, fila = actual
        if actual == destino:
            camino = []
            nodo   = destino
            while nodo is not None:
                camino.append(nodo)
                nodo = padres[nodo]
            camino.reverse()
            return camino
        for dc, df in [(1,0),(-1,0),(0,1),(0,-1)]:
            vecino = ((col+dc) % mapa.columnas, fila+df)
            if vecino not in padres and not es_solido_para_fantasma(fila+df, vecino[0]):
                padres[vecino] = actual
                cola.append(vecino)
    return [inicio, destino]


def elegir_mejor_direccion(fantasma: any, target_x: int, target_y: int) -> tuple:
    """
    Calcula la mejor dirección ortogonal para acercarse a un objetivo minimizando 
    la distancia euclidiana que decia el enunciado
    
    Args:
        fantasma (Any): La instancia del fantasma que se mueve
        target_x (int): Coordenada X del objetivo
        target_y (int): Coordenada Y del objetivo
        
    Returns:
        tuple|none: La tupla (dx, dy) óptima, o None
    """
    opuesta    = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir  = None
    menor_dist = float("inf")
    for dir in [(1,0),(-1,0),(0,1),(0,-1)]:
        if dir == opuesta: continue
        nc = (fantasma.posicion[0] + dir[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + dir[1]
        if es_solido_para_fantasma(nf, nc): continue
        dist = (nc-target_x)**2 + (nf-target_y)**2
        if dist < menor_dist:
            menor_dist = dist; mejor_dir = dir
    if mejor_dir is None:
        nc = (fantasma.posicion[0] + opuesta[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + opuesta[1]
        if not es_solido_para_fantasma(nf, nc):
            mejor_dir = opuesta
    return mejor_dir


def elegir_direccion_huyendo(fantasma: any, pac_x: int, pac_y: int) -> tuple:
    """
    Calcula la dirección ortogonal para alejarse de Pac-Man maximizando
    la distancia euclidiana, usado cuando los fantasmas están asustados
    
    Args:
        fantasma (Any): La instancia del fantasma que huye
        pac_x (int): Coordenada X de Pac-Man
        pac_y (int): Coordenada Y de Pac-Man
        
    Returns:
        Optional(tuple): La tupla directriz (dx, dy) óptima para huir
    """
    opuesta    = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir  = None
    mayor_dist = -1
    for dir in [(1,0),(-1,0),(0,1),(0,-1)]:
        if dir == opuesta: continue
        nc = (fantasma.posicion[0] + dir[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + dir[1]
        if es_solido_para_fantasma(nf, nc): continue
        dist = (nc-pac_x)**2 + (nf-pac_y)**2
        if dist > mayor_dist:
            mayor_dist = dist; mejor_dir = dir
    if mejor_dir is None:
        nc = (fantasma.posicion[0] + opuesta[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + opuesta[1]
        if not es_solido_para_fantasma(nf, nc):
            mejor_dir = opuesta
    return mejor_dir


def elegir_target_fantasma(f: any) -> tuple:
    """
    Delega la obtención de la celda objetivo del fantasma según su comportamiento 
    característico y el estado actual del juego
    
    Args:
        f (Any): El fantasma para el cual se busca objetivo
        
    Returns:
        tuple: Coordenadas (X, Y) hacia donde el fantasma intentará ir
    """
    if f.modo == "scatter":
        return f.esquina_scatter
    if f.nombre == "Inky":
        blinky_ref = next((g for g in fantasmas if g.nombre == "Blinky"), None)
        return f.elegir_target(pacman, blinky_ref) if blinky_ref else pacman.posicion
    return f.elegir_target(pacman)


def verificar_colision(pacman, fantasma):
    return pacman.posicion == fantasma.posicion


def resolver_colision(f: any) -> bool:
    """
    Maneja las colisiones entre pacman y fantasmas, modifica el puntaje, 
    genera popups de estado visual o resta vidas
    
    Args:
        f (Any): El fantasma involucrado en la colisión
        
    Returns:
        bool: True si la colisión resultó en la muerte de Pac-Man, False si el fantasma fue devorado
    """
    global estado, timer_muerte, es_ultima_vida, contador_fantasmas_comidos

    if f.modo == "asustado":
        puntos = 200 * (2 ** contador_fantasmas_comidos)
        score_manager.sumar_puntaje(puntos)
        popups.append({"pos": f.posicion, "timer": 0.0, "texto": str(puntos)})
        camino        = encontrar_camino(f.posicion, f.posicion_inicial)
        f.oculto      = True
        f.apareciendo = False
        f.reiniciar_posicion()
        f.cambiar_modo("scatter")
        viajes.append({"camino": camino, "timer": 0.0,
                       "velocidad": VEL_OJOS, "fantasma": f})
        contador_fantasmas_comidos += 1
        return False
    else:
        sonido_sirena_loop.stop()
        sonido_power_pallet.stop()
        sonido_muerte.play()
        score_manager.restar_vidas()
        es_ultima_vida         = score_manager.vidas <= 0
        estado                 = "muriendo"
        timer_muerte           = 0.0
        pacman.muriendo        = True
        pacman.progreso_muerte = 0.0
        return True


def activar_ghost_house() -> None:
    """
    Revisa si se cumplen las condiciones de puntaje para liberar fantasmas
    que se encuentren en espera en la ghost house
    """
    while fantasmas_en_espera and umbrales_salida and \
          score_manager.puntaje >= umbrales_salida[0]:
        nuevo = fantasmas_en_espera.pop(0)
        umbrales_salida.pop(0)
        nuevo.oculto      = False
        nuevo.apareciendo = False
        nuevo.acumulador  = 0.0
        nuevo.cambiar_modo(modo_global)
        fantasmas.append(nuevo)


def respawn_jugador() -> None:
    """
    Devuelve a Pac-Man y a los fantasmas a sus posiciones iniciales despues
    de que el jugador pierda una vida, reiniciando estados temporales
    """
    
    global modo_asustado, contador_tiempo_asustado, contador_fantasmas_comidos

    viajes.clear()
    popups.clear()

    pacman.posicion   = pos_pac
    pacman.direccion  = (1, 0)
    pacman.acumulador = 0.0

    for f in todos_seleccionados:
        f.reiniciar()
        if f in fantasmas:
            f.cambiar_modo(modo_global)

    modo_asustado              = False
    contador_tiempo_asustado   = 0
    contador_fantasmas_comidos = 0


def resetear_nivel() -> None:
    """
    Reinicia la distribución del nivel, posiciones, listas de fantasmas 
    y fases de comportamiento
    """
    global modo_asustado, contador_tiempo_asustado, contador_fantasmas_comidos
    global fase_modo, tiempo_modo, modo_global
    global fantasmas_en_espera, umbrales_salida

    viajes.clear()
    popups.clear()
    modo_asustado              = False
    contador_tiempo_asustado   = 0
    contador_fantasmas_comidos = 0
    fase_modo   = 0
    tiempo_modo = 0.0
    modo_global = ciclo_modos[0][0]

    fantasmas.clear()
    fantasmas_en_espera.clear()
    umbrales_salida.clear()
    fantasmas.extend(todos_seleccionados)

    pos = mapa.obtener_posiciones_iniciales()
    pacman.posicion   = pos[0]
    pacman.direccion  = (1, 0)
    pacman.acumulador = 0.0

    for f in todos_seleccionados:
        f.reiniciar()
        f.cambiar_modo(modo_global)


# variables de juego

modo_asustado              = False
contador_tiempo_asustado   = 0.0
duracion_modo_asustado     = 6.0
contador_fantasmas_comidos = 0

popups             = []
viajes             = []
duracion_aparicion = 0.5
vida_extra_otorgada = False

reloj = py.time.Clock()

estado           = "inicio"
timer_muerte     = 0.0
duracion_muerte  = 1.5
timer_cortina    = 0.0
duracion_cortina = 1.2
es_ultima_vida   = False

corriendo = True
sonido_inicio.play()


# loop principal

while corriendo:

    dt = reloj.tick(60) / 1000.0

    for evento in py.event.get():
        if evento.type == py.QUIT:
            corriendo = False

        elif evento.type == py.KEYDOWN:
            if estado == "inicio" and evento.key == py.K_RETURN:
                estado = "seleccion"
            elif estado == "jugando":
                if evento.key == py.K_UP:    pacman.cambiar_direccion((0,-1))
                elif evento.key == py.K_DOWN:  pacman.cambiar_direccion((0, 1))
                elif evento.key == py.K_LEFT:  pacman.cambiar_direccion((-1,0))
                elif evento.key == py.K_RIGHT: pacman.cambiar_direccion((1, 0))

        elif evento.type == py.MOUSEBUTTONDOWN and estado == "seleccion" and evento.button == 1:
            pos_mouse = py.mouse.get_pos()
            for nombre, info in fantasmas_info_UI.items():
                if (info["rect"].collidepoint(pos_mouse)
                        and nombre not in fantasmas_seleccionados
                        and esquina_actual < 4):
                    fantasmas_seleccionados[nombre] = esquinas_nombres[esquina_actual]
                    esquina_actual += 1
                    if esquina_actual == 4:
                        todos_seleccionados.clear()
                        for nom, nombre_esquina in fantasmas_seleccionados.items():
                            f = mapeo_instancias[nom]
                            f.esquina_scatter = esquinas_scatter_coords[nombre_esquina]
                            todos_seleccionados.append(f)
                        fantasmas.clear()
                        fantasmas.append(todos_seleccionados[0])
                        todos_seleccionados[0].cambiar_modo(modo_global)
                        fantasmas_en_espera.clear()
                        fantasmas_en_espera.extend(todos_seleccionados[1:])
                        umbrales_salida.clear()
                        umbrales_salida.extend(UMBRALES_SALIDA_BASE[:len(fantasmas_en_espera)])
                        estado = "jugando"
                        sonido_sirena_loop.play(-1)
                    break

    if estado == "inicio":
        renderer.dibujar_pantalla_inicio()
        renderer.actualizar_pantalla()
        continue

    if estado == "seleccion":
        renderer.dibujar_pantalla_seleccion(
            esquinas_nombres, esquina_actual, fantasmas_info_UI, fantasmas_seleccionados)
        renderer.actualizar_pantalla()
        continue

    renderer.limpiar_pantalla()
    if estado != "game_over":
        renderer.dibujar_mapa(mapa.grilla)

    if estado == "jugando":

        if not modo_asustado:
            duracion_actual = ciclo_modos[fase_modo][1]
            if duracion_actual is not None:
                tiempo_modo += dt
                if tiempo_modo >= duracion_actual:
                    fase_modo   = min(fase_modo + 1, len(ciclo_modos) - 1)
                    tiempo_modo = 0.0
                    modo_global = ciclo_modos[fase_modo][0]
                    for f in fantasmas:
                        if not f.oculto and not f.apareciendo:
                            f.invertir_direccion()
                            f.cambiar_modo(modo_global)

        if modo_asustado:
            contador_tiempo_asustado += dt
            if contador_tiempo_asustado >= duracion_modo_asustado:
                modo_asustado              = False
                contador_tiempo_asustado   = 0.0
                contador_fantasmas_comidos = 0
                sonido_power_pallet.stop()
                sonido_sirena_loop.play(-1)
                for f in fantasmas:
                    if not f.oculto:
                        f.invertir_direccion()
                        f.cambiar_modo(modo_global)

        activar_ghost_house()

        pacman.acumulador += dt
        paso_pac = paso_pacman()

        if pacman.acumulador >= paso_pac:
            pacman.acumulador -= paso_pac

            prox_col  = (pacman.posicion[0] + pacman.proxima_direccion[0]) % mapa.columnas
            prox_fila =  pacman.posicion[1] + pacman.proxima_direccion[1]
            if not mapa.es_solido(prox_fila, prox_col):
                pacman.direccion = pacman.proxima_direccion

            nueva_col  = (pacman.posicion[0] + pacman.direccion[0]) % mapa.columnas
            nueva_fila =  pacman.posicion[1] + pacman.direccion[1]

            if not mapa.es_solido(nueva_fila, nueva_col):
                pacman.movimiento(mapa.columnas)
                pacman.se_movio = True

                col_a, fila_a = pacman.posicion
                tile = mapa.grilla[fila_a, col_a]

                if tile == ".":
                    score_manager.sumar_puntaje(mapa.tiles["."]["score"])
                    mapa.actualizar_celda(fila_a, col_a, " ")
                    if not modo_asustado:
                        sonido_comer.play()

                elif tile == "o":
                    score_manager.sumar_puntaje(mapa.tiles["o"]["score"])
                    mapa.actualizar_celda(fila_a, col_a, " ")
                    if not modo_asustado:
                        sonido_sirena_loop.stop()
                        sonido_power_pallet.play(-1)
                    modo_asustado              = True
                    contador_tiempo_asustado   = 0.0
                    contador_fantasmas_comidos = 0
                    for f in fantasmas:
                        if not f.oculto:
                            f.invertir_direccion()
                            f.cambiar_modo("asustado")
            else:
                pacman.se_movio = False

            colision_resuelta = False
            for f in fantasmas:
                if f.oculto or f.apareciendo: continue
                if verificar_colision(pacman, f):
                    colision_resuelta = resolver_colision(f)
                    break

            if not vida_extra_otorgada and score_manager.puntaje >= 10000:
                score_manager.vidas += 1
                sonido_vida_extra.play()
                vida_extra_otorgada = True
                popups.append({"pos": pacman.posicion, "timer": 0.0, "texto": "1UP!"})

            if not colision_resuelta and verificar_nivel_completo(mapa):
                py.mixer.stop()
                subir_nivel(score_manager, mapa, 0)
                resetear_nivel()
                sonido_sirena_loop.play(-1)

        colision_resuelta = False
        for f in fantasmas:
            if f.oculto or f.apareciendo: continue
            f.acumulador += dt
            paso_f = paso_fantasma(f)
            if f.acumulador >= paso_f:
                f.acumulador -= paso_f
                if f.modo == "asustado":
                    pac_x, pac_y = pacman.posicion
                    mejor = elegir_direccion_huyendo(f, pac_x, pac_y)
                else:
                    tx, ty = elegir_target_fantasma(f)
                    mejor  = elegir_mejor_direccion(f, tx, ty)
                if mejor:
                    f.cambiar_direccion(mejor)
                nc = (f.posicion[0] + f.direccion[0]) % mapa.columnas
                nf =  f.posicion[1] + f.direccion[1]
                if not es_solido_para_fantasma(nf, nc):
                    f.movimiento(mapa.columnas)
                if verificar_colision(pacman, f):
                    colision_resuelta = resolver_colision(f)
                    if colision_resuelta:
                        break

        if modo_asustado:
            tr = duracion_modo_asustado - contador_tiempo_asustado
            for f in fantasmas:
                f.parpadeando = (f.modo == "asustado" and not f.oculto and tr <= 2.0)
        else:
            for f in fantasmas:
                f.parpadeando = False

        for f in fantasmas:
            if f.apareciendo:
                f.progreso_aparicion += dt / duracion_aparicion
                if f.progreso_aparicion >= 1.0:
                    f.progreso_aparicion = 1.0
                    f.apareciendo        = False

        renderer.dibujar_pacman(pacman)
        renderer.dibujar_fantasmas(fantasmas)
        renderer.dibujar_hud(score_manager.puntaje, score_manager.high_score,
                             score_manager.vidas, score_manager.nivel)

        for popup in popups[:]:
            popup["timer"] += dt
            if popup["timer"] >= 1.0:
                popups.remove(popup); continue
            progreso = popup["timer"]
            col, fila = popup["pos"]
            px   = col  * tamaño_celda + tamaño_celda // 2
            py_p = fila * tamaño_celda - int(30 * progreso)
            alpha = 255 if progreso < 0.7 else int(255 * (1-(progreso-0.7)/0.3))
            surf  = fuente_popup.render(popup["texto"], True, (255,255,100))
            surf.set_alpha(alpha)
            screen.blit(surf, (px - surf.get_width()//2, py_p))

        for viaje in viajes[:]:
            viaje["timer"] += dt
            camino = viaje["camino"]
            n_segs = len(camino) - 1
            if n_segs <= 0 or viaje["timer"] >= n_segs / viaje["velocidad"]:
                fv = viaje["fantasma"]
                fv.oculto             = False
                fv.apareciendo        = True
                fv.progreso_aparicion = 0.0
                viajes.remove(viaje)
                continue
            progreso  = viaje["timer"] / (n_segs / viaje["velocidad"])
            pos_float = progreso * n_segs
            idx       = min(int(pos_float), n_segs - 1)
            frac      = pos_float - idx
            col_a, fila_a = camino[idx]
            col_b, fila_b = camino[idx + 1]
            px_v = int((col_a+(col_b-col_a)*frac)*tamaño_celda + tamaño_celda//2)
            py_v = int((fila_a+(fila_b-fila_a)*frac)*tamaño_celda + tamaño_celda//2)
            py.draw.circle(screen, (180,180,255), (px_v,py_v), 5)
            py.draw.circle(screen, (255,255,255), (px_v,py_v), 3)

    elif estado == "muriendo":
        timer_muerte           += dt
        pacman.progreso_muerte  = min(timer_muerte / duracion_muerte, 1.0)
        if timer_muerte >= duracion_muerte:
            pacman.muriendo        = False
            pacman.progreso_muerte = 0.0
            if es_ultima_vida:
                estado        = "cortina"
                timer_cortina = 0.0
            else:
                respawn_jugador()
                estado = "jugando"
                sonido_sirena_loop.play(-1)
        renderer.dibujar_pacman(pacman)
        renderer.dibujar_hud(score_manager.puntaje, score_manager.high_score,
                             score_manager.vidas, score_manager.nivel)

    elif estado == "cortina":
        timer_cortina += dt
        progreso       = min(timer_cortina / duracion_cortina, 1.0)
        py.draw.rect(screen, (0,0,0), (0, 0, ancho_ventana, int(alto_ventana*progreso)))
        if timer_cortina >= duracion_cortina:
            estado       = "game_over"
            timer_muerte = 0.0

    elif estado == "game_over":
        timer_muerte += dt
        alpha = int(255 * min(timer_muerte / 2.0, 1.0))
        renderer.dibujar_game_over(score_manager.puntaje, alpha)
        if timer_muerte >= 5.0:
            corriendo = False

    renderer.actualizar_pantalla()

py.mixer.stop()
py.quit()