class Fantasma:
    def __init__(self, nombre, direccion, posicion, color, modo):
        self.nombre = nombre
        self.direccion = direccion
        self.posicion = posicion
        self.color = color
        self.modo = modo
        self.posicion_inicial = posicion

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

    def elegir_target(self, pacman):
        pass

    







    


    

    



        


