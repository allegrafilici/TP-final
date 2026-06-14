from fantasmas import Fantasma

class Negui(Fantasma):
    """
    Fantasma inventado Negui.

    Negui hereda de la clase Fantasma y tiene un comportamiento propio:
    elige como objetivo una posición reflejada de Pac-Man respecto del centro
    aproximado del mapa. Es decir, si Pac-Man está de un lado del mapa,
    Negui intenta ir hacia el lado contrario.
    """

    def __init__(self, direccion, posicion, modo, vida):
        """
        Inicializa al fantasma Negui con su nombre, dirección, posición,
        modo de movimiento, vida e imagen correspondiente.
        """
        super().__init__(
            "Negui",
            direccion,
            posicion,
            modo,
            vida,
            "assets/negui.png"
        )

    def elegir_target(self, pacman, blinky=None):
        """
        Calcula el objetivo de Negui.

        El objetivo se calcula reflejando la posición de Pac-Man respecto
        del centro aproximado del mapa. El parámetro blinky queda opcional
        para que sea compatible con decidir_direccion, igual que el resto
        de fantasmas.
        """
        centro_x = 14
        centro_y = 15

        pac_x, pac_y = pacman.posicion

        target_x = centro_x * 2 - pac_x
        target_y = centro_y * 2 - pac_y

        return (target_x, target_y)
