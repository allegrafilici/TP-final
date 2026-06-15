from fantasmas import Fantasma

class Pinky(Fantasma):
    def __init__(self, direccion, posicion, modo, vida):
        #el super manda a llamar al constructor de la clase padre
        super().__init__(
            "Pinky", 
            direccion, 
            posicion, 
            modo, 
            vida, 
            "assets/pinki.png"
        )
    
    def elegir_target(self, pacman):
        direc_x, direc_y = pacman.direccion
        pos_x, pos_y = pacman.posicion

        target_x = pos_x + direc_x * 4
        target_y = pos_y + direc_y * 4

        return (target_x, target_y)