import pygame


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

        ¿Como se escribe texto en PyGame?
            1. Renderizar: convertimos el texto en una imagen con fuente.render().
            2. Pegar (blit): copiamos esa imagen en la pantalla en la posicion deseada.
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
        Muestra el titulo y un mensaje para presionar ENTER.
        """
        self.limpiar_pantalla()

        ancho, alto = self.pantalla.get_size()
        centro_x    = ancho // 2

        titulo      = self.fuente.render("PAC-MAN", True, self.colores["amarillo"])
        instruccion = self.fuente.render("Presiona ENTER para empezar", True, self.colores["blanco"])

        rect_titulo = titulo.get_rect(center=(centro_x, alto // 2 - 40))
        rect_instr  = instruccion.get_rect(center=(centro_x, alto // 2 + 20))

        self.pantalla.blit(titulo, rect_titulo)
        self.pantalla.blit(instruccion, rect_instr)

    def dibujar_game_over(self, puntaje, alpha=255):
        """
        Dibuja la pantalla de GAME OVER con efecto de fade in.

        ¿Que es el parametro alpha?
            Alpha controla la OPACIDAD de cada texto:
                0   → completamente transparente (invisible)
                128 → 50% transparente (semitransparente)
                255 → completamente opaco (se ve normal)

            main.py calcula y pasa este valor segun cuanto tiempo paso
            desde que empezo el estado "game_over". Al principio es 0
            (nada se ve) y sube hasta 255 a medida que pasan los segundos.

        ¿Como se aplica la transparencia en PyGame?
            No podemos aplicar alpha directamente sobre la pantalla.
            Hay que hacerlo sobre la SURFACE del texto:
                1. Renderizamos el texto → obtenemos una Surface
                2. Llamamos a surface.set_alpha(alpha) → le ponemos la opacidad
                3. Hacemos blit → la pegamos en pantalla con esa opacidad

            Sin el set_alpha(), el texto siempre aparece 100% opaco de golpe.

        Parametros:
            puntaje : int   → el puntaje final a mostrar.
            alpha   : int   → opacidad del texto, de 0 (invisible) a 255 (opaco).
                              Por defecto es 255 para mantener compatibilidad.
        """
        # La pantalla ya esta negra (la dejo la cortina). No hacemos limpiar_pantalla()
        # porque eso pisaria el negro que vino del estado "cortina".

        ancho, alto = self.pantalla.get_size()
        centro_x    = ancho // 2

        # Renderizamos los textos
        texto_go  = self.fuente.render("GAME OVER", True, self.colores["rojo"])
        texto_pts = self.fuente.render(f"Puntaje final: {puntaje}", True, self.colores["blanco"])

        # Aplicamos la opacidad a cada superficie de texto.
        # Esto es lo que crea el efecto de fade: al principio alpha=0 (invisible)
        # y va subiendo hasta alpha=255 (totalmente visible).
        texto_go.set_alpha(alpha)
        texto_pts.set_alpha(alpha)

        # Centramos los textos en la pantalla
        rect_go  = texto_go.get_rect(center=(centro_x, alto // 2 - 30))
        rect_pts = texto_pts.get_rect(center=(centro_x, alto // 2 + 20))

        self.pantalla.blit(texto_go,  rect_go)
        self.pantalla.blit(texto_pts, rect_pts)

    def actualizar_pantalla(self):
        """
        Muestra en la ventana todo lo dibujado en este frame.

        PyGame usa doble buffer: dibujamos en una pantalla oculta y recien
        con flip() lo mostramos todo junto. Esto evita el parpadeo.
        Siempre va al final del loop, despues de dibujar todo.
        """
        pygame.display.flip()