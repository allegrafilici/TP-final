"""
main.py - Va a ser el loop principal del juego Pacman
 
Este archivo es el punto de entrada del programa. Se va a encargar de:
    - Inicializar pygame y todos los modulos necesarios.
    - Crear los objetos del juego (mapa, personajes, render, etc).
    - Definir las funciones auxiliares de movimiento y colision.
    - Ejecutar el loop principal que corre a 60 FPS.
 
El loop principal maneja cuatro estados posibles:
    "inicio"    = pantalla de bienvenida, espera ENTER
    "seleccion" = el jugador elige 4 fantasmas y asigna esquinas
    "jugando"   = partida activa con logica completa
    "muriendo"  = animacion de cuando muere  Pacman
    "cortina"   = transicion/efecto visual al game over
    "game_over" = pantalla final con animacion progresiva del puntaje
"""

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


# Inicializamos tanto el motor grafico como el de sonido de pygame.
# py.init() activa todos los modulos y py.mixer.init() habilita el audio.
py.init()
py.mixer.init()

tamaño_celda = 20
#Esto seria pixel x tile, es decir cada celda/tile del mapa es 20x20px
fuente_popup  = py.font.SysFont(None, 26)
#fuente para los textos de puntaje flotante

# Diccionario de configuracion de tiles.
# Cada caracter del mapa.txt va a tener un tipo, color, puntaje y si es solido o no.
# "es_solido" va a determinar si Pac-Man o los fantasmas pueden atravesar esa celda.
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
"""
Aca creamos el objeto "mapa" pasándole el diccionario "config_tiles" (El de arriba)

Esto va a hacer lo siguiente:
1.Lee el archivo "assets/mapa.txt" que contiene el diseño del laberinto.
2. Valida que el archivo este bien armado (sin caracteres desconocidos).
3. Cruza ese texto con "config_tiles" para entender las reglas (ej: 
la "X" es pared sólida, el "." es un punto, etc).
4. Por ultimo convierte todo en una grilla matematica (array bidimensional de numpy) 
que el motor del juego usa constantemente para calcular las colisiones 
y saber por donde pueden caminar los personajes.
"""


# Calculamos el tamaño de la ventana en base al mapa cargado.
# ui_altura reserva espacio en la parte superior para el HUD (puntaje, vidas, nivel).
ui_altura     = 40
ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana  = (mapa.filas * tamaño_celda) + ui_altura
screen        = py.display.set_mode((ancho_ventana, alto_ventana))
renderer      = Renderer(screen, tamaño_celda)  # Se encarga de dibujar todo
score_manager = ScoreManager() # Es quien maneja puntaje, vidas y nivel

# Obtenemos las posiciones iniciales de cada personaje desde el mapa.
# El mapa calcula estas posiciones en base a donde esta la puerta '-' en el txt.
pos_pac, pos_bli, pos_pin, pos_ink, pos_cly, pos_patan, pos_negui = mapa.obtener_posiciones_iniciales()

"""
Segun la consigna, la velocidad máxima (100%) del juego equivale a 
7.5 casilleros (tiles) por segundo. 

Explicacion del metodo por tiempo acomulado:
En Pacman, el laberinto es una grilla estricta. Los personajes no pueden 
moverse "un cuarto de casillero", porque quedarian desalineados con las 
paredes y romperian las colisiones. Siempre deben moverse de a 1 casillero 
entero por vez.

Por lo tanto, para hacer que un personaje sea "más lento" o "más rápido", no 
cambiamos la distancia que recorre, sino CUANTO TIEMPO ESPERA antes de 
dar el siguiente paso.

Razonamiento de la formula:
1. REGLA BASE: Al 100% de velocidad, se dan 7.5 pasos en 1 segundo real.
2. EJEMPLO CON PACMAN (80%): 
   Si va al 80%, da 6 pasos en 1 segundo (7.5 * 0.80 = 6).
   Si da 6 pasos en 1 segundo... ¿Cuánto tiempo tarda en dar 1 solo paso?
   Formula: 1 segundo / 6 pasos = 0.166 segundos por paso.


¿como se ve en el juego?
En el loop principal (main), contamos los milisegundos reales que van 
pasando (dt). Por ejemplo cuando a Pacman se le acumulan 0.166 segundos de espera, 
el codigo le da permiso para saltar al siguiente casillero. Un fantasma en 
el tunel (40%) necesita acumular 0.333 segundos. Como necesita esperar más 
tiempo para que le den permiso de moverse, lo vemos caminar más lento.
"""
BASE              = 7.5
PASO_PAC_NORMAL   = 1.0 / (BASE * 0.80)
PASO_PAC_POWER    = 1.0 / (BASE * 0.90)
PASO_F_NORMAL     = 1.0 / (BASE * 0.75)
PASO_F_TUNEL      = 1.0 / (BASE * 0.40)
PASO_F_ASUSTADO   = 1.0 / (BASE * 0.50)
VEL_OJOS          = BASE * 1.50


#inicializamos a los personajes
# NOTA: usamos pacman_obj como nombre temporal para no pisar la clase pacman importada.
# Al final lo reasignamos a la variable pacman para que el resto del codigo no cambie.
pacman_obj = pacman(pos_pac)
blinky = Blinky(direccion=(1, 0),  posicion=pos_bli,   modo="scatter", vida=1)
pinky  = Pinky (direccion=(0, -1), posicion=pos_pin,   modo="scatter", vida=1)
inky   = Inky  (direccion=(1, 0),  posicion=pos_ink,   modo="scatter", vida=1)
clyde  = Clyde (direccion=(-1, 0), posicion=pos_cly,   modo="scatter", vida=1)
patan  = Patan (direccion=(0, 1),  posicion=pos_patan, modo="scatter", vida=1)
negui  = Negui (direccion=(0, -1), posicion=pos_negui, modo="scatter", vida=1)
pacman = pacman_obj


# Diccionario que asocia el nombre string de cada fantasma con su objeto en Python.
# Se lo va a usar en la pantalla de seleccion para saber que instancia activar.
mapeo_instancias = {
    "Blinky": blinky, "Pinky": pinky, "Inky": inky,
    "Clyde": clyde,   "Patan": patan, "Negui": negui
}

# fantasmas: lista de los que estan activos en el juego ahora mismo.
# fantasmas_en_espera: lista de los que fueron seleccionados pero todavia no salieron de del refugio
fantasmas           = []
fantasmas_en_espera = []

def paso_pacman() -> float:
    """
    Calcula el tiempo en segundos que Pacman tarda en moverse un tile.
 
    Cuando hay un power pellet activo (modo_asustado == True), Pac-Man
    va mas rapido (90% de velocidad base en vez del 80% normal).
    """
    return PASO_PAC_POWER if modo_asustado else PASO_PAC_NORMAL


def paso_fantasma(f: any) -> float:
    """
    Lo mismo pero con fantasmas:
 
    La velocidad varia segun el estado actual del fantasma y su posicion:
        - Asustado: 50% (huye de Pacman, mas lento)
        - En tunel 'T': 40% (penalizacion del tunel lateral)
        - Normal: 75% (velocidad estandar de persecucion)"""

    if f.modo == "asustado":
        return PASO_F_ASUSTADO
    col, fila = f.posicion
    col_real = col % mapa.columnas
    if 0 <= fila < mapa.filas and mapa.grilla[fila, col_real] == "T":
        return PASO_F_TUNEL
    return PASO_F_NORMAL



#definimos los cíclos que nos daba el enunciado (scatter/chase)
"""
Los fantasmas alternan globalmente entre dos modos de comportamiento:

Scatter: cada fantasma va hacia su esquina asignada del mapa.
           Esto crea patrones predecibles que el jugador puede explotar y aprovechar.

Chase:   cada fantasma activa su algoritmo de persecucion propio
            (Blinky persigue directo, Pinky embosca, Inky flanquea, etc).

Al cambiar de modo, TODOS los fantasmas invierten su direccion inmediatamente.
El ciclo se PAUSA durante el modo asustado y retoma donde quedo al terminar.

Duraciones segun la consigna (nivel 1):
   Scatter 7s = Chase 20s = Scatter 7s = Chase 20s 
   Scatter 5s = Chase 20s = Scatter 5s = Chase inefinido
"""

ciclo_modos = [
    ("scatter",  7),
    ("chase",   20),
    ("scatter",  7),
    ("chase",   20),
    ("scatter",  5),
    ("chase",   20),
    ("scatter",  5),
    ("chase",  None) # None = dura indefinidamente hasta que termine el nivel
]

fase_modo   = 0  # Indice actual en ciclo_modos
tiempo_modo = 0.0  # Segundos acumulados en la fase actual
modo_global = ciclo_modos[0][0] # Modo activo ahora mismo ("scatter" o "chase")


#salida de la base de los fantasmas

"""
El primer fantasma seleccionado sale al inicio de la partida.
 
Los siguientes salen cuando el puntaje acumulado supera estos umbrales(30, 60, 90).
Esto hace que al principio haya un solo enemigo y la dificultad vaya subiendo.
"""
UMBRALES_SALIDA_BASE = [30, 60, 90]


#nombres de las esquinas
esquinas_nombres = ["Arriba-Izquierda", "Arriba-Derecha", "Abajo-Izquierda", "Abajo-Derecha"]


"""
Coordenadas reales (col, fila) de cada esquina del mapa.
Estas son las celdas a las que cada fantasma intentara llegar en modo Scatter.
"""
esquinas_scatter_coords = {
    "Arriba-Izquierda": (1, 1),
    "Arriba-Derecha":   (mapa.columnas - 2, 1),
    "Abajo-Izquierda":  (1, mapa.filas - 2),
    "Abajo-Derecha":    (mapa.columnas - 2, mapa.filas - 2)
}

esquina_actual          = 0
fantasmas_seleccionados = {}

# Rectangulos y colores de las tarjetas clickeables en la pantalla de inicio.
fantasmas_info_UI = {
    "Blinky": {"color": (222, 0, 0),     "rect": py.Rect(60,  150, 200, 60)},
    "Pinky":  {"color": (255, 184, 222), "rect": py.Rect(300, 150, 200, 60)},
    "Inky":   {"color": (0, 222, 222),   "rect": py.Rect(60,  250, 200, 60)},
    "Clyde":  {"color": (222, 138, 0),   "rect": py.Rect(300, 250, 200, 60)},
    "Patan":  {"color": (0, 200, 0),     "rect": py.Rect(60,  350, 200, 60)},
    "Negui":  {"color": (170, 70, 220),  "rect": py.Rect(300, 350, 200, 60)}
}

todos_seleccionados = [] # Los 4 objetos elegidos, en orden de seleccion
umbrales_salida     = [] # Copia mutable de UMBRALES_SALIDA_BASE (se va a ir vaciando)


# funciones auxiliares
def es_solido_para_fantasma(fila: int, col: int) -> bool:
    """
    Verifica si una celda es solida para un fantasma pero pueden atravesar las puertas de la base de los fantsmas
    
    Args:
        fila (int): Coordenada Y en la grilla
        col (int): Coordenada X en la grilla
        
    Returns:
        bool: True si la celda es un obstaculo para el fantasma, False en caso contrario
    """
    col %= mapa.columnas
    if fila < 0 or fila >= mapa.filas:
        return True
    if mapa.grilla[fila, col] == "-":
        return False
    return mapa.es_solido(fila, col)


def encontrar_camino(inicio: tuple, destino: tuple) -> list :
    """
    Busqueda para encontrar el camino mas corto desde un punto de inicio hasta un destino en la grilla.
    
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
    Calcula la mejor direccion para acercarse a un objetivo minimizando 
    la distancia euclidiana que mencionaba el enunciado
    
    Args:
        fantasma (Any): La instancia del fantasma que se mueve
        target_x (int): Coordenada X del objetivo
        target_y (int): Coordenada Y del objetivo
        
    Returns:
        tuple|none: La tupla (dx, dy) optima, o None
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
    Calcula la direccion ortogonal para alejarse de Pacman maximizando
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

        # Regla 1: sin reversa
        nc = (fantasma.posicion[0] + dir[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + dir[1]
        if es_solido_para_fantasma(nf, nc): continue
        # Regla 2: sin paredes
        dist = (nc-pac_x)**2 + (nf-pac_y)**2
        if dist > mayor_dist:
            mayor_dist = dist; mejor_dir = dir
        # Fallback: si quedo atrapado, permite dar la vuelta
    if mejor_dir is None:
        nc = (fantasma.posicion[0] + opuesta[0]) % mapa.columnas
        nf =  fantasma.posicion[1] + opuesta[1]
        if not es_solido_para_fantasma(nf, nc):
            mejor_dir = opuesta
    return mejor_dir


def elegir_target_fantasma(f: any) -> tuple:
    """
    Delega la obtencion de la celda objetivo del fantasma según su comportamiento 
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

    """
    Detecta si Pacman y un fantasma ocupan la misma celda.
 
    La colision se basa en comparar posiciones exactas en la grilla.
    Se llama dos veces por ciclo: antes y despues de que el fantasma
    se mueva, para no perder colisiones en pasos grandes.
 
    Args:
        pacman (Any): El objeto Pacman.
        fantasma (Any): El objeto Fantasma a comparar.
 
    Returns:
        bool: True si estan en la misma celda, False si no.
    """

    return pacman.posicion == fantasma.posicion


def resolver_colision(f: any) -> bool:
    """
   Maneja lo que ocurre cuando Pacman toca a un fantasma.
 
    Hay dos casos posibles:
 
    1. Fantasma ASUSTADO (modo "asustado"):
       Pacman lo come. Se suma puntaje con multiplicador (200, 400, 800, 1600
       segun cuantos fantasmas se comieron en el mismo power pellet).
       El fantasma queda oculto y sus "ojos" viajan de vuelta a la base
       usando BFS. Al llegar, renace con animacion que le pusimos.
 
    2. Fantasma NORMAL (modo "scatter" o "chase"):
       Pacman pierde una vida. Se activa la animacion de muerte y el estado
       pasa a "muriendo". Si no quedan vidas, se va a la animacion de cortina y luego "game_over".
 
    Args:
        f (Any): El fantasma involucrado en la colision.
 
    Returns:
        bool: True si Pacman murio (pierde vida), False si comio al fantasma.
    """
    global estado, timer_muerte, es_ultima_vida, contador_fantasmas_comidos

    if f.modo == "asustado":
        puntos = 200 * (2 ** contador_fantasmas_comidos) # Multiplicador: 200, 400, etc por cada fantasma en el mismo power pellet
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
         # Pacman muere: freno sonidos, resto vida, activo animacion de muerte
        
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
     Libera el siguiente fantasma en espera si el puntaje supero su umbral.
 
    Se llama cada frame (no cada paso) para reaccionar inmediatamente
    cuando el puntaje cruza el umbral. Usa un while por si dos umbrales
    se cruzan en el mismo frame (ej: comer 3 puntos y pasar de 29 a 59).
 
    La lista umbrales_salida se va vaciando a medida que cada fantasma sale.
    El nuevo fantasma hereda el modo global actual (scatter o chase).
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
    Devuelve a Pacman y a los fantasmas a sus posiciones iniciales despues
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

modo_asustado              = False # True mientras hay power pellet activo
contador_tiempo_asustado   = 0.0   # Segundos transcurridos del modo asustado
duracion_modo_asustado     = 6.0   # Duracion total del modo asustado (consigna: 6s)
contador_fantasmas_comidos = 0     # Cuantos fantasmas se comieron en el mismo power pellet

popups             = [] # Lista de popups de puntaje flotantes activos
viajes             = []  # Lista de viajes de ojos en curso hacia la base de los fantasmas
duracion_aparicion = 0.5 # Segundos que dura la animacion de reaparicion del fantasma
vida_extra_otorgada = False # Solo se da una vida extra por partida a 10.000 puntos

reloj = py.time.Clock() # Controla los FPS

estado           = "inicio"  # Estado inicial: pantalla de bienvenida
timer_muerte     = 0.0  # Tiempo acumulado en el estado "muriendo" o "game_over"
duracion_muerte  = 1.5 # Segundos que dura la animacion de muerte
timer_cortina    = 0.0 # Tiempo acumulado en el estado "cortina" es decir la animacion
duracion_cortina = 1.2 # Segundos que tarda la cortina en bajar
es_ultima_vida   = False # True si Pacman murio sin vidas restantes

corriendo = True
sonido_inicio.play()


# loop principal

while corriendo:

    dt = reloj.tick(60) / 1000.0 # Limita a 60 FPS y convierte ms a segundos

    # py.event.get() devuelve todos los eventos ocurridos desde el ultimo frame.
    # Los tres que nos importan: cerrar ventana, teclas y clics del mouse.
    for evento in py.event.get():
        if evento.type == py.QUIT:
            corriendo = False

        elif evento.type == py.KEYDOWN:
            # En "inicio": ENTER avanza a la seleccion de fantasmas.
            # En "jugando": las flechas guardan la proxima direccion deseada.
            # pacman.py la aplica en cuanto el camino este libre (pre-input).
            if estado == "inicio" and evento.key == py.K_RETURN:
                estado = "seleccion"
            elif estado == "jugando":
                if evento.key == py.K_UP:    pacman.cambiar_direccion((0,-1))
                elif evento.key == py.K_DOWN:  pacman.cambiar_direccion((0, 1))
                elif evento.key == py.K_LEFT:  pacman.cambiar_direccion((-1,0))
                elif evento.key == py.K_RIGHT: pacman.cambiar_direccion((1, 0))

        elif evento.type == py.MOUSEBUTTONDOWN and estado == "seleccion" and evento.button == 1:
            # El jugador clickea una tarjeta de fantasma para asignarlo a la esquina actual.
            # Cuando se completan las 4 selecciones, se arma la lista de activos/en espera
            # y el juego pasa al estado "jugando".
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
                        # El primero sale inmediatamente, los otros esperan sus umbrales
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

    # En "inicio" y "seleccion" solo dibujamos la UI y esperamos input.
    # El "continue" salta el resto del loop para no ejecutar logica de juego.
    if estado == "inicio":
        renderer.dibujar_pantalla_inicio()
        renderer.actualizar_pantalla()
        continue

    if estado == "seleccion":
        renderer.dibujar_pantalla_seleccion(
            esquinas_nombres, esquina_actual, fantasmas_info_UI, fantasmas_seleccionados)
        renderer.actualizar_pantalla()
        continue

    # Para el resto de estados, limpiamos la pantalla y dibujamos el mapa como base.
    # En "game_over" no mostramos el mapa porque la pantalla ya fue cubierta por la cortina.
    renderer.limpiar_pantalla()
    if estado != "game_over":
        renderer.dibujar_mapa(mapa.grilla)

    if estado == "jugando":

        # El timer avanza solo cuando NO hay power pellet activo.
        # Cuando el tiempo de la fase actual se agota, pasamos a la siguiente
        # y todos los fantasmas invierten su direccion inmediatamente.
        # Si la duracion es None (ultima fase), el ciclo quedo en chase indefinido.
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

        # Cuenta los 6 segundos que dura el power pellet.
        # Al terminar, los fantasmas vuelven al modo del ciclo donde habia quedado.
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


        # Se llama cada frame para liberar el proximo fantasma en espera
        # en cuanto el puntaje supere su umbral (30, 60 o 90 puntos).
        activar_ghost_house()

        # Cada frame sumamos dt al acumulador de Pacman.
        # Cuando supera su "paso" (tiempo por tile), da un casillero y resetea.
        pacman.acumulador += dt
        paso_pac = paso_pacman()

        if pacman.acumulador >= paso_pac:
            pacman.acumulador -= paso_pac

            # Intenta aplicar la proxima direccion si el camino esta libre
            prox_col  = (pacman.posicion[0] + pacman.proxima_direccion[0]) % mapa.columnas
            prox_fila =  pacman.posicion[1] + pacman.proxima_direccion[1]
            if not mapa.es_solido(prox_fila, prox_col):
                pacman.direccion = pacman.proxima_direccion

            # Se mueve en la direccion actual si no hay pared adelante
            nueva_col  = (pacman.posicion[0] + pacman.direccion[0]) % mapa.columnas
            nueva_fila =  pacman.posicion[1] + pacman.direccion[1]

            if not mapa.es_solido(nueva_fila, nueva_col):
                pacman.movimiento(mapa.columnas)
                pacman.se_movio = True

                # Procesar el tile donde Pacman aterrizó
                col_a, fila_a = pacman.posicion
                tile = mapa.grilla[fila_a, col_a]

                if tile == ".":
                    score_manager.sumar_puntaje(mapa.tiles["."]["score"])  # +10 pts
                    mapa.actualizar_celda(fila_a, col_a, " ")
                    if not modo_asustado:
                        sonido_comer.play()

                elif tile == "o":
                    score_manager.sumar_puntaje(mapa.tiles["o"]["score"])  # +50 pts
                    mapa.actualizar_celda(fila_a, col_a, " ")
                    if not modo_asustado:
                        sonido_sirena_loop.stop()
                        sonido_power_pallet.play(-1)
                    # Activa modo asustado: todos los fantasmas activos se asustan
                    modo_asustado              = True
                    contador_tiempo_asustado   = 0.0
                    contador_fantasmas_comidos = 0
                    for f in fantasmas:
                        if not f.oculto:
                            f.invertir_direccion()
                            f.cambiar_modo("asustado")
            else:
                pacman.se_movio = False  # Hay pared adelante: la boca se cierra (ver pacman.py)

            # Colision temprana: Pacman camino hacia donde estaba un fantasma
            colision_resuelta = False
            for f in fantasmas:
                if f.oculto or f.apareciendo: continue
                if verificar_colision(pacman, f):
                    colision_resuelta = resolver_colision(f)
                    break

            # Vida extra: se otorga una sola vez al llegar a 10.000 puntos
            if not vida_extra_otorgada and score_manager.puntaje >= 10000:
                score_manager.vidas += 1
                sonido_vida_extra.play()
                vida_extra_otorgada = True
                popups.append({"pos": pacman.posicion, "timer": 0.0, "texto": "1UP!"})

            # Verificar si no quedan puntos ni power pellets en el mapa
            if not colision_resuelta and verificar_nivel_completo(mapa):
                py.mixer.stop()
                subir_nivel(score_manager, mapa, 0)
                resetear_nivel()
                sonido_sirena_loop.play(-1)

        # Cada fantasma tiene su propio acumulador y velocidad.
        # El paso depende de su modo (asustado/normal) y si esta en el tunel.
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
                # Colision tardia: el fantasma se movio encima de Pacman
                if verificar_colision(pacman, f):
                    colision_resuelta = resolver_colision(f)
                    if colision_resuelta:
                        break

        # En los ultimos 2 segundos del power pellet los fantasmas parpadean
        # para avisar que el efecto esta por terminar.
        if modo_asustado:
            tr = duracion_modo_asustado - contador_tiempo_asustado
            for f in fantasmas:
                f.parpadeando = (f.modo == "asustado" and not f.oculto and tr <= 2.0)
        else:
            for f in fantasmas:
                f.parpadeando = False

        # Cuando los ojos de un fantasma llegan a la base, el fantasma
        # renace creciendo desde 0 hasta su tamaño normal (ver fantasmas.py).
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

        # Popups de puntaje: textos flotantes que suben y se desvanecen en 1 segundo
        for popup in popups[:]:
            popup["timer"] += dt
            if popup["timer"] >= 1.0:
                popups.remove(popup); continue
            progreso = popup["timer"]
            col, fila = popup["pos"]
            px   = col  * tamaño_celda + tamaño_celda // 2
            py_p = fila * tamaño_celda - int(30 * progreso)  # Sube 30px en 1 segundo
            alpha = 255 if progreso < 0.7 else int(255 * (1-(progreso-0.7)/0.3))  # Fade-out
            surf  = fuente_popup.render(popup["texto"], True, (255,255,100))
            surf.set_alpha(alpha)
            screen.blit(surf, (px - surf.get_width()//2, py_p))

        # Bolitas de ojos: circulo blanco/azul que viaja por los pasillos
        # usando interpolacion lineal entre las celdas del camino BFS.
        for viaje in viajes[:]:
            viaje["timer"] += dt
            camino = viaje["camino"]
            n_segs = len(camino) - 1
            if n_segs <= 0 or viaje["timer"] >= n_segs / viaje["velocidad"]:
                # Llego a la base de los fantasmas: renace con animacion 
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

    # Pacman ejecuta su animacion de muerte (giro + se hace mas chiquito).
    # Al terminar: si era la ultima vida va a "cortina", sino respawnea.
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

    # Un rectangulo negro baja de arriba a abajo cubriendo la pantalla.
    # Es la transicion visual entre la ultima muerte y el game over.
    elif estado == "cortina":
        timer_cortina += dt
        progreso       = min(timer_cortina / duracion_cortina, 1.0)
        py.draw.rect(screen, (0,0,0), (0, 0, ancho_ventana, int(alto_ventana*progreso)))
        if timer_cortina >= duracion_cortina:
            estado       = "game_over"
            timer_muerte = 0.0  # Reutilizamos timer_muerte para el fade-in del game over

    # Muestra "GAME OVER" y el puntaje final con fade-in de 2 segundos.
    # Despues de 5 segundos en total, el juego cierra el loop y termina.
    elif estado == "game_over":
        timer_muerte += dt
        alpha = int(255 * min(timer_muerte / 2.0, 1.0))
        renderer.dibujar_game_over(score_manager.puntaje, alpha)
        if timer_muerte >= 5.0:
            corriendo = False

    renderer.actualizar_pantalla()

# Cuando el loop termina, cortamos todos los sonidos y cerramos pygame limpiamente.
py.mixer.stop()
py.quit()