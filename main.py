import numpy as np
import pygame as py
import random

from blinky import *
from pinky import *
from clyde import *
from inky import *
from mapa import *
from pacman import *
from fantasmas import *
from render import *

# inicialización
py.init()
py.mixer.init()

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

ancho_ventana = mapa.columnas * tamaño_celda
alto_ventana = (mapa.filas * tamaño_celda)

screen = py.display.set_mode((ancho_ventana, alto_ventana))

class Pantallas:
    
    def __init__(self, screen):
        self.screen = screen
        self.fuente = py.font.Font(None, 36)
        self.fuente_chica = py.font.Font(None, 24)
        self.color_texto = (255, 255, 0)            
        self.color_activo = (0, 255, 0)             
        self.color_instruccion = (150, 150, 150)    
        
        self.ancho_pantalla = self.screen.get_width()
        self.alto_pantalla = self.screen.get_height()
    
    def pantalla_de_inicio(self):
        esperando = True
        while esperando:
            self.screen.fill((0, 0, 0))
            
            texto_titulo = self.fuente.render("PAC-MAN", True, self.color_texto)
            x_titulo = (self.ancho_pantalla - texto_titulo.get_width()) // 2
            y_titulo = (self.alto_pantalla // 2) - 20
            self.screen.blit(texto_titulo, (x_titulo, y_titulo))
            
            texto_enter = self.fuente_chica.render("Presiona ENTER para comenzar", True, self.color_instruccion)
            x_enter = (self.ancho_pantalla - texto_enter.get_width()) // 2
            y_enter = y_titulo + 50
            self.screen.blit(texto_enter, (x_enter, y_enter))
            
            py.display.flip()
            
            for evento in py.event.get():
                if evento.type == py.QUIT:
                    py.quit()
                    exit()
                if evento.type == py.KEYDOWN and evento.key == py.K_RETURN:
                    esperando = False
    
    def pantalla_de_seleccion(self):
        nombres = {
            py.K_1: "Blinky", py.K_2: "Pinky", py.K_3: "Inky", 
            py.K_4: "Clyde", py.K_5: "Negui", py.K_6: "Patan"
        }
        seleccionados = set()
        esperando = True
        
        while esperando:
            self.screen.fill((0, 0, 0))
            
            titulo = f"Selecciona hasta 4 fantasmas ({len(seleccionados)}/4)"
            texto_titulo = self.fuente.render(titulo, True, (255, 255, 255))
            x_titulo = (self.ancho_pantalla - texto_titulo.get_width()) // 2
            self.screen.blit(texto_titulo, (x_titulo, 60))
            
            y_inicial = 130
            for tecla, nombre in nombres.items():
                color = self.color_activo if nombre in seleccionados else self.color_texto
                texto = self.fuente.render(f"{tecla - 48}- {nombre}", True, color)
                x_opcion = (self.ancho_pantalla - texto.get_width()) // 2
                self.screen.blit(texto, (x_opcion, y_inicial))
                y_inicial += 40
                
            texto_enter = self.fuente_chica.render("Presiona ENTER para confirmar selección", True, self.color_instruccion)
            x_enter = (self.ancho_pantalla - texto_enter.get_width()) // 2
            self.screen.blit(texto_enter, (x_enter, y_inicial + 20))
                
            py.display.flip()
            
            for evento in py.event.get():
                if evento.type == py.QUIT:
                    py.quit()
                    exit()
                elif evento.type == py.KEYDOWN:
                    if evento.key in nombres:
                        fantasma = nombres[evento.key]
                        if fantasma in seleccionados:
                            seleccionados.remove(fantasma)
                        elif len(seleccionados) < 4:
                            seleccionados.add(fantasma)
                    elif evento.key == py.K_RETURN and seleccionados:
                        esperando = False
                        
        return list(seleccionados)
    
    def elegir_esquina(self, lista_fantasmas):
        esquinas_asignadas = {}
        opciones = {
            py.K_1: "Arriba-Izquierda", py.K_2: "Arriba-Derecha", 
            py.K_3: "Abajo-Izquierda", py.K_4: "Abajo-Derecha"
        }
        
        for i, fantasma in enumerate(lista_fantasmas):
            esperando = True
            while esperando:
                self.screen.fill((0, 0, 0))
                
                titulo = f"Asigna una esquina a {fantasma} ({i+1}/{len(lista_fantasmas)})"
                texto_titulo = self.fuente.render(titulo, True, (255, 255, 255))
                x_titulo = (self.ancho_pantalla - texto_titulo.get_width()) // 2
                self.screen.blit(texto_titulo, (x_titulo, 60))
                
                y_inicial = 140
                for tecla, esquina in opciones.items():
                    texto = self.fuente.render(f"{tecla - 48}- {esquina}", True, self.color_texto)
                    x_opcion = (self.ancho_pantalla - texto.get_width()) // 2
                    self.screen.blit(texto, (x_opcion, y_inicial))
                    y_inicial += 40
                
                py.display.flip()
                
                for evento in py.event.get():
                    if evento.type == py.QUIT:
                        py.quit()
                        exit()
                    elif evento.type == py.KEYDOWN:
                        if evento.key in opciones:
                            esquinas_asignadas[fantasma] = opciones[evento.key]
                            esperando = False
                            
        return esquinas_asignadas


renderer = Renderer(screen, tamaño_celda)

score_manager = ScoreManager()

pos_pac, pos_bli, pos_pin, pos_ink, pos_cly = mapa.obtener_posiciones_iniciales()

# inicializamos Pac-Man
pacman = pacman(pos_pac)

# inicializamos fantasmas
blinky = Blinky(direccion=(1, 0), posicion=pos_bli, modo="scatter", vida=1)
pinky = Pinky(direccion=(0, -1), posicion=pos_pin, modo="scatter", vida=1)
inky = Inky(direccion=(1, 0), posicion=pos_ink, modo="scatter", vida=1)
clyde = Clyde(direccion=(-1, 0), posicion=pos_cly, modo="scatter", vida=1)

fantasmas = [blinky, pinky, inky, clyde]


pantallas = Pantallas(screen)
pantallas.pantalla_de_inicio()
fantasmas_seleccionados = pantallas.pantalla_de_seleccion()
esquinas_asignadas = pantallas.elegir_esquina(fantasmas_seleccionados)

# Filtramos la lista original de fantasmas para quedarnos solo con los elegidos y guardarles su esquina
mapa_instancias = {"Blinky": blinky, "Pinky": pinky, "Inky": inky, "Clyde": clyde}
fantasmas = []
for nombre in fantasmas_seleccionados:
    if nombre in mapa_instancias:
        fantasma_obj = mapa_instancias[nombre]
        fantasma_obj.esquina_asignada = esquinas_asignadas[nombre]
        fantasmas.append(fantasma_obj)


# variables del modo asustado
modo_asustado = False
contador_tiempo_asustado = 0
duracion_modo_asustado = 8

# tiempo
reloj = py.time.Clock()
tiempo_acumulado = 0.0
tiempo_por_paso = 0.15

corriendo = True
sonido_sirena_loop.play(-1)

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

        #controlar duración del modo asustado
        if modo_asustado:
            contador_tiempo_asustado += tiempo_por_paso

            if contador_tiempo_asustado >= duracion_modo_asustado:
                modo_asustado = False
                contador_tiempo_asustado = 0
                sonido_power_pallet.stop()
                sonido_sirena_loop.play(-1)

                for f in fantasmas:
                    f.cambiar_modo("scatter")

        #movimiento Pac-Man
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
                if not modo_asustado:
                    sonido_comer.play()

            elif tile_actual == "o":
                score_manager.sumar_puntaje(mapa.tiles["o"]["score"])
                mapa.actualizar_celda(fila_actual, col_actual, " ")

                if not modo_asustado:
                    sonido_sirena_loop.stop()
                    sonido_power_pallet.play()
                    
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

    renderer.dibujar_pacman(pacman)
    renderer.dibujar_fantasmas(fantasmas)
    renderer.dibujar_hud(score_manager.puntaje, score_manager.high_score, score_manager.vidas, score_manager.nivel)
    renderer.actualizar_pantalla()

py.quit()
