import pygame
import math


class pacman:
    """
    Esta clase representa a Pac-Man dentro del juego.

    Guarda su posición, dirección, estado de vida y toda la parte visual:
    la animación de la boca, la orientación según hacia dónde se mueve
    y la animación de muerte.
    """

    def __init__(self, posicion):
        """
        Inicializo a Pac-Man en una posición del mapa.

        La posición está en tiles, no en píxeles.
        Por ejemplo, (5, 10) significa columna 5, fila 10.
        """
        self.posicion          = posicion
        self.velocidad         = 3

        # Dirección actual de movimiento.
        # (1, 0) significa derecha.
        self.direccion         = (1, 0)

        # Dirección que el jugador quiere tomar.
        # Se guarda aparte para poder girar cuando el camino esté libre.
        self.proxima_direccion = (1, 0)

        self.vivo  = True
        self.radio = 9

        # Variables para animar la boca.
        self.angulo_boca   = 5
        self.abriendo      = True
        self.contador_boca = 0
        self.se_movio      = True

        # Variables para la animación de muerte.
        self.muriendo        = False
        self.progreso_muerte = 0.0

        # Este acumulador funciona como un cronómetro propio de Pac-Man.
        # main.py lo va aumentando con dt en cada frame.
        # Cuando llega al tiempo necesario, Pac-Man avanza una casilla.
        self.acumulador = 0.0

        # Según la dirección, la boca se dibuja mirando hacia otro lado.
        self._dir_a_rotacion = {
            (1,  0):   0,   # derecha
            (-1, 0): 180,   # izquierda
            (0, -1):  90,   # arriba
            (0,  1): 270,   # abajo
        }

    def cambiar_direccion(self, nueva_direccion):
        """
        Guardo la próxima dirección que quiere tomar el jugador.

        No cambio la dirección real directamente porque capaz hay una pared.
        main.py después revisa si se puede girar.
        """
        self.proxima_direccion = nueva_direccion

    def movimiento(self, limite_columnas=None):
        """
        Muevo a Pac-Man una casilla en su dirección actual.

        Si limite_columnas tiene un valor, uso módulo para que Pac-Man pueda
        atravesar el túnel lateral y aparecer del otro lado del mapa.
        """
        col, fila = self.posicion
        nueva_col = col + self.direccion[0]

        if limite_columnas is not None:
            nueva_col %= limite_columnas

        self.posicion = (nueva_col, fila + self.direccion[1])

    def animar_boca(self):
        """
        Animo la boca de Pac-Man abriéndose y cerrándose.

        Si Pac-Man no se movió, la boca vuelve lentamente a estar casi cerrada.
        Si sí se movió, alterna entre abrir y cerrar.
        """
        if not self.se_movio:
            if self.angulo_boca > 5:
                self.angulo_boca = max(5, self.angulo_boca - 3)
            return

        self.contador_boca += 1

        # Esto hace que la animación no vaya demasiado rápido.
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
        Dibujo la animación de muerte de Pac-Man.

        La idea es que Pac-Man vaya achicándose mientras gira.
        progreso_muerte va de 0.0 a 1.0:
        - 0.0 significa que recién empieza la muerte.
        - 1.0 significa que la animación terminó.
        """
        progreso     = self.progreso_muerte
        radio_actual = max(0, int(self.radio * (1.0 - progreso)))

        if radio_actual == 0:
            return

        rotacion_spin    = progreso * 720  # Gira 2 vueltas completas mientras se achica
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
        Dibujo a Pac-Man en pantalla.

        Primero convierto su posición de tiles a píxeles.
        Después, si está muriendo, dibujo la animación de muerte.
        Si no, dibujo el círculo amarillo y el triángulo negro de la boca.
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