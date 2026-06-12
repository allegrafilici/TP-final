import pygame as py


imagen_pacman = open("assets/pacman.png")

class pacman:
    def __init__(self, posicion_inicial):
        self.posicion = posicion_inicial
        self.direccion = (1, 0)
        self.proxima_direccion = (1, 0)
        
        imagen_original = py.image.load("assets/pacman.png").convert_alpha()
        self.imagen = py.transform.scale(imagen_original, (24, 24))

    def movimiento(self):
        columna, fila = self.posicion
        x, y = self.direccion
        self.posicion = (columna + x, fila + y)

    def cambiar_direccion(self, nueva_direccion):
        #registramos el movimiento pero sin realizarlo
        self.proxima_direccion = nueva_direccion