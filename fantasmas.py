import pygame as py

class Fantasma:
    def __init__(self, nombre, direccion, posicion, modo, vida, ruta_imagen):
        self.nombre = nombre
        self.direccion = direccion
        self.posicion = posicion
        self.modo = modo
        self.posicion_inicial = posicion
        self.vida = vida
        
        
        imagen_original = py.image.load(ruta_imagen).convert_alpha()
        self.imagen = py.transform.scale(imagen_original, (24, 24))

    def movimiento(self):
        columna, fila = self.posicion
        self.posicion = (columna + self.direccion[0], fila + self.direccion[1])

    def cambiar_direccion(self, nueva_direccion):
        self.direccion = nueva_direccion

    def cambiar_modo(self, modo_nuevo):
        self.modo = modo_nuevo

    def reiniciar_posicion(self):
        self.posicion = self.posicion_inicial

    def decidir_direccion(self, pacman, blinky=None):
        if self.nombre == "Inky":
            target_x, target_y = self.elegir_target(pacman, blinky)
        else:
            target_x, target_y = self.elegir_target(pacman)
            
        fantasma_x, fantasma_y = self.posicion
        
        if target_x > fantasma_x: self.direccion = (1, 0)
        elif target_x < fantasma_x: self.direccion = (-1, 0)
        elif target_y > fantasma_y: self.direccion = (0, 1)
        elif target_y < fantasma_y: self.direccion = (0, -1)

    def elegir_target(self, pacman, blinky=None):
        pass


class ScoreManager:
    def __init__(self):
        self.puntaje = 0 
        self.high_score = 0 
        self.vidas = 3 
        self.nivel = 1
    
    def sumar_puntaje(self, cantidad):
        self.puntaje += cantidad #cantidad como variable provisoria
        
    def restar_vidas(self):
        self.vidas -= 1

    #el siguiente método solo puede llamarse 1 vez por partida(x la)
    def sumar_vidas(self):
        self.vidas += 1



    





