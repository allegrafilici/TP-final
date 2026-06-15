import pygame as py

class Fantasma:
    def __init__(self, nombre, direccion, posicion, modo, vida, ruta_imagen):
        self.nombre           = nombre
        self.direccion        = direccion
        self.posicion         = posicion
        self.modo             = modo
        self.posicion_inicial = posicion
        self.vida             = vida

        imagen_original = py.image.load(ruta_imagen).convert_alpha()
        self.imagen     = py.transform.scale(imagen_original, (24, 24))

        self.frame_actual        = 0
        self.contador_animacion  = 0
        self.velocidad_animacion = 5
        self.animaciones         = self.cargar_animaciones(nombre, ruta_imagen)

        self.parpadeando        = False
        self.oculto             = False
        self.apareciendo        = False
        self.progreso_aparicion = 0.0

        # acumulador: tiempo acumulado desde el ultimo movimiento.
        # main.py lo incrementa con dt y cuando supera el paso de este
        # fantasma (que depende de modo y posicion), el fantasma se mueve.
        self.acumulador = 0.0

        # esquina_scatter: tile objetivo cuando el fantasma esta en modo scatter.
        # Se asigna desde main.py segun la eleccion del jugador en la pantalla
        # de seleccion. Por defecto apunta a la esquina superior izquierda.
        self.esquina_scatter = (1, 1)

    def cargar_imagen(self, ruta):
        imagen = py.image.load(ruta).convert_alpha()
        return py.transform.scale(imagen, (24, 24))

    def cargar_animaciones(self, nombre, ruta_imagen):
        imagen_base = self.cargar_imagen(ruta_imagen)
        animaciones = {
            "derecha":   [imagen_base, imagen_base],
            "izquierda": [imagen_base, imagen_base],
            "arriba":    [imagen_base, imagen_base],
            "abajo":     [imagen_base, imagen_base],
            "asustado": [
                self.cargar_imagen("assets/sprites/asustado/asustado1.png"),
                self.cargar_imagen("assets/sprites/asustado/asustado2.png"),
            ],
        }
        rutas = {
            "Blinky": {"carpeta": "assets/sprites/blinky",
                       "derecha": ["derehabli.png","derehabli2.png"],
                       "izquierda": ["izquierdabli.png","izquierdabli2.png"],
                       "arriba": ["arribabli.png","arribabli2.png"],
                       "abajo": ["abajobli.png","abajobli2.png"]},
            "Pinky":  {"carpeta": "assets/sprites/pinky",
                       "derecha": ["derechapi.png","derechapi2.png"],
                       "izquierda": ["izquierdapi.png","izquierdapi2.png"],
                       "arriba": ["arribapi.png","arribapi2.png"],
                       "abajo": ["abajopi.png","abajopi2.png"]},
            "Inky":   {"carpeta": "assets/sprites/inky",
                       "derecha": ["derechaink.png","derechaink2.png"],
                       "izquierda": ["izquierdainky.png","izquierdainky2.png"],
                       "arriba": ["arribainky.png","arribainky2.png"],
                       "abajo": ["abajoinky.png","abajoinky2.png"]},
            "Clyde":  {"carpeta": "assets/sprites/clyde",
                       "derecha": ["derechacly.png","derechacly2.png"],
                       "izquierda": ["izquierdacly.png","izquierdacly2.png"],
                       "arriba": ["arribacly.png","arribacly2.png"],
                       "abajo": ["abajocly.png","abajocly2.png"]},
        }
        if nombre in rutas:
            datos   = rutas[nombre]
            carpeta = datos["carpeta"]
            for dir in ["derecha", "izquierda", "arriba", "abajo"]:
                animaciones[dir] = [
                    self.cargar_imagen(f"{carpeta}/{datos[dir][0]}"),
                    self.cargar_imagen(f"{carpeta}/{datos[dir][1]}"),
                ]
        return animaciones

    def movimiento(self, limite_columnas=None):
        col, fila = self.posicion
        nueva_col = col + self.direccion[0]
        if limite_columnas is not None:
            nueva_col %= limite_columnas
        self.posicion = (nueva_col, fila + self.direccion[1])
        self.actualizar_animacion()

    def cambiar_direccion(self, nueva_direccion):
        self.direccion = nueva_direccion

    def invertir_direccion(self):
        """
        Invierte la direccion actual del fantasma (da la vuelta).

        En el Pac-Man original, los fantasmas invierten su direccion
        inmediatamente cada vez que cambian de modo (scatter → chase
        o chase → scatter). Esto se logra negando dx y dy:
            derecha (1,0)  → izquierda (-1,0)
            arriba  (0,-1) → abajo     (0,1)
        """
        self.direccion = (-self.direccion[0], -self.direccion[1])

    def cambiar_modo(self, modo_nuevo):
        self.modo            = modo_nuevo
        self.frame_actual    = 0
        self.contador_animacion = 0
        self.parpadeando     = False

    def reiniciar(self):
        """Reseteo completo: posicion, modo, estado visual y acumulador."""
        self.posicion           = self.posicion_inicial
        self.modo               = "scatter"
        self.frame_actual       = 0
        self.parpadeando        = False
        self.oculto             = False
        self.apareciendo        = False
        self.progreso_aparicion = 0.0
        self.acumulador         = 0.0

    def reiniciar_posicion(self):
        self.posicion = self.posicion_inicial

    def obtener_direccion_texto(self):
        if self.direccion == (1,  0): return "derecha"
        if self.direccion == (-1, 0): return "izquierda"
        if self.direccion == (0, -1): return "arriba"
        if self.direccion == (0,  1): return "abajo"
        return "derecha"

    def actualizar_animacion(self):
        self.contador_animacion += 1
        if self.contador_animacion >= self.velocidad_animacion:
            self.contador_animacion = 0
            self.frame_actual = (self.frame_actual + 1) % 2

    def decidir_direccion(self, pacman, blinky=None):
        if self.nombre == "Inky":
            target_x, target_y = self.elegir_target(pacman, blinky)
        else:
            target_x, target_y = self.elegir_target(pacman)
        fx, fy = self.posicion
        if   target_x > fx: self.direccion = (1,  0)
        elif target_x < fx: self.direccion = (-1, 0)
        elif target_y > fy: self.direccion = (0,  1)
        elif target_y < fy: self.direccion = (0, -1)

    def elegir_target(self, pacman, blinky=None):
        pass

    def _dibujar_aparicion(self, pantalla, tamano_tile):
        escala        = 1.0 - (1.0 - self.progreso_aparicion) ** 2
        tamano_actual = max(2, int(24 * escala))
        dir_texto     = self.obtener_direccion_texto()
        imagen        = self.animaciones[dir_texto][self.frame_actual]
        imagen_sc     = py.transform.scale(imagen, (tamano_actual, tamano_actual))
        cx = self.posicion[0] * tamano_tile + tamano_tile // 2
        cy = self.posicion[1] * tamano_tile + tamano_tile // 2
        pantalla.blit(imagen_sc, (cx - tamano_actual // 2, cy - tamano_actual // 2))

    def dibujar(self, pantalla, tamano_tile=20):
        if self.oculto:
            return
        if self.apareciendo:
            self._dibujar_aparicion(pantalla, tamano_tile)
            return
        x = self.posicion[0] * tamano_tile + 3
        y = self.posicion[1] * tamano_tile + 3
        if self.modo == "asustado":
            if self.parpadeando:
                fase = (py.time.get_ticks() // 250) % 2
                if fase == 0:
                    cx = self.posicion[0] * tamano_tile + tamano_tile // 2
                    cy = self.posicion[1] * tamano_tile + tamano_tile // 2
                    py.draw.circle(pantalla, (255, 255, 255), (cx, cy), tamano_tile // 2 - 1)
                    return
            imagen = self.animaciones["asustado"][self.frame_actual]
            pantalla.blit(imagen, (x, y))
        else:
            dir_texto = self.obtener_direccion_texto()
            imagen    = self.animaciones[dir_texto][self.frame_actual]
            pantalla.blit(imagen, (x, y))


class ScoreManager:
    def __init__(self):
        self.puntaje = 0
        try:
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
        self.vidas = 3
        self.nivel = 1

    def sumar_puntaje(self, cantidad):
        self.puntaje += cantidad
        if self.puntaje > self.high_score:
            self.high_score = self.puntaje
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))

    def restar_vidas(self):
        self.vidas -= 1

    def sumar_vidas(self):
        self.vidas += 1