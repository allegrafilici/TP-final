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

        self.angulo_boca  = 5
        self.abriendo     = True
        self.contador_boca = 0

        # se_movio: main.py lo pone en True cuando Pac-Man se pudo mover,
        # en False cuando hay una pared adelante y no puede moverse.
        # animar_boca() lo usa para cerrar la boca cuando esta bloqueado.
        self.se_movio = True

        self.muriendo         = False
        self.progreso_muerte  = 0.0

        self._dir_a_rotacion = {
            (1,  0):   0,
            (-1, 0): 180,
            (0, -1):  90,
            (0,  1): 270,
        }

    def cambiar_direccion(self, nueva_direccion):
        self.proxima_direccion = nueva_direccion

    def movimiento(self):
        col, fila = self.posicion
        self.posicion = (col + self.direccion[0], fila + self.direccion[1])

    def animar_boca(self):
        """
        Anima la apertura y cierre de la boca.

        CUANDO PAC-MAN SE MUEVE (se_movio == True):
            Ciclo normal: abre hasta 35° y cierra hasta 5°,
            cambiando 3° cada 2 frames.

        CUANDO PAC-MAN ESTA BLOQUEADO (se_movio == False):
            En vez de seguir el ciclo, la boca se cierra gradualmente
            hasta 5° y se queda ahí. Así no parece que "come" la pared.
            Cuando vuelva a moverse, el ciclo retoma normalmente.
        """
        if not self.se_movio:
            # Cerrar la boca de a poco hasta llegar al minimo
            if self.angulo_boca > 5:
                self.angulo_boca = max(5, self.angulo_boca - 3)
            return  # no avanzar el ciclo normal

        # Animacion normal: cambia cada 2 frames
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
        """
        Animacion de muerte: gira 2 vueltas mientras se encoge.
        Usa self.progreso_muerte (0.0 a 1.0), actualizado por main.py.
        """
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
        """
        Dibuja a Pac-Man.
        Si self.muriendo es True, llama a _dibujar_muerte().
        Si no, dibuja la animacion normal de boca con rotacion segun direccion.
        """
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