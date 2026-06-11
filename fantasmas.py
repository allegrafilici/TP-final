class Fantasma:
    def __init__(self, nombre, direccion, posicion, color, modo, vida):
        self.nombre = nombre
        self.direccion = direccion
        self.posicion = posicion
        self.color = color
        self.modo = modo
        self.posicion_inicial = posicion
        self.vida = vida

    def movimiento(self):
        columna, fila = self.posicion
        x, y = self.direccion

        posicion_actual = (columna + x, fila + y)
        self.posicion = posicion_actual

    def cambiar_direccion(self, nueva_direccion):
        self.direccion = nueva_direccion

    def cambiar_modo(self, modo_nuevo):
        self.modo = modo_nuevo

    def reiniciar_posicion(self):
        self.posicion = self.posicion_inicial

    def decidir_direccion(self, pacman):
        target = self.elegir_target(pacman)
        target_x, target_y = target
        fantasma_x, fantasma_y = self.posicion
        if target_x > fantasma_x:
            self.direccion = (1, 0)
            
        elif target_x < fantasma_x:
            self.direccion = (-1, 0)
        elif target_y > fantasma_y:
            self.direccion = (0, 1)
        elif target_y < fantasma_y:
            self.direccion = (0, -1)

    def elegir_target(self, pacman):
        pass

    



    







    


    

    



        


