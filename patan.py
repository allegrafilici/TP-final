from fantasmas import Fantasma

class Patan(Fantasma):
    """
    Fantasma inventado Patan.

    Patan hereda de la clase Fantasma y tiene un comportamiento propio:
    intenta seguir a Pac-Man desde atrás, eligiendo como objetivo una posición
    ubicada dos casillas detrás de la dirección en la que Pac-Man se está moviendo.
    """

    def __init__(self, direccion, posicion, modo, vida):
        """
        Inicializa al fantasma Patan con su nombre, dirección, posición,
        modo de movimiento, vida e imagen correspondiente.
        """
        super().__init__(
            "Patan",
            direccion,
            posicion,
            modo,
            vida,
            "assets/patan.png"
        )

    def elegir_target(self, pacman, blinky=None):
        """
        Calcula el objetivo de Patan.

        El objetivo se obtiene tomando la posición actual de Pac-Man y
        retrocediendo dos casillas en sentido contrario a su dirección.
        El parámetro blinky queda opcional para que sea compatible con
        decidir_direccion, igual que el resto de fantasmas.
        """
        direc_x, direc_y = pacman.direccion
        pac_x, pac_y = pacman.posicion

        target_x = pac_x - direc_x * 2
        target_y = pac_y - direc_y * 2

        return (target_x, target_y)
