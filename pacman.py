import pygame
import math


class pacman:
    def __init__(self, posicion):
        self.posicion          = posicion
        self.velocidad         = 3
        self.direccion         = (1, 0)
        self.proxima_direccion = (1, 0)
        self.vivo              = True
        self.radio             = 9

        self.angulo_boca   = 5
        self.abriendo      = True
        self.contador_boca = 0
        self.se_movio      = True

        self.muriendo        = False
        self.progreso_muerte = 0.0

        # acumulador: cuanto tiempo paso desde el ultimo movimiento.
        # main.py lo incrementa con dt cada frame y cuando supera el
        # tiempo_por_paso de Pac-Man (que depende de si hay power pellet),
        # Pac-Man da un paso y el acumulador se resetea.
        self.acumulador = 0.0

        self._dir_a_rotacion = {
            (1,  0):   0,
            (-1, 0): 180,
            (0, -1):  90,
            (0,  1): 270,
        }

    def cambiar_direccion(self, nueva_direccion):
        self.proxima_direccion = nueva_direccion

    def movimiento(self, limite_columnas=None):
        col, fila = self.posicion
        nueva_col = col + self.direccion[0]
        if limite_columnas is not None:
            nueva_col %= limite_columnas
        self.posicion = (nueva_col, fila + self.direccion[1])

    def animar_boca(self):
        if not self.se_movio:
            if self.angulo_boca > 5:
                self.angulo_boca = max(5, self.angulo_boca - 3)
            return

        self.contador_boca += 1
        if self.contador_boca < 2:
            return
        self.contador_boca = 0

        if self.abriendo:
            self.angulo_boca += 3
            if self.angulo_boca >= 35:
                self.abriendo = False
        else:
            self.angulo_boca -= 3
            if self.angulo_boca <= 5:
                self.abriendo = True

    def _dibujar_muerte(self, pantalla, x, y):
        progreso     = self.progreso_muerte
        radio_actual = max(0, int(self.radio * (1.0 - progreso)))
        if radio_actual == 0:
            return
        rotacion_spin    = progreso * 720
        angulo_boca_fijo = 30
        pygame.draw.circle(pantalla, (255, 220, 0), (int(x), int(y)), radio_actual)
        largo = radio_actual * 1.29
        p1 = (
            int(x + largo * math.cos(math.radians(rotacion_spin + angulo_boca_fijo))),
            int(y - largo * math.sin(math.radians(rotacion_spin + angulo_boca_fijo)))
        )
        p2 = (
            int(x + largo * math.cos(math.radians(rotacion_spin - angulo_boca_fijo))),
            int(y - largo * math.sin(math.radians(rotacion_spin - angulo_boca_fijo)))
        )
        pygame.draw.polygon(pantalla, (0, 0, 0), [(int(x), int(y)), p1, p2])

    def dibujar(self, pantalla, tamano_tile=20):
        x = self.posicion[0] * tamano_tile + tamano_tile // 2
        y = self.posicion[1] * tamano_tile + tamano_tile // 2
        if self.muriendo:
            self._dibujar_muerte(pantalla, x, y)
            return
        self.animar_boca()
        rotacion = self._dir_a_rotacion.get(self.direccion, 0)
        pygame.draw.circle(pantalla, (255, 220, 0), (int(x), int(y)), self.radio)
        centro = (int(x), int(y))
        largo  = self.radio * 1.29
        p1 = (
            int(x + largo * math.cos(math.radians(rotacion + self.angulo_boca))),
            int(y - largo * math.sin(math.radians(rotacion + self.angulo_boca)))
        )
        p2 = (
            int(x + largo * math.cos(math.radians(rotacion - self.angulo_boca))),
            int(y - largo * math.sin(math.radians(rotacion - self.angulo_boca)))
        )
        pygame.draw.polygon(pantalla, (0, 0, 0), [centro, p1, p2])