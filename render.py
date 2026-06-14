import pygame
import math


class Renderer:
    """
    Es la clase encargada de DIBUJAR absolutamente todo lo visual del juego.

    Pensemos al Renderer como "el dibujante" o "el pintor" del juego. Ninguna otra
    clase deberia tocar la pantalla directamente, todo lo visual pasa por aca.
    Esto se hace asi a proposito y tiene nombre: "separacion de responsabilidades".
    La idea es que cada clase tenga UN solo trabajo:
        - PacMan se encarga de moverse y saber donde esta.
        - Los fantasmas se encargan de perseguir.
        - El Renderer se encarga UNICAMENTE de dibujar.

    ¿Que ventaja tiene esto? Si el dia de mañana queremos cambiar los colores del
    juego, el tamaño de la letra del puntaje o como se ve el laberinto, tocamos
    UN solo archivo (este) y no andamos rompiendo el codigo de los demas integrantes.

    Concepto clave: TILES (casilleros)
    El mapa del juego NO se piensa en pixeles sueltos, sino en una grilla de
    casilleros cuadrados llamados "tiles". El mapa de Pac-Man es una grilla de
    28 tiles de ancho por 31 de alto. Cada tile mide, por ejemplo, 20x20 pixeles.
    El trabajo del Renderer es TRADUCIR esos casilleros (fila, columna) a pixeles
    (x, y) reales en la pantalla para poder dibujarlos.

    Los atributos principales son:
        pantalla: La superficie de PyGame (la ventana) sobre la que dibujamos todo.
        tile (int): El tamaño en pixeles de cada casillero del mapa (20x20).
        colores (dict): Un diccionario con los colores RGB que usa el juego.
        fuente (Font): La tipografia que usamos para escribir textos (puntaje, etc).
    """

    def __init__(self, pantalla, tamano_tile=20):
        """
        Metodo constructor (__init__): Prepara al "dibujante" antes de que el
        juego empiece a correr.
        """
        self.pantalla = pantalla
        self.tile     = tamano_tile

        self.colores = {
            "negro":    (0, 0, 0),
            "amarillo": (255, 255, 0),
            "azul":     (33, 33, 222),
            "blanco":   (255, 255, 255),
            "rosa":     (255, 184, 222),
            "rojo":     (222, 0, 0),
            "celeste":  (0, 222, 222),
            "naranja":  (222, 138, 0)
        }

        self.fuente = pygame.font.SysFont(None, 30)

    def limpiar_pantalla(self):
        """Pinta toda la pantalla de negro para borrar el frame anterior."""
        self.pantalla.fill(self.colores["negro"])

    def dibujar_mapa(self, mapa):
        """
        Dibuja el laberinto completo: paredes, bolitas y power pellets.

        Recorre la grilla fila por fila y columna por columna.
        Convierte cada casillero a pixeles: x = columna * tile, y = fila * tile.
        Segun el caracter del casillero dibuja una pared, dot o power pellet.
        """
        for indice_fila, fila in enumerate(mapa):
            for indice_col, casillero in enumerate(fila):

                x = indice_col * self.tile
                y = indice_fila * self.tile

                if casillero == "X":
                    pared = pygame.Rect(x, y, self.tile, self.tile)
                    pygame.draw.rect(self.pantalla, self.colores["azul"], pared)

                elif casillero == ".":
                    centro_x = x + self.tile // 2
                    centro_y = y + self.tile // 2
                    pygame.draw.circle(self.pantalla, self.colores["blanco"], (centro_x, centro_y), 3)

                elif casillero == "o":
                    centro_x = x + self.tile // 2
                    centro_y = y + self.tile // 2
                    pygame.draw.circle(self.pantalla, self.colores["blanco"], (centro_x, centro_y), 7)

    def dibujar_pacman(self, pacman):
        """Delega el dibujo al propio Pac-Man, pasandole nuestra pantalla."""
        pacman.dibujar(self.pantalla)

    def dibujar_fantasmas(self, fantasmas):
        """Recorre la lista de fantasmas y le pide a cada uno que se dibuje."""
        for fantasma in fantasmas:
            fantasma.dibujar(self.pantalla)

    def dibujar_hud(self, puntaje, high_score, vidas, nivel):
        """
        Dibuja el HUD: puntaje, record, vidas y nivel en la parte superior.
        """
        texto_puntaje = self.fuente.render(f"Puntaje: {puntaje}", True, self.colores["blanco"])
        texto_record  = self.fuente.render(f"Record: {high_score}", True, self.colores["blanco"])
        texto_nivel   = self.fuente.render(f"Nivel: {nivel}", True, self.colores["blanco"])
        texto_vidas   = self.fuente.render(f"Vidas: {vidas}", True, self.colores["blanco"])

        self.pantalla.blit(texto_puntaje, (10, 10))
        self.pantalla.blit(texto_record,  (250, 10))
        self.pantalla.blit(texto_nivel,   (480, 10))
        self.pantalla.blit(texto_vidas,   (650, 10))

    def dibujar_pantalla_inicio(self):
        """
        Dibuja la pantalla de inicio antes de que arranque la partida.
        Muestra el titulo y un mensaje animado para presionar ENTER.
        """
        self.limpiar_pantalla()

        ancho, alto = self.pantalla.get_size()
        centro_x    = ancho // 2

        fuente_titulo = pygame.font.SysFont(None, 48)
        fuente_sub = pygame.font.SysFont(None, 28)

        titulo = fuente_titulo.render("PAC-MAN - LOS 4 FANTASTICOS", True, self.colores["amarillo"])
        
        # Efecto de parpadeo suave para el texto de presionar ENTER
        tiempo = pygame.time.get_ticks()
        alpha_pulso = int(255 * abs(math.sin(tiempo * 0.002)))
        
        instruccion = fuente_sub.render("PRESIONA ENTER PARA CONTINUAR", True, self.colores["blanco"])
        instruccion.set_alpha(max(50, alpha_pulso)) # Nunca desaparece del todo

        rect_titulo = titulo.get_rect(center=(centro_x, alto // 2 - 40))
        rect_instr  = instruccion.get_rect(center=(centro_x, alto // 2 + 20))

        self.pantalla.blit(titulo, rect_titulo)
        self.pantalla.blit(instruccion, rect_instr)

    def dibujar_pantalla_seleccion(self, esquinas_nombres, esquina_actual_idx, fantasmas_info, asignados):
        """
        Dibuja la pantalla de seleccion con tarjetas animadas, bordes redondeados
        y un sistema de iluminacion dinamica tipo LED al pasar el mouse.
        """
        self.limpiar_pantalla()
        ancho, alto = self.pantalla.get_size()
        
        fuente_tit = pygame.font.SysFont(None, 38)
        fuente_txt = pygame.font.SysFont(None, 24)
        fuente_etiqueta = pygame.font.SysFont(None, 20)
        
        # Variable de tiempo para animaciones fluidas (ondas senoidales)
        tiempo = pygame.time.get_ticks()
        pulso = (math.sin(tiempo * 0.005) + 1) / 2  # Oscila suavemente entre 0.0 y 1.0
        
        # Instrucción superior
        esquina_texto = esquinas_nombres[esquina_actual_idx] if esquina_actual_idx < 4 else "¡Listo!"
        txt_titulo = fuente_tit.render(f"Asignar esquina: {esquina_texto}", True, self.colores["celeste"])
        self.pantalla.blit(txt_titulo, (ancho // 2 - txt_titulo.get_width() // 2, 35))
        
        txt_ayuda = fuente_txt.render("Hace clic sobre un fantasma para asignarlo", True, (180, 180, 180))
        self.pantalla.blit(txt_ayuda, (ancho // 2 - txt_ayuda.get_width() // 2, 75))
        
        # Posición del mouse para efectos Hover
        pos_mouse = pygame.mouse.get_pos()
        
        # Dibujar las tarjetas para cada uno de los 6 fantasmas
        for nombre, info in fantasmas_info.items():
            rect_base = info["rect"]
            color_fantasma = info["color"]
            
            ya_asignado = nombre in asignados
            en_hover = rect_base.collidepoint(pos_mouse)
            
            # --- LÓGICA DE ANIMACIÓN DE LA TARJETA ---
            if en_hover and not ya_asignado:
                # La tarjeta "salta" hacia adelante (se agranda un poquito)
                offset = 4
                rect_dibujo = rect_base.inflate(offset * 2, offset * 2)
                
                # Brillo de neón calculando la interpolación hacia el blanco
                r = min(255, color_fantasma[0] + int(100 * pulso))
                g = min(255, color_fantasma[1] + int(100 * pulso))
                b = min(255, color_fantasma[2] + int(100 * pulso))
                color_borde = (r, g, b)
                
                grosor_borde = 3
                fondo_tarjeta = (40, 40, 45)
            else:
                rect_dibujo = rect_base.copy()
                fondo_tarjeta = (25, 25, 28)
                if ya_asignado:
                    color_borde = (40, 40, 40)
                    grosor_borde = 2
                else:
                    color_borde = (80, 80, 80)
                    grosor_borde = 2
                    
            # Dibujamos el fondo y el borde con esquinas redondeadas (border_radius)
            pygame.draw.rect(self.pantalla, fondo_tarjeta, rect_dibujo, border_radius=12)
            pygame.draw.rect(self.pantalla, color_borde, rect_dibujo, width=grosor_borde, border_radius=12)
            
            # --- DIBUJO DEL ICONO (ESFERA) ---
            centro_icono = (rect_dibujo.x + 35, rect_dibujo.y + rect_dibujo.height // 2)
            
            if ya_asignado:
                # Si está asignado, lo apagamos (escala de grises oscura)
                color_esfera = (color_fantasma[0]//4, color_fantasma[1]//4, color_fantasma[2]//4)
                radio = 12
            else:
                color_esfera = color_fantasma
                radio = 14 if en_hover else 12

            pygame.draw.circle(self.pantalla, color_esfera, centro_icono, radio)
            
            # Brillo superior para darle volumen 3D a la esfera (si no está asignado)
            if not ya_asignado:
                pygame.draw.circle(self.pantalla, (255, 255, 255), (centro_icono[0] - 4, centro_icono[1] - 4), radio // 3)
            
            # --- TEXTOS ---
            color_texto = self.colores["blanco"] if not ya_asignado else (100, 100, 100)
            texto_nombre = fuente_txt.render(nombre, True, color_texto)
            
            # Ajustamos la posición vertical del nombre dependiendo de si hay subtítulo
            pos_y_texto = rect_dibujo.y + 12 if ya_asignado else rect_dibujo.y + (rect_dibujo.height // 2) - 8
            self.pantalla.blit(texto_nombre, (rect_dibujo.x + 65, pos_y_texto))
            
            # Mostrar etiqueta de confirmación si ya fue elegido
            if ya_asignado:
                lbl_esq = fuente_etiqueta.render(f"Fijo: {asignados[nombre]}", True, (0, 200, 100))
                self.pantalla.blit(lbl_esq, (rect_dibujo.x + 65, rect_dibujo.y + 32))

    def dibujar_game_over(self, puntaje, alpha=255):
        """
        Dibuja la pantalla de GAME OVER con efecto de fade in.
        """
        ancho, alto = self.pantalla.get_size()
        centro_x    = ancho // 2

        texto_go  = self.fuente.render("GAME OVER", True, self.colores["rojo"])
        texto_pts = self.fuente.render(f"Puntaje final: {puntaje}", True, self.colores["blanco"])

        texto_go.set_alpha(alpha)
        texto_pts.set_alpha(alpha)

        rect_go  = texto_go.get_rect(center=(centro_x, alto // 2 - 30))
        rect_pts = texto_pts.get_rect(center=(centro_x, alto // 2 + 20))

        self.pantalla.blit(texto_go,  rect_go)
        self.pantalla.blit(texto_pts, rect_pts)

    def actualizar_pantalla(self):
        """
        Muestra en la ventana todo lo dibujado en este frame.
        """
        pygame.display.flip()