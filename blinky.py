from fantasmas import Fantasma


class Blinky(Fantasma):  # Blinky hereda de Fantasma

    def __init__(self, direccion, posicion, modo):

        super().__init__(
            "Blinky",
            direccion,
            posicion,
            "rojo",
            modo
        )

    def elegir_target(self, pacman):
        return pacman.posicion

    def decidir_direccion(self, pacman):
        target = self.elegir_target(pacman)

        target_x, target_y = target
        bli_x, bli_y = self.posicion

        if target_x > bli_x:
            self.direccion = (1, 0)   # derecha
        elif target_x < bli_x:
            self.direccion = (-1, 0)  # izquierda
        elif target_y > bli_y:
            self.direccion = (0, 1)   # abajo
        elif target_y < bli_y:
            self.direccion = (0, -1)  # arriba


# CLASE TEMPORAL SOLO PARA PROBAR
class PacmanPrueba:

    def __init__(self, posicion):
        self.posicion = posicion


# PRUEBA
pacman = PacmanPrueba((10, 5))

blinky1 = Blinky(
    (0, -1),
    (10, 5),
    "chase"
)

print(blinky1.nombre)

print("Posicion inicial:")
print(blinky1.posicion)

print("Target de Blinky:")
print(blinky1.elegir_target(pacman))

blinky1.decidir_direccion(pacman)
blinky1.movimiento()

print("Nueva posicion:")
print(blinky1.posicion)





 



    

