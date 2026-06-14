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
        self.frame_actual = 0 #decide si estas usando la imagen 1 0 la 2 
        self.contador_animacion = 0 
        self.velocidad_animacion = 5 #cada cuantos moviemientos cambia de sprite
        self.animaciones = self.cargar_animaciones(nombre, ruta_imagen) #diccionario donde guardamos imagenes por direcion

    def cargar_imagen(self,ruta):
        imagen = py.image.load(ruta).convert_alpha()
        return py.transform.scale(imagen, (24, 24))
        #carga una imagen desde una ruta y la escala al tamaño de los fantasmas

    def cargar_animaciones(self, nombre, ruta_imagen):
        """
        Carga las animaciones del fantasma según su nombre.

        Cada dirección tiene dos sprites:
            - derecha: imagen 1 e imagen 2
            - izquierda: imagen 1 e imagen 2
            - arriba: imagen 1 e imagen 2
            - abajo: imagen 1 e imagen 2

        También carga el modo asustado.

        Si algo falla o un fantasma no tiene sprites, usa la imagen original
        como respaldo para que el juego no se rompa.
        """
        imagen_base = self.cargar_imagen(ruta_imagen)

        animaciones = {
            "derecha": [imagen_base, imagen_base],
            "izquierda": [imagen_base, imagen_base],
            "arriba": [imagen_base, imagen_base],
            "abajo": [imagen_base, imagen_base],
            "asustado": [
                self.cargar_imagen("assets/sprites/asustado/asustado1.png"),
                self.cargar_imagen("assets/sprites/asustado/asustado2.png"),
            ],
        }

        rutas_por_fantasma = {
            "Blinky": {
                "carpeta": "assets/sprites/blinky",
                "derecha": ["derehabli.png", "derehabli2.png"],
                "izquierda": ["izquierdabli.png", "izquierdabli2.png"],
                "arriba": ["arribabli.png", "arribabli2.png"],
                "abajo": ["abajobli.png", "abajobli2.png"],
            },
            "Pinky": {
                "carpeta": "assets/sprites/pinky",
                "derecha": ["derechapi.png", "derechapi2.png"],
                "izquierda": ["izquierdapi.png", "izquierdapi2.png"],
                "arriba": ["arribapi.png", "arribapi2.png"],
                "abajo": ["abajopi.png", "abajopi2.png"],
            },
            "Inky": {
                "carpeta": "assets/sprites/inky",
                "derecha": ["derechaink.png", "derechaink2.png"],
                "izquierda": ["izquierdainky.png", "izquierdainky2.png"],
                "arriba": ["arribainky.png", "arribainky2.png"],
                "abajo": ["abajoinky.png", "abajoinky2.png"],
            },
            "Clyde": {
                "carpeta": "assets/sprites/clyde",
                "derecha": ["derechacly.png", "derechacly2.png"],
                "izquierda": ["izquierdacly.png", "izquierdacly2.png"],
                "arriba": ["arribacly.png", "arribacly2.png"],
                "abajo": ["abajocly.png", "abajocly2.png"],
            },
        }

        if nombre in rutas_por_fantasma:
            datos = rutas_por_fantasma[nombre]
            carpeta = datos["carpeta"]

            for direccion in ["derecha", "izquierda", "arriba", "abajo"]:
                archivo1 = datos[direccion][0]
                archivo2 = datos[direccion][1]

                animaciones[direccion] = [
                    self.cargar_imagen(f"{carpeta}/{archivo1}"),
                    self.cargar_imagen(f"{carpeta}/{archivo2}"),
                ]

        return animaciones

    
  
    def movimiento(self):
        """
    cada vez que se mueve cambia entre la imagen 1 e imagen 2 
    """
        columna, fila = self.posicion
        self.posicion = (columna + self.direccion[0], fila + self.direccion[1])
        self.actualizar_animacion()

    def cambiar_direccion(self, nueva_direccion):
        self.direccion = nueva_direccion

    def cambiar_modo(self, modo_nuevo):
        self.modo = modo_nuevo
        self.frame_actual = 0
        self.contador_animacion = 0

    def obtener_direccion_texto(self):
        """
        Convierte la dirección del fantasma en texto para elegir el sprite correcto.
        """
        if self.direccion == (1, 0):
            return "derecha"
        elif self.direccion == (-1, 0):
            return "izquierda"
        elif self.direccion == (0, -1):
            return "arriba"
        elif self.direccion == (0, 1):
            return "abajo"
        return "derecha"

    def actualizar_animacion(self):
        self.contador_animacion += 1
        if self.contador_animacion >= self.velocidad_animacion:
            self.contador_animacion = 0
            self.frame_actual = (self.frame_actual + 1) % 2

    

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

    def dibujar(self, pantalla, tamano_tile=20):
        """
        Dibuja el fantasma en pantalla.

        Si está en modo asustado usa los sprites azules de la carpeta asustado.
        Si está en modo normal usa los sprites según la dirección actual.
        """
        x = self.posicion[0] * tamano_tile + 3
        y = self.posicion[1] * tamano_tile + 3

        if self.modo == "asustado":
            imagen = self.animaciones["asustado"][self.frame_actual]
        else:
            direccion = self.obtener_direccion_texto()
            imagen = self.animaciones[direccion][self.frame_actual]

        pantalla.blit(imagen, (x, y))

class ScoreManager:
    def __init__(self):
        self.puntaje = 0

        try:
            with open("highscore.txt", "r") as archivo:
                self.high_score = int(archivo.read())
        except:
            self.high_score = 0

        self.vidas = 3
        self.nivel = 1
    
    def sumar_puntaje(self, cantidad):
        self.puntaje += cantidad
        
        if self.puntaje > self.high_score:
            self.high_score = self.puntaje
            with open("highscore.txt", "w") as archivo:
                archivo.write(str(self.high_score))
        
    def restar_vidas(self):
        self.vidas -= 1

    def sumar_vidas(self):
        self.vidas += 1
