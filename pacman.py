import pygame
import math


class pacman:
    def __init__(self, posicion):
        # Posicion en tiles (col, fila)
        self.posicion = posicion

        # Movimiento
        self.velocidad = 3
        self.direccion = (1, 0)          # tupla: (dx, dy)
        self.proxima_direccion = (1, 0)  # siguiente direccion deseada (era direccion_buffer)

        # Vida
        self.vivo = True

        # Visual
        self.radio = 9  # ajustado para que entre bien en el tile de 20px con margen

        # Animacion de la boca
        self.angulo_boca = 5      # arranca en 5 para que nunca quede completamente cerrada
        self.abriendo = True
        self.contador_boca = 0   # controla cada cuantos frames avanza la animacion

        # Mapa de direccion (tupla) a angulo de rotacion para el dibujo
        self._dir_a_rotacion = {
            (1, 0):  0,     # derecha: sin rotacion
            (-1, 0): 180,   # izquierda: 180°
            (0, -1): 90,    # arriba: 90°
            (0, 1):  270    # abajo: 270°
        }

    def cambiar_direccion(self, nueva_direccion):
        self.proxima_direccion = nueva_direccion

    def movimiento(self):
        col, fila = self.posicion
        self.posicion = (col + self.direccion[0], fila + self.direccion[1])

    def animar_boca(self):
        # El contador sube cada frame. Solo movemos la boca cada 2 frames,
        # asi la animacion es el doble de lenta sin cambiar la logica de angulos.
        self.contador_boca += 1
        if self.contador_boca < 2:
            return
        self.contador_boca = 0

        if self.abriendo:
            self.angulo_boca += 3    # abrir 3 grados
            if self.angulo_boca >= 35:   # maximo 35°, el original no llega a 45
                self.abriendo = False    # llego al maximo, ahora cerrar
        else:
            self.angulo_boca -= 3    # cerrar 3 grados
            if self.angulo_boca <= 5:    # minimo 5° para que nunca quede cerrada del todo
                self.abriendo = True     # llego al minimo, ahora abrir

    def dibujar(self, pantalla, tamano_tile=20):
        # Calcular el centro del tile en pixeles
        x = self.posicion[0] * tamano_tile + tamano_tile // 2
        y = self.posicion[1] * tamano_tile + tamano_tile // 2

        self.animar_boca()

        # Buscamos cuantos grados de rotacion corresponden a la direccion actual
        rotacion = self._dir_a_rotacion.get(self.direccion, 0)

        # Primero dibujamos el circulo amarillo completo y relleno
        pygame.draw.circle(pantalla, (255, 220, 0), (int(x), int(y)), self.radio)

        # Ahora calculamos los 3 puntos del triangulo negro (la boca)
        # -> El primer punto es el centro mismo de Pac-Man
        centro = (int(x), int(y))

        # Estiramos la boca un 40% mas alla del borde del circulo
        largo_boca = self.radio * 1.29

        # -> El segundo punto es el "labio de arriba" de la boca
        punto1 = (
            int(x + largo_boca * math.cos(math.radians(rotacion + self.angulo_boca))),
            int(y - largo_boca * math.sin(math.radians(rotacion + self.angulo_boca)))
        )

        # -> El tercer punto es el "labio de abajo" de la boca
        punto2 = (
            int(x + largo_boca * math.cos(math.radians(rotacion - self.angulo_boca))),
            int(y - largo_boca * math.sin(math.radians(rotacion - self.angulo_boca)))
        )

        # Finalmente dibujamos el triangulo negro uniendo los 3 puntos
        pygame.draw.polygon(pantalla, (0, 0, 0), [centro, punto1, punto2])