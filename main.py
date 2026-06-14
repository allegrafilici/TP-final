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


py.init()
py.mixer.init()

tamaño_celda = 20
fuente_popup = py.font.SysFont(None, 26)

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

ui_altura     = 40
ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana  = (mapa.filas * tamaño_celda) + ui_altura

screen   = py.display.set_mode((ancho_ventana, alto_ventana))
renderer = Renderer(screen, tamaño_celda)
score_manager = ScoreManager()

pos_pac, pos_bli, pos_pin, pos_ink, pos_cly, pos_patan, pos_negui = mapa.obtener_posiciones_iniciales()

pacman = pacman(pos_pac)
blinky = Blinky(direccion=(1, 0),  posicion=pos_bli,   modo="scatter", vida=1)
pinky  = Pinky (direccion=(0, -1), posicion=pos_pin,   modo="scatter", vida=1)
inky   = Inky  (direccion=(1, 0),  posicion=pos_ink,   modo="scatter", vida=1)
clyde  = Clyde (direccion=(-1, 0), posicion=pos_cly,   modo="scatter", vida=1)
patan  = Patan (direccion=(0, 1),  posicion=pos_patan, modo="scatter", vida=1)
negui  = Negui (direccion=(0, -1), posicion=pos_negui, modo="scatter", vida=1)

# Inicialmente dejamos la lista vacía; se llenará dinámicamente al seleccionar
fantasmas = []


# ===========================================================================
# FUNCIONES AUXILIARES
# ===========================================================================

def es_solido_para_fantasma(fila, col):
    if fila < 0 or fila >= mapa.filas or col < 0 or col >= mapa.columnas:
        return True
    if mapa.grilla[fila, col] == "-":
        return False
    return mapa.es_solido(fila, col)


def encontrar_camino(inicio, destino):
    """
    BFS para encontrar el camino mas corto entre dos celdas siguiendo pasillos.
    Retorna lista de (col, fila) desde inicio hasta destino.
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

        for dc, df in [(1,0), (-1,0), (0,1), (0,-1)]:
            vecino = (col + dc, fila + df)
            if vecino not in padres and not es_solido_para_fantasma(fila + df, col + dc):
                padres[vecino] = actual
                cola.append(vecino)

    return [inicio, destino]


def elegir_mejor_direccion(fantasma, target_x, target_y):
    opuesta    = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir  = None
    menor_dist = float("inf")
    for dir in [(1,0),(-1,0),(0,1),(0,-1)]:
        if dir == opuesta: continue
        nc = fantasma.posicion[0] + dir[0]
        nf = fantasma.posicion[1] + dir[1]
        if es_solido_para_fantasma(nf, nc): continue
        dist = (nc-target_x)**2 + (nf-target_y)**2
        if dist < menor_dist:
            menor_dist = dist; mejor_dir = dir
    if mejor_dir is None:
        nc = fantasma.posicion[0] + opuesta[0]
        nf = fantasma.posicion[1] + opuesta[1]
        if not es_solido_para_fantasma(nf, nc):
            mejor_dir = opuesta
    return mejor_dir


def elegir_direccion_huyendo(fantasma, pac_x, pac_y):
    opuesta    = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir  = None
    mayor_dist = -1
    for dir in [(1,0),(-1,0),(0,1),(0,-1)]:
        if dir == opuesta: continue
        nc = fantasma.posicion[0] + dir[0]
        nf = fantasma.posicion[1] + dir[1]
        if es_solido_para_fantasma(nf, nc): continue
        dist = (nc-pac_x)**2 + (nf-pac_y)**2
        if dist > mayor_dist:
            mayor_dist = dist; mejor_dir = dir
    if mejor_dir is None:
        nc = fantasma.posicion[0] + opuesta[0]
        nf = fantasma.posicion[1] + opuesta[1]
        if not es_solido_para_fantasma(nf, nc):
            mejor_dir = opuesta
    return mejor_dir


def verificar_colision_pacman_fantasma(pacman, fantasma):
    return pacman.posicion == fantasma.posicion


def resolver_colision(f):
    """
    Maneja la colision entre Pac-Man y el fantasma f.
    """
    global estado, timer_muerte, es_ultima_vida, contador_fantasmas_comidos

    if f.modo == "asustado":
        puntos = 200 * (2 ** contador_fantasmas_comidos)
        score_manager.sumar_puntaje(puntos)
        popups.append({"pos": f.posicion, "timer": 0.0, "texto": str(puntos)})

        camino = encontrar_camino(f.posicion, f.posicion_inicial)

        f.oculto      = True
        f.apareciendo = False
        f.reiniciar_posicion()
        f.cambiar_modo("scatter")

        viajes.append({
            "camino":    camino,
            "timer":     0.0,
            "velocidad": 12,
            "fantasma":  f       
        })

        contador_fantasmas_comidos += 1
        return False

    else:
        # Freno sonidos de ambiente y reproduzco muerte
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


def respawn_jugador():
    """Resetea todos los personajes. Cancela viajes y popups en curso."""
    global modo_asustado, contador_tiempo_asustado, contador_fantasmas_comidos

    viajes.clear()
    popups.clear()

    pacman.posicion  = pos_pac ; pacman.direccion  = (1, 0)

    for f in fantasmas:
        f.reiniciar()


def resetear_nivel():
    """Repositiona todos los personajes al subir de nivel."""
    global modo_asustado, contador_tiempo_asustado, contador_fantasmas_comidos

    viajes.clear()
    popups.clear()
    modo_asustado              = False
    contador_tiempo_asustado   = 0
    contador_fantasmas_comidos = 0

    pos = mapa.obtener_posiciones_iniciales()
    pacman.posicion  = pos[0]; pacman.direccion  = (1, 0)
    blinky.posicion  = pos[1]; blinky.direccion  = (1, 0)
    pinky.posicion   = pos[2]; pinky.direccion   = (0, -1)
    inky.posicion    = pos[3]; inky.direccion    = (1, 0)
    clyde.posicion   = pos[4]; clyde.direccion   = (-1, 0)
    patan.posicion   = pos[5]; patan.direccion   = (0, 1)
    negui.posicion   = pos[6]; negui.direccion   = (0, -1)

    for f in fantasmas:
        f.reiniciar()

    return pos


# ===========================================================================
# VARIABLES DEL JUEGO Y CONFIGURACIÓN DE SELECCIÓN
# ===========================================================================

estado = "inicio"  # Cambiado para iniciar en la pantalla de bienvenida

# Configuración de pantallas de selección
esquinas_nombres = ["Arriba-Izquierda", "Arriba-Derecha", "Abajo-Izquierda", "Abajo-Derecha"]
esquina_actual = 0
fantasmas_seleccionados = {}  # Guardará {Nombre: Esquina}

# Estructura de rectángulos y colores para los botones interactivos
fantasmas_info_UI = {
    "Blinky": {"color": (222, 0, 0),     "rect": py.Rect(60,  150, 200, 60)},
    "Pinky":  {"color": (255, 184, 222), "rect": py.Rect(300, 150, 200, 60)},
    "Inky":   {"color": (0, 222, 222),   "rect": py.Rect(60,  250, 200, 60)},
    "Clyde":  {"color": (222, 138, 0),   "rect": py.Rect(300, 250, 200, 60)},
    "Patan":  {"color": (0, 200, 0),     "rect": py.Rect(60,  350, 200, 60)},
    "Negui":  {"color": (170, 70, 220),  "rect": py.Rect(300, 350, 200, 60)}
}

modo_asustado              = False
contador_tiempo_asustado   = 0
duracion_modo_asustado     = 8
contador_fantasmas_comidos = 0

popups = []
viajes = []

duracion_aparicion = 0.5  

reloj            = py.time.Clock()
tiempo_acumulado = 0.0
tiempo_por_paso  = 0.15

timer_muerte     = 0.0
duracion_muerte  = 1.5
timer_cortina    = 0.0
duracion_cortina = 1.2
es_ultima_vida   = False

vida_extra_otorgada = False

corriendo = True
sonido_inicio.play()


# ===========================================================================
# LOOP PRINCIPAL
# ===========================================================================

while corriendo:

    dt = reloj.tick(60) / 1000.0

    for evento in py.event.get():
        if evento.type == py.QUIT:
            corriendo = False
            
        elif evento.type == py.KEYDOWN:
            if estado == "inicio":
                if evento.key == py.K_RETURN:  # ENTER pasa a selección
                    estado = "seleccion"
            elif estado == "jugando":
                if evento.key == py.K_UP:    pacman.cambiar_direccion((0,-1))
                elif evento.key == py.K_DOWN:  pacman.cambiar_direccion((0, 1))
                elif evento.key == py.K_LEFT:  pacman.cambiar_direccion((-1,0))
                elif evento.key == py.K_RIGHT: pacman.cambiar_direccion((1, 0))
                
        elif evento.type == py.MOUSEBUTTONDOWN and estado == "seleccion":
            if evento.button == 1:  # Clic izquierdo
                pos_mouse = py.mouse.get_pos()
                for nombre, info in fantasmas_info_UI.items():
                    if info["rect"].collidepoint(pos_mouse) and nombre not in fantasmas_seleccionados:
                        # Asignamos el fantasma seleccionado a la esquina correspondiente
                        fantasmas_seleccionados[nombre] = esquinas_nombres[esquina_actual]
                        esquina_actual += 1
                        
                        # Al completar las 4 esquinas, filtramos y activamos los fantasmas en el juego
                        if esquina_actual == 4:
                            mapeo_instancias = {
                                "Blinky": blinky,
                                "Pinky": pinky,
                                "Inky": inky,
                                "Clyde": clyde,
                                "Patan": patan,
                                "Negui": negui
                            }
                            fantasmas_activos = []
                            for nom in fantasmas_seleccionados.keys():
                                f = mapeo_instancias[nom]
                                f.esquina_asignada = fantasmas_seleccionados[nom]
                                fantasmas_activos.append(f)
                            
                            fantasmas = fantasmas_activos  # Sobrescribimos la lista global
                            estado = "jugando"
                            sonido_sirena_loop.play(-1)  # Arranca la sirena
                        break

    # =========================================================================
    # GESTIÓN DE RENDERIZADO Y LÓGICA SEGÚN EL ESTADO
    # =========================================================================
    
    if estado == "inicio":
        renderer.dibujar_pantalla_inicio()
        renderer.actualizar_pantalla()
        
    elif estado == "seleccion":
        renderer.dibujar_pantalla_seleccion(esquinas_nombres, esquina_actual, fantasmas_info_UI, fantasmas_seleccionados)
        renderer.actualizar_pantalla()
        
    else:
        # Lógica de juego normal
        renderer.limpiar_pantalla()
        if estado != "game_over":
            renderer.dibujar_mapa(mapa.grilla)

        # =========================================================================
        # ESTADO: JUGANDO
        # =========================================================================
        if estado == "jugando":
            tiempo_acumulado += dt

            if tiempo_acumulado >= tiempo_por_paso:

                if modo_asustado:
                    contador_tiempo_asustado += tiempo_por_paso
                    if contador_tiempo_asustado >= duracion_modo_asustado:
                        modo_asustado              = False
                        contador_tiempo_asustado   = 0
                        contador_fantasmas_comidos = 0
                        
                        # Frenar power pallet, retomar sirena
                        sonido_power_pallet.stop()
                        sonido_sirena_loop.play(-1)
                        
                        for f in fantasmas:
                            if not f.oculto:   
                                f.cambiar_modo("scatter")

                prox_col  = pacman.posicion[0] + pacman.proxima_direccion[0]
                prox_fila = pacman.posicion[1] + pacman.proxima_direccion[1]
                if not mapa.es_solido(prox_fila, prox_col):
                    pacman.direccion = pacman.proxima_direccion

                nueva_col  = pacman.posicion[0] + pacman.direccion[0]
                nueva_fila = pacman.posicion[1] + pacman.direccion[1]

                if not mapa.es_solido(nueva_fila, nueva_col):
                    pacman.movimiento()
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
                        contador_tiempo_asustado   = 0
                        contador_fantasmas_comidos = 0
                        for f in fantasmas:
                            if not f.oculto:   
                                f.cambiar_modo("asustado")
                else:
                    pacman.se_movio = False

                colision_resuelta = False
                for f in fantasmas:
                    if f.oculto or f.apareciendo:   
                        continue
                    if verificar_colision_pacman_fantasma(pacman, f):
                        colision_resuelta = resolver_colision(f)
                        break

                if not colision_resuelta:
                    for f in fantasmas:
                        if f.oculto or f.apareciendo:   
                            continue

                        if f.modo == "asustado":
                            pac_x, pac_y = pacman.posicion
                            mejor = elegir_direccion_huyendo(f, pac_x, pac_y)
                        else:
                            if f.nombre == "Inky":
                                tx, ty = f.elegir_target(pacman, blinky)
                            else:
                                tx, ty = f.elegir_target(pacman)
                            mejor = elegir_mejor_direccion(f, tx, ty)

                        if mejor:
                            f.cambiar_direccion(mejor)

                        nc = f.posicion[0] + f.direccion[0]
                        nf = f.posicion[1] + f.direccion[1]
                        if not es_solido_para_fantasma(nf, nc):
                            f.movimiento()

                        if verificar_colision_pacman_fantasma(pacman, f):
                            colision_resuelta = resolver_colision(f)
                            if colision_resuelta:
                                break

                tiempo_acumulado -= tiempo_por_paso

                if not vida_extra_otorgada and score_manager.puntaje >= 10000:
                    score_manager.vidas += 1
                    sonido_vida_extra.play()
                    vida_extra_otorgada = True
                    popups.append({"pos": pacman.posicion, "timer": 0.0, "texto": "1UP!"})

                if not colision_resuelta and verificar_nivel_completo(mapa):
                    py.mixer.stop()
                    tiempo_por_paso = subir_nivel(score_manager, mapa, tiempo_por_paso)
                    resetear_nivel()
                    sonido_sirena_loop.play(-1)

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
                px    = col  * tamaño_celda + tamaño_celda // 2
                py_p  = fila * tamaño_celda - int(30 * progreso)
                alpha = 255 if progreso < 0.7 else int(255 * (1-(progreso-0.7)/0.3))
                surf  = fuente_popup.render(popup["texto"], True, (255,255,100))
                surf.set_alpha(alpha)
                screen.blit(surf, (px - surf.get_width()//2, py_p))

            for viaje in viajes[:]:
                viaje["timer"] += dt
                camino  = viaje["camino"]
                n_segs  = len(camino) - 1

                if n_segs <= 0:
                    f_v = viaje["fantasma"]
                    f_v.oculto             = False
                    f_v.apareciendo        = True
                    f_v.progreso_aparicion = 0.0
                    viajes.remove(viaje)
                    continue

                tiempo_total = n_segs / viaje["velocidad"]

                if viaje["timer"] >= tiempo_total:
                    f_v = viaje["fantasma"]
                    f_v.oculto             = False
                    f_v.apareciendo        = True
                    f_v.progreso_aparicion = 0.0
                    viajes.remove(viaje)
                    continue

                progreso  = viaje["timer"] / tiempo_total
                pos_float = progreso * n_segs
                idx       = min(int(pos_float), n_segs - 1)
                frac      = pos_float - idx

                col_a, fila_a = camino[idx]
                col_b, fila_b = camino[idx + 1]

                px_v = int((col_a + (col_b - col_a) * frac) * tamaño_celda + tamaño_celda // 2)
                py_v = int((fila_a + (fila_b - fila_a) * frac) * tamaño_celda + tamaño_celda // 2)

                py.draw.circle(screen, (180, 180, 255), (px_v, py_v), 5)
                py.draw.circle(screen, (255, 255, 255), (px_v, py_v), 3)

        # =========================================================================
        # ESTADO: MURIENDO
        # =========================================================================
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
                    sonido_sirena_loop.play(-1)  # Retomar la sirena luego de respawnear

            renderer.dibujar_pacman(pacman)
            renderer.dibujar_hud(score_manager.puntaje, score_manager.high_score,
                                 score_manager.vidas, score_manager.nivel)

        # =========================================================================
        # ESTADO: CORTINA
        # =========================================================================
        elif estado == "cortina":

            timer_cortina    += dt
            progreso_cortina  = min(timer_cortina / duracion_cortina, 1.0)
            py.draw.rect(screen, (0,0,0), (0, 0, ancho_ventana, int(alto_ventana * progreso_cortina)))

            if timer_cortina >= duracion_cortina:
                estado       = "game_over"
                timer_muerte = 0.0

        # =========================================================================
        # ESTADO: GAME OVER
        # =========================================================================
        elif estado == "game_over":

            timer_muerte += dt
            alpha = int(255 * min(timer_muerte / 2.0, 1.0))
            renderer.dibujar_game_over(score_manager.puntaje, alpha)

            if timer_muerte >= 5.0:
                corriendo = False

        renderer.actualizar_pantalla()

# Cortar todos los sonidos al salir
py.mixer.stop()
py.quit()