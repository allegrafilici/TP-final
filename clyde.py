#logica de clyde seria si esta lejos lo persigue al pacman 
# si esta cerca se escapa  # para poder caluclar la distancia entre el pacman y clyde 
from fantasmas import Fantasma

class Clyde(Fantasma):
    def __init__(self, direccion, posicion, modo,vida):

        super().__init__(
            "Clyde",
            direccion,
            posicion,
            (255, 165, 0),
            modo,
            1
        )

    def elegir_target(self,pacman):
        pac_x, pac_y = pacman.posicion #separamos posicion pacman 
        cly_x, cly_y = self.posicion #separamos posicoin clyde
        distancia = ((pac_x - cly_x) ** 2 + ( pac_y - cly_y ) ** 2) ** 0.5
        #usaremos 8 como parametro de distancia para ver si esta lejos o cerca 

        if distancia > 8:
            return pacman.posicion #esta lejos para hacer que el pacman sea su tagret
        
        else: 
            return (0,0) # se escapa a una esquina si esta cerca del pacman 


