from turtle import Screen

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

        ¿Que hace este metodo?
        Cuando en el archivo principal escribimos "Renderer(pantalla)", este metodo
        se ejecuta automaticamente y guarda todas las herramientas que el dibujante
        va a necesitar despues: sobre que pantalla pintar, de que tamaño es cada
        casillero, que colores usar y con que letra escribir.

        Recordemos que "self" es el identificador de ESTE dibujante en particular,
        asi sus herramientas no se mezclan con las de otro objeto.

        Parametros:
        - pantalla: La superficie de PyGame donde vamos a dibujar. Se crea en el
          archivo principal con "pygame.display.set_mode()" y se nos pasa aca para
          que el Renderer sepa sobre que "lienzo" tiene que pintar.
        - tamano_tile (int): Cuantos pixeles mide el lado de cada casillero.
          Por defecto vale 20. Si lo agrandamos, todo el juego se ve mas grande.

        Atributos de instancia (el "equipamiento" del dibujante):

        - self.pantalla: Guardamos la pantalla recibida para poder usarla en TODOS
          los demas metodos sin tener que pasarla una y otra vez.
        - self.tile: El tamaño del casillero. Es el numero MAGICO que nos permite
          convertir casilleros en pixeles (columna * tile = pixel en x).
        - self.colores: Un diccionario de colores en formato RGB. Lo armamos como
          diccionario para no andar escribiendo numeros sueltos tipo (255,255,0)
          por todos lados. Asi pedimos el color por su NOMBRE ("amarillo") y queda
          mucho mas legible y facil de cambiar.
        - self.fuente: El objeto tipografia para escribir texto en pantalla.
          pygame.font.SysFont(None, 30) agarra una letra del sistema de tamaño 30.
        """
        # Guardamos la pantalla y el tamaño de casillero para usarlos en todos lados
        self.pantalla = pantalla
        self.tile = tamano_tile

        # Diccionario de colores RGB. Pedimos los colores por nombre para que el
        # codigo sea legible. -> Cada color es una tupla (Rojo, Verde, Azul) de 0 a 255.
        self.colores = {
            "negro":     (0, 0, 0),         # fondo del juego
            "amarillo":  (255, 255, 0),     # Pac-Man
            "azul":      (33, 33, 222),      # paredes del laberinto
            "blanco":    (255, 255, 255),    # textos y bolitas (dots)
            "rosa":      (255, 184, 222),    # power pellets / fantasma Pinky
            "rojo":      (222, 0, 0),        # fantasma Blinky
            "celeste":   (0, 222, 222),      # fantasma Inky
            "naranja":   (222, 138, 0)       # fantasma Clyde
        }

        # La tipografia para escribir textos (puntaje, vidas, "GAME OVER", etc).
        # -> El "None" significa "usa la letra por defecto del sistema". El 30 es el tamaño.
        self.fuente = pygame.font.SysFont(None, 30)

    def limpiar_pantalla(self):
        """
        Pinta toda la pantalla de negro para "borrar" el frame anterior.

        ¿Por que necesitamos esto?
        Recordemos como funciona un juego: la pantalla se redibuja entera 60 veces
        por segundo. Si NO borraramos lo anterior, Pac-Man dejaria un rastro de
        copias suyas por toda la pantalla (como un fantasma de si mismo en cada
        posicion donde estuvo). Por eso, ANTES de dibujar nada nuevo, pintamos todo
        de negro y empezamos de cero, como una pizarra que se borra cada frame.

        Este metodo deberia ser SIEMPRE lo primero que se llama en cada frame,
        antes de dibujar el mapa, Pac-Man o los fantasmas.
        """
        # "fill" rellena toda la superficie con un color de un saque.
        self.pantalla.fill(self.colores["negro"])

    def dibujar_mapa(self, mapa):
        """
        Dibuja el laberinto completo: las paredes, las bolitas (dots) y los
        power pellets (las bolitas grandes).

        ¿Como entendemos el mapa?
        El mapa que nos pasa el Integrante 1 es una grilla (una lista de listas).
        Es como una tabla de Excel: filas y columnas. Cada celda de esa tabla
        guarda una letra que nos dice QUE hay en ese casillero:
            - "X" = una pared (la dibujamos como un cuadrado azul).
            - "." = una bolita chica / dot (vale 10 puntos al comerla).
            - "o" = una bolita grande / power pellet (vale 50 y asusta fantasmas).
            - " " = un espacio vacio (no dibujamos nada).

        ¿Como convertimos casilleros en pixeles? (¡La parte clave!)
        Recorremos la grilla con dos "for" anidados: uno para las filas y otro
        para las columnas. Para cada casillero hacemos la traduccion magica:
            - pixel_x = columna * self.tile
            - pixel_y = fila    * self.tile
        Por ejemplo, si un casillero esta en la columna 3 y el tile mide 20px,
        entonces en la pantalla va dibujado en x = 3 * 20 = 60 pixeles.
        Asi es como pasamos del "mundo de casilleros" al "mundo de pixeles".

        Parametros:
        - mapa: La grilla del laberinto (lista de listas de caracteres) que nos
          provee la clase Map del Integrante 1.

        ACLARACION para la integracion: por ahora suponemos que "mapa" es una
        lista de listas de letras. Cuando el Integrante 1 termine su clase Map,
        quizas tengamos que pedirle los datos con algun metodo (ej: mapa.get_grilla()).
        Eso lo coordinamos llegado el momento, la logica de dibujo no cambia.
        """
        # Recorremos fila por fila. enumerate nos da el numero de fila Y su contenido.
        # -> "indice_fila" es el numero (0, 1, 2...) y "fila" es la lista de letras.
        for indice_fila, fila in enumerate(mapa):

            # Y dentro de cada fila, recorremos columna por columna.
            for indice_col, casillero in enumerate(fila):

                # LA TRADUCCION: de casillero (fila, columna) a pixeles (x, y).
                x = indice_col * self.tile
                y = indice_fila * self.tile

                # Segun que letra haya en el casillero, dibujamos una cosa u otra.
                if casillero == "X":
                    # Pared: un cuadrado azul del tamaño del tile.
                    # -> pygame.Rect(x, y, ancho, alto) define el rectangulo a pintar.
                    pared = pygame.Rect(x, y, self.tile, self.tile)
                    pygame.draw.rect(self.pantalla, self.colores["azul"], pared)

                elif casillero == ".":
                    # Dot (bolita chica): un circulito blanco en el CENTRO del casillero.
                    # -> Por eso sumamos "self.tile // 2": para correr el centro del
                    #    circulo a la mitad del casillero y que no quede pegado a la esquina.
                    centro_x = x + self.tile // 2
                    centro_y = y + self.tile // 2
                    pygame.draw.circle(self.pantalla, self.colores["blanco"], (centro_x, centro_y), 3)

                elif casillero == "o":
                    # Power pellet (bolita grande): igual que el dot pero con mas radio.
                    centro_x = x + self.tile // 2
                    centro_y = y + self.tile // 2
                    pygame.draw.circle(self.pantalla, self.colores["blanco"], (centro_x, centro_y), 7)

    def dibujar_pacman(self, pacman):
        """
        Dibuja a Pac-Man en pantalla.

        ¿Por que es tan cortito este metodo?
        Porque Pac-Man YA sabe dibujarse a si mismo. En su propia clase tiene un
        metodo "dibujar" que hace toda la magia de la boca animada y la rotacion.
        Entonces, el Renderer simplemente le DELEGA esa tarea: le pasa la pantalla
        y le dice "dibujate vos". Esto es una buena practica, no repetimos codigo
        que ya existe en otro lado.

        Parametros:
        - pacman: El objeto PacMan que queremos dibujar. Tiene que tener su propio
          metodo .dibujar(pantalla) (que ya programamos en pacman.py).
        """
        # Le delegamos el dibujo al propio Pac-Man, pasandole nuestra pantalla.
        pacman.dibujar(self.pantalla)

    def dibujar_fantasmas(self, fantasmas):
        """
        Dibuja a todos los fantasmas que esten activos en la partida.

        Misma idea que con Pac-Man: cada fantasma sabe dibujarse a si mismo (lo
        programan los Integrantes 3 y 4). Nosotros solo recorremos la lista de
        fantasmas y a cada uno le decimos "dibujate".

        ¿Por que un "for"?
        Porque en el juego hay 4 fantasmas activos a la vez. En vez de escribir la
        misma linea 4 veces, recorremos la lista con un for y se la aplicamos a
        todos. Si mañana fueran 6 fantasmas, este codigo funcionaria igual sin tocar nada.

        Parametros:
        - fantasmas: Una lista con los objetos fantasma activos. Cada uno tiene que
          tener su metodo .dibujar(pantalla).
        """
        # Recorremos la lista y le pedimos a cada fantasma que se dibuje.
        for fantasma in fantasmas:
            fantasma.dibujar(self.pantalla)

    def dibujar_hud(self, puntaje, high_score, vidas, nivel):
        """
        Dibuja el HUD: la informacion de la partida en pantalla (puntaje, high
        score, vidas y nivel).

        ¿Que es el HUD?
        HUD significa "Heads-Up Display". Es toda la info que se le muestra al
        jugador SIN ser parte del laberinto en si: el puntaje arriba, las vidas
        que le quedan, el record, etc. Es la "interfaz" del juego.

        ¿Como se escribe texto en PyGame?
        PyGame no escribe texto directo en la pantalla. Hay que seguir 2 pasos:
            1. "Renderizar" el texto: convertimos las palabras en una imagen
               (una superficie) con self.fuente.render(). Le pasamos el texto,
               un True (para que la letra se vea suavizada/antialiased) y el color.
            2. "Pegar" esa imagen en la pantalla con self.pantalla.blit(), diciendole
               en que coordenada (x, y) la queremos.
        El metodo "blit" es basicamente copiar una imagen encima de otra.

        Parametros:
        - puntaje (int): Los puntos actuales del jugador.
        - high_score (int): El record historico guardado.
        - vidas (int): Cuantas vidas le quedan a Pac-Man.
        - nivel (int): En que nivel va la partida.
        """
        # 1) Creamos las imagenes de texto (las "renderizamos").
        # -> render(texto, suavizado, color). El f"..." nos deja meter variables
        #    adentro del texto facilmente (f-string).
        texto_puntaje = self.fuente.render(f"Puntaje: {puntaje}", True, self.colores["blanco"])
        texto_record  = self.fuente.render(f"Record: {high_score}", True, self.colores["blanco"])
        texto_nivel   = self.fuente.render(f"Nivel: {nivel}", True, self.colores["blanco"])
        texto_vidas   = self.fuente.render(f"Vidas: {vidas}", True, self.colores["blanco"])

        # 2) Pegamos cada imagen en la pantalla en su posicion (x, y).
        # -> Las coordenadas las elegimos nosotros para acomodar el HUD a gusto.
        self.pantalla.blit(texto_puntaje, (10, 10))
        self.pantalla.blit(texto_record,  (250, 10))
        self.pantalla.blit(texto_nivel,   (480, 10))
        self.pantalla.blit(texto_vidas,   (650, 10))

    def dibujar_pantalla_inicio(self):
        """
        Dibuja la pantalla de inicio (lo primero que ve el jugador al abrir el juego).

        Muestra el titulo del juego y un mensaje del tipo "Presiona ENTER para
        empezar". Esta pantalla se muestra ANTES de que arranque la partida.

        Detalle tecnico: para centrar el texto usamos ".get_rect(center=(x, y))".
        Esto nos da un rectangulo del tamaño del texto, y le decimos que su CENTRO
        este en el punto que queremos. Asi el texto queda centrado de verdad y no
        corrido hacia un lado. Es mas prolijo que calcular la posicion a mano.
        """
        # Primero limpiamos para que no quede nada del frame anterior.
        self.limpiar_pantalla()

        # Averiguamos el centro de la pantalla. -> get_size() nos da (ancho, alto).
        ancho, alto = self.pantalla.get_size()
        centro_x = ancho // 2

        # Creamos los textos.
        titulo = self.fuente.render("PAC-MAN", True, self.colores["amarillo"])
        instruccion = self.fuente.render("Presiona ENTER para empezar", True, self.colores["blanco"])

        # Los centramos horizontalmente usando get_rect(center=...).
        rect_titulo = titulo.get_rect(center=(centro_x, alto // 2 - 40))
        rect_instr  = instruccion.get_rect(center=(centro_x, alto // 2 + 20))

        # Y los pegamos en pantalla en su rectangulo ya centrado.
        self.pantalla.blit(titulo, rect_titulo)
        self.pantalla.blit(instruccion, rect_instr)

    def dibujar_game_over(self, puntaje):
        """
        Dibuja la pantalla de "GAME OVER" cuando el jugador pierde sus 3 vidas.

        Muestra el cartel de fin de juego y el puntaje final que logro el jugador.
        Usa la misma tecnica de centrado que la pantalla de inicio.

        Parametros:
        - puntaje (int): El puntaje final con el que termino la partida, para
          mostrarselo al jugador.
        """
        # Limpiamos la pantalla.
        self.limpiar_pantalla()

        # Buscamos el centro.
        ancho, alto = self.pantalla.get_size()
        centro_x = ancho // 2

        # Creamos los textos: el cartel grande en rojo y el puntaje final en blanco.
        texto_go = self.fuente.render("GAME OVER", True, self.colores["rojo"])
        texto_pts = self.fuente.render(f"Puntaje final: {puntaje}", True, self.colores["blanco"])

        # Los centramos.
        rect_go  = texto_go.get_rect(center=(centro_x, alto // 2 - 30))
        rect_pts = texto_pts.get_rect(center=(centro_x, alto // 2 + 20))

        # Los pegamos en pantalla.
        self.pantalla.blit(texto_go, rect_go)
        self.pantalla.blit(texto_pts, rect_pts)
    def actualizar_pantalla(self):
        """
        Muestra en la ventana todo lo que dibujamos durante este frame.

        ¿Por que existe este metodo y por que va AL FINAL de cada frame?
        PyGame trabaja con "doble buffer": todo lo que dibujamos (mapa, Pac-Man,
        fantasmas...) en realidad se dibuja en una pantalla "oculta", detras de
        escena. El jugador todavia NO ve nada de eso. Recien cuando llamamos a
        "pygame.display.flip()" se muestra TODO de un saque.

        ¿Que ganamos con esto? Evitamos el parpadeo. Si mostraramos cada cosa a
        medida que la dibujamos, el jugador veria el dibujo "armandose" a pedazos.
        Asi, en cambio, ve cada frame ya completo y terminado.

        Por eso este metodo es SIEMPRE lo ultimo que se llama en cada vuelta del
        game loop, despues de haber dibujado absolutamente todo.
        """
        pygame.display.flip()
        


#Pantalla de inicio

def pantalla_de_inicio():
    Screen.fill(0,0,0)
    
    color_texto = (255, 255, 0)
    fuente = pygame.font.SysFont(None, 50)
    