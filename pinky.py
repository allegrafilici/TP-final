from fantasmas import Fantasma

class Pinky(Fantasma):

    def __init__(self, direccion, posicion, modo, vida):

        super().__init__(
            "Pinky",
            direccion,
            posicion,
            (255, 105, 180),
            modo,
            1
        )
    
    def elegir_target(self,pacman):
        direc_x,direc_y = pacman.direccion
        pos_x , pox_y = pacman.posicion

        target_x = pos_x + direc_x * 4
        target_y = pos_y + direc_y * 4

        return (target_x, target_y)
