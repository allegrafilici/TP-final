from fantasmas import Fantasma

class Negui(Fantasma):
    """
    Fantasma inventado Negui.

    Negui hereda de la clase Fantasma y tiene un comportamiento propio:
    elije como objetivo una posicion reflejada de Pac-Man respecto del centro
    aproximado del mapa. Es decir, si Pac-Man esta de un lado del mapa,
    Negui intenta ir hacia el lado contrario.
    """

    def __init__(self, direccion, posicion, modo, vida):
        """
        Inicializa al fantasma Negui con su nombre, direccion, posicion,
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

    def elegir_target(self, pacman):
        """
        Calcula el objetivo de Negui.

        El objetivo se calcula reflejando la posicion de Pac-Man respecto
        del centro aproximado del mapa.
        """
        centro_x = 14
        centro_y = 15

        pac_x, pac_y = pacman.posicion

        target_x = centro_x * 2 - pac_x
        target_y = centro_y * 2 - pac_y

        return (target_x, target_y)