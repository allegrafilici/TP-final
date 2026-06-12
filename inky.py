from fantasmas import Fantasma
        
class Inky(Fantasma):
    def __init__(self, direccion, posicion, modo, vida):
        
        super().__init__(
            "Inky", 
            direccion, 
            posicion, 
            modo, 
            vida, 
            "assets/inki.png"
        )

    def elegir_target(self, pacman, blinky):
        pac_x, pac_y = pacman.posicion
        direc_x, direc_y = pacman.direccion

        tile_adelantado_x = pac_x + direc_x * 2
        tile_adelantado_y = pac_y + direc_y * 2

        blinky_x, blinky_y = blinky.posicion

        vector_x = (tile_adelantado_x - blinky_x) * 2
        vector_y = (tile_adelantado_y - blinky_y) * 2

        target_x = blinky_x + vector_x
        target_y = blinky_y + vector_y

        return (target_x, target_y)




         
    

    
    


