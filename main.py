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
from nivel import verificar_nivel_completo, subir_nivel


# ===========================================================================
# INICIALIZACIÓN
# ===========================================================================

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

pacman = pacman(pos_pac)

blinky = Blinky(direccion=(1, 0), posicion=pos_bli, modo="scatter", vida=1)
pinky  = Pinky (direccion=(0,-1), posicion=pos_pin, modo="scatter", vida=1)
inky   = Inky  (direccion=(1, 0), posicion=pos_ink, modo="scatter", vida=1)
clyde  = Clyde (direccion=(-1,0), posicion=pos_cly, modo="scatter", vida=1)
patan  = Patan (direccion=(0, 1), posicion=pos_patan, modo="scatter", vida=1)
negui  = Negui (direccion=(0,-1), posicion=pos_negui, modo="scatter", vida=1)

fantasmas = [blinky, pinky, inky, clyde, patan, negui]


# ===========================================================================
# FUNCIONES AUXILIARES
# Están acá arriba, antes del loop, para que estén disponibles cuando el
# loop las necesite. En Python una función puede usar variables del módulo
# (como "mapa") aunque estén definidas después, siempre que existan en el
# momento en que la función se LLAMA (no cuando se define).
# ===========================================================================

def es_solido_para_fantasma(fila, col):
    """
    Verifica si una celda es sólida (bloqueante) para los fantasmas.

    ¿Por qué necesitamos esta función y no usamos mapa.es_solido directamente?

        Los fantasmas y Pac-Man tienen reglas distintas sobre qué pueden atravesar:

        - Pac-Man NO puede pasar por la puerta de la ghost house ("-").
          Tiene sentido: Pac-Man no puede meterse adentro de la casa.

        - Los fantasmas SÍ pueden pasar por esa puerta, tanto para salir
          al principio del nivel como para volver si son comidos por Pac-Man.

        Por eso esta función trata "-" como NO sólido para los fantasmas,
        mientras que mapa.es_solido lo trata como sólido para todos.

    Parámetros:
        fila : int   → número de fila en la grilla (coordenada Y).
        col  : int   → número de columna en la grilla (coordenada X).

    Retorna:
        True  → la celda es sólida → el fantasma NO puede entrar.
        False → la celda es libre  → el fantasma SÍ puede entrar.
    """
    # Si la posición está fuera del mapa, la tratamos como sólida
    # para que los fantasmas no se "escapen" del tablero
    if fila < 0 or fila >= mapa.filas or col < 0 or col >= mapa.columnas:
        return True

    # La puerta de la ghost house NO es sólida para los fantasmas
    if mapa.grilla[fila, col] == "-":
        return False

    # Para todo lo demás, usamos la lógica normal del mapa
    return mapa.es_solido(fila, col)


def elegir_mejor_direccion(fantasma, target_x, target_y):
    """
    Elige la mejor dirección para que el fantasma se acerque a su objetivo.

    Este es el núcleo del AI de los fantasmas de Pac-Man. El algoritmo del
    juego original usa exactamente esta lógica:

        1. Considera las 4 direcciones: derecha, izquierda, arriba, abajo.
        2. Elimina la dirección OPUESTA a la actual.
           (Regla del Pac-Man original: los fantasmas no pueden dar la vuelta
           mientras se mueven normalmente. Evita que zigzagueen erráticamente.)
        3. Elimina las direcciones que llevan a una PARED.
        4. De las que quedan, elige la que pone al fantasma MÁS CERCA del target.

    ¿Cómo medimos "más cerca"?
        Calculamos distancia al cuadrado para cada opción posible:
            dist² = (col_nueva - target_x)² + (fila_nueva - target_y)²
        La que tenga el número más chico gana. No necesitamos raíz cuadrada
        porque solo comparamos distancias entre sí.

    Caso extremo: si todas las direcciones (excepto la reversa) son paredes,
    le permitimos dar la vuelta para que no quede atascado.

    Parámetros:
        fantasma : Fantasma → el objeto del fantasma que decide su dirección.
        target_x : int      → columna del objetivo.
        target_y : int      → fila del objetivo.

    Retorna:
        tuple (dx, dy) con la dirección ganadora, por ejemplo (1,0) = derecha.
        None si no hay ninguna dirección válida (caso muy raro).
    """
    # La dirección opuesta: si va a la derecha (1,0), la opuesta es (-1,0)
    direccion_opuesta = (-fantasma.direccion[0], -fantasma.direccion[1])

    todas_direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    mejor_dir      = None
    menor_distancia = float("inf")  # infinito como punto de partida

    for dir in todas_direcciones:

        # Regla 1: no dar la vuelta
        if dir == direccion_opuesta:
            continue

        # Celda a la que llegaría el fantasma si elige esta dirección
        col_nueva  = fantasma.posicion[0] + dir[0]
        fila_nueva = fantasma.posicion[1] + dir[1]

        # Regla 2: no ir a una pared
        if es_solido_para_fantasma(fila_nueva, col_nueva):
            continue

        # ¿Qué tan cerca del target queda si elige esta dirección?
        distancia = (col_nueva - target_x) ** 2 + (fila_nueva - target_y) ** 2

        # Si es la más cercana hasta ahora, la guardamos como mejor opción
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_dir       = dir

    # Caso extremo: si todas las opciones son paredes, permitir dar la vuelta
    if mejor_dir is None:
        col_rev  = fantasma.posicion[0] + direccion_opuesta[0]
        fila_rev = fantasma.posicion[1] + direccion_opuesta[1]
        if not es_solido_para_fantasma(fila_rev, col_rev):
            mejor_dir = direccion_opuesta

    return mejor_dir


def elegir_direccion_huyendo(fantasma, pac_x, pac_y):
    """
    Elige la dirección que MAXIMIZA la distancia con Pac-Man (para huir).

    Es el opuesto exacto de elegir_mejor_direccion: en vez de minimizar
    la distancia al objetivo, MAXIMIZAMOS la distancia a Pac-Man.

    Se usa cuando el fantasma está en modo "asustado": Pac-Man comió una
    power pellet (bolita grande) y ahora puede comerlos a ellos.

    La lógica es idéntica a elegir_mejor_direccion pero en el paso 4
    buscamos la distancia MÁS GRANDE en vez de la más chica.

    Parámetros:
        fantasma : Fantasma → el fantasma que está huyendo.
        pac_x    : int      → columna actual de Pac-Man.
        pac_y    : int      → fila actual de Pac-Man.

    Retorna:
        tuple (dx, dy) con la dirección que más aleja al fantasma de Pac-Man.
        None si no hay ninguna dirección válida.
    """
    direccion_opuesta = (-fantasma.direccion[0], -fantasma.direccion[1])
    todas_direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    mejor_dir       = None
    mayor_distancia = -1  # -1 como punto de partida (cualquier distancia real es mayor)

    for dir in todas_direcciones:

        if dir == direccion_opuesta:
            continue

        col_nueva  = fantasma.posicion[0] + dir[0]
        fila_nueva = fantasma.posicion[1] + dir[1]

        if es_solido_para_fantasma(fila_nueva, col_nueva):
            continue

        # Acá queremos la distancia MÁS GRANDE (al revés de cuando perseguimos)
        distancia = (col_nueva - pac_x) ** 2 + (fila_nueva - pac_y) ** 2

        if distancia > mayor_distancia:
            mayor_distancia = distancia
            mejor_dir       = dir

    if mejor_dir is None:
        col_rev  = fantasma.posicion[0] + direccion_opuesta[0]
        fila_rev = fantasma.posicion[1] + direccion_opuesta[1]
        if not es_solido_para_fantasma(fila_rev, col_rev):
            mejor_dir = direccion_opuesta

    return mejor_dir


def verificar_colision_pacman_fantasma(pacman, fantasma):
    """
    Verifica si Pac-Man y un fantasma están en la misma casilla del mapa.

    Este juego usa colisiones por CASILLA (tile-based), no por píxel.
    Si Pac-Man y el fantasma tienen la misma posición en la grilla
    (misma fila y misma columna), se considera que chocaron.

    Es más simple que comparar píxeles y funciona bien porque el movimiento
    también es basado en casillas: cada paso mueve exactamente 1 tile.

    ¿Qué consecuencias tiene la colisión? (lo decide quien llama a esta función)
        - Fantasma en modo NORMAL   → Pac-Man pierde una vida.
        - Fantasma en modo ASUSTADO → Pac-Man se come al fantasma, gana puntos.

    Parámetros:
        pacman   : pacman   → el objeto Pac-Man con su posición.
        fantasma : Fantasma → el objeto del fantasma con su posición.

    Retorna:
        True  → misma casilla → hubo colisión.
        False → casillas distintas → no hay colisión.
    """
    return pacman.posicion == fantasma.posicion


def respawn_jugador():
    """
    Resetea posiciones de Pac-Man y todos los fantasmas tras perder una vida.

    ¿Qué hace exactamente?
        1. Pausa el juego 1 segundo para que el jugador note que perdió.
        2. Manda a Pac-Man a su posición inicial (la "P" del mapa).
        3. Manda a cada fantasma a su posición inicial (dentro de la ghost house).
        4. Resetea las direcciones iniciales de todos.
        5. Cancela el modo asustado si estaba activo.
        6. Pone a todos los fantasmas en modo "scatter" (dispersión).

    ¿Qué NO hace?
        NO resetea el mapa. Los puntos que Pac-Man ya comió NO vuelven.
        Solo se reposicionan los personajes; el puntaje y el mapa no cambian.

    ¿Qué son las variables "global" acá?
        modo_asustado y contador_tiempo_asustado están definidas fuera de esta
        función (a nivel del módulo). Para poder ASIGNARLES un valor nuevo
        desde adentro de la función, necesitamos declararlas con "global".
        Sin eso, Python crearía variables locales y el cambio no se vería afuera.
        Nota: pacman.posicion = pos_pac SÍ funciona sin global porque estamos
        modificando un ATRIBUTO del objeto, no reasignando la variable "pacman".
    """
    global modo_asustado, contador_tiempo_asustado

    # Pausa para que el jugador note que perdió
    py.time.wait(1000)

    # Pac-Man vuelve a su posición inicial
    pacman.posicion  = pos_pac
    pacman.direccion = (1, 0)

    # Cada fantasma vuelve a su posición inicial dentro de la ghost house
    blinky.posicion  = pos_bli
    blinky.direccion = (1, 0)

    pinky.posicion   = pos_pin
    pinky.direccion  = (0, -1)

    inky.posicion    = pos_ink
    inky.direccion   = (1, 0)

    clyde.posicion   = pos_cly
    clyde.direccion  = (-1, 0)

    patan.posicion   = pos_patan
    patan.direccion  = (0, 1)

    negui.posicion   = pos_negui
    negui.direccion  = (0, -1)

    # Cancelar el modo asustado si estaba activo
    modo_asustado            = False
    contador_tiempo_asustado = 0

    for f in fantasmas:
        f.cambiar_modo("scatter")


# ===========================================================================
# VARIABLES DEL JUEGO
# ===========================================================================

modo_asustado            = False
contador_tiempo_asustado = 0
duracion_modo_asustado   = 8    # segundos que duran los fantasmas asustados

reloj            = py.time.Clock()
tiempo_acumulado = 0.0
tiempo_por_paso  = 0.15         # segundos entre cada paso del juego

corriendo = True


# ===========================================================================
# LOOP PRINCIPAL
# Cada iteración es un FRAME. El juego corre a 60 frames por segundo.
# Dentro del loop hay dos "capas" de tiempo:
#   - Cada FRAME: se procesa input, se dibuja todo (60 veces por segundo).
#   - Cada PASO (tiempo_por_paso): se mueve Pac-Man y los fantasmas.
#     Al principio es cada 0.15s (~6.6 veces por segundo). Sube de dificultad.
# ===========================================================================

while corriendo:

    # dt = "delta time": cuántos SEGUNDOS pasaron desde el frame anterior.
    # Dividimos los milisegundos de reloj.tick(60) por 1000 para pasarlo a segundos.
    # reloj.tick(60) también limita el juego a 60 fps como máximo.
    dt = reloj.tick(60) / 1000.0

    # ── INPUT DEL JUGADOR ─────────────────────────────────────────────────
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

    # ── DIBUJO BASE (se hace siempre, cada frame) ─────────────────────────
    renderer.limpiar_pantalla()
    renderer.dibujar_mapa(mapa.grilla)

    # ── LÓGICA DEL JUEGO (se ejecuta cada "paso", no cada frame) ─────────
    # Acumulamos el tiempo pasado. Cuando se acumuló suficiente (tiempo_por_paso),
    # ejecutamos UN paso del juego y restamos ese tiempo del acumulado.
    tiempo_acumulado += dt

    if tiempo_acumulado >= tiempo_por_paso:

        # ── TEMPORIZADOR DEL MODO ASUSTADO ───────────────────────────────
        # Llevamos la cuenta de cuánto tiempo llevan asustados los fantasmas.
        # Cuando se agota, vuelven al modo scatter (dispersión normal).
        if modo_asustado:
            contador_tiempo_asustado += tiempo_por_paso

            if contador_tiempo_asustado >= duracion_modo_asustado:
                modo_asustado            = False
                contador_tiempo_asustado = 0

                for f in fantasmas:
                    f.cambiar_modo("scatter")

        # ── MOVIMIENTO DE PAC-MAN ─────────────────────────────────────────
        # Primero intentamos cambiar a la dirección que el jugador pidió
        # (proxima_direccion). Solo lo hacemos si esa dirección no tiene pared.
        prox_col  = pacman.posicion[0] + pacman.proxima_direccion[0]
        prox_fila = pacman.posicion[1] + pacman.proxima_direccion[1]

        if not mapa.es_solido(prox_fila, prox_col):
            pacman.direccion = pacman.proxima_direccion

        # Después intentamos mover en la dirección actual.
        # Si hay pared adelante, Pac-Man se queda quieto (no rebota).
        nueva_col  = pacman.posicion[0] + pacman.direccion[0]
        nueva_fila = pacman.posicion[1] + pacman.direccion[1]

        if not mapa.es_solido(nueva_fila, nueva_col):
            pacman.movimiento()

            # Revisar si comió algo en la nueva casilla
            col_actual, fila_actual = pacman.posicion
            tile_actual = mapa.grilla[fila_actual, col_actual]

            if tile_actual == ".":
                score_manager.sumar_puntaje(mapa.tiles["."]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

            elif tile_actual == "o":
                score_manager.sumar_puntaje(mapa.tiles["o"]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

                # Activar modo asustado en todos los fantasmas
                modo_asustado            = True
                contador_tiempo_asustado = 0

                for f in fantasmas:
                    f.cambiar_modo("asustado")

        # ── MOVIMIENTO DE FANTASMAS ───────────────────────────────────────
        # Cada fantasma decide su dirección según su modo y luego se mueve.
        # CAMBIO CLAVE respecto al código anterior:
        #   Antes: se usaba f.decidir_direccion() que NO chequeaba paredes,
        #          y luego se usaba mapa.es_solido() que los dejaba sin poder
        #          salir de la ghost house.
        #   Ahora: usamos elegir_mejor_direccion() / elegir_direccion_huyendo()
        #          que SI chequean paredes con es_solido_para_fantasma(),
        #          y el movimiento también usa es_solido_para_fantasma().
        for f in fantasmas:

            if f.modo == "asustado":
                # Modo asustado: el fantasma huye de Pac-Man
                # Elige la dirección que LO ALEJA más de Pac-Man
                pac_x, pac_y = pacman.posicion
                mejor = elegir_direccion_huyendo(f, pac_x, pac_y)
                if mejor:
                    f.cambiar_direccion(mejor)

            else:
                # Modo normal (scatter o chase): el fantasma persigue su target
                # Cada fantasma tiene su propio elegir_target() definido en su clase
                # Inky es especial: necesita la posición de Blinky para calcular su target
                if f.nombre == "Inky":
                    target_x, target_y = f.elegir_target(pacman, blinky)
                else:
                    target_x, target_y = f.elegir_target(pacman)

                # Elegir la dirección que LO ACERCA más al target, evitando paredes
                mejor = elegir_mejor_direccion(f, target_x, target_y)
                if mejor:
                    f.cambiar_direccion(mejor)

            # Mover al fantasma en la dirección elegida.
            # Solo se mueve si la próxima casilla NO es sólida para él.
            nc = f.posicion[0] + f.direccion[0]
            nf = f.posicion[1] + f.direccion[1]

            if not es_solido_para_fantasma(nf, nc):
                f.movimiento()

        # ── DETECCIÓN DE COLISIONES PAC-MAN / FANTASMAS ───────────────────
        # Recorremos todos los fantasmas y chequeamos si alguno está en la
        # misma casilla que Pac-Man. Hay dos casos:
        #
        #   CASO 1 - Fantasma ASUSTADO:
        #       Pac-Man se lo come. Gana 200 puntos. El fantasma vuelve
        #       a su posición inicial dentro de la ghost house.
        #
        #   CASO 2 - Fantasma NORMAL (scatter o chase):
        #       El fantasma atrapa a Pac-Man. Pierde una vida.
        #       Si quedan vidas → respawn. Si no → game over.
        #
        # El "break" al final asegura que solo procesamos UNA colisión por paso.
        # Sin esto, si dos fantasmas están en la misma celda que Pac-Man al mismo
        # tiempo, procesaríamos dos colisiones y podría perder dos vidas de golpe.
        for f in fantasmas:
            if verificar_colision_pacman_fantasma(pacman, f):

                if f.modo == "asustado":
                    # Pac-Man come al fantasma
                    score_manager.sumar_puntaje(200)
                    f.reiniciar_posicion()   # vuelve a la ghost house
                    f.cambiar_modo("scatter")

                else:
                    # Fantasma atrapa a Pac-Man
                    score_manager.restar_vidas()

                    if score_manager.vidas <= 0:
                        # Sin vidas: mostrar game over y terminar
                        renderer.limpiar_pantalla()
                        renderer.dibujar_game_over(score_manager.puntaje)
                        renderer.actualizar_pantalla()
                        py.time.wait(3000)   # 3 segundos mostrando el game over
                        corriendo = False

                    else:
                        # Quedan vidas: reposicionar todos y continuar
                        respawn_jugador()

                # Solo procesamos una colisión por paso
                break

        tiempo_acumulado -= tiempo_por_paso

        # ── VERIFICAR NIVEL COMPLETO ──────────────────────────────────────
        if verificar_nivel_completo(mapa):
            tiempo_por_paso = subir_nivel(score_manager, mapa, tiempo_por_paso)

            modo_asustado            = False
            contador_tiempo_asustado = 0

            pos_pac, pos_bli, pos_pin, pos_ink, pos_cly, pos_patan, pos_negui = mapa.obtener_posiciones_iniciales()

            pacman.posicion  = pos_pac
            pacman.direccion = (1, 0)

            blinky.posicion  = pos_bli
            blinky.direccion = (1, 0)

            pinky.posicion   = pos_pin
            pinky.direccion  = (0, -1)

            inky.posicion    = pos_ink
            inky.direccion   = (1, 0)

            clyde.posicion   = pos_cly
            clyde.direccion  = (-1, 0)

            patan.posicion   = pos_patan
            patan.direccion  = (0, 1)

            negui.posicion   = pos_negui
            negui.direccion  = (0, -1)

            for f in fantasmas:
                f.cambiar_modo("scatter")

    # ── RENDERIZADO (siempre, cada frame) ────────────────────────────────
    renderer.dibujar_pacman(pacman)
    renderer.dibujar_fantasmas(fantasmas)
    renderer.dibujar_hud(
        score_manager.puntaje,
        score_manager.high_score,
        score_manager.vidas,
        score_manager.nivel
    )
    renderer.actualizar_pantalla()

py.quit()