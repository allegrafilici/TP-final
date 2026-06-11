from fantasmas import Fantasma


class Blinky(Fantasma):

    def __init__(self, direccion, posicion, modo, vida):

        super().__init__(
            "Blinky",
            direccion,
            posicion,
            (255, 0, 0),
            modo,
            vida
        )

    def elegir_target(self, pacman):
        return pacman.posicion
