#pinky a diferencia de blinky busca la posicion adelantada de pacman
from fantasmas import Fantasma

class Pinky(Fantasma): #hereda de la clase padre de fantasma
    def __init__(self, direccion, posicion, modo):

        super().__init__(
            "Pinky",
            direccion,
            posicion,
            "Rosa",
            modo
        )

    def elegir_target(): #pinly tiene que predecir el movimenot del pacman y adelantrase para su proximo movieminento
        
        direc_x, direc_y = pacman.direccion #separamos la direcion del pacman
        pos_x, pos_y = pacman.posicion #separamos la posicion del pacman
        target_x = pos_x + direc_x * 4 #pinky se adelanta 4 casillas eb base al pacman (x)
        target_y = pos_y + direc_y * 4 #pinky se adelanta 4 casillas eb base al pacman (y)
        return (target_x, target_y)


#codigo prueba para probar los algoritmos 
# CLASE TEMPORAL SOLO PARA PROBAR
class PacmanPrueba:

    def __init__(self, posicion, direccion):

        self.posicion = posicion
        self.direccion = direccion


# PRUEBA
pacman = PacmanPrueba(
    (10, 5),   # posicion
    (1, 0)     # direccion → derecha
)

pinky1 = Pinky(
    (0, -1),
    (5, 5),
    "chase"
)

print(pinky1.nombre)

print("Posicion inicial:")
print(pinky1.posicion)

print("Target de Pinky:")
print(pinky1.elegir_target(pacman))

pinky1.decidir_direccion(pacman)
pinky1.movimiento()

print("Nueva posicion:")
print(pinky1.posicion)