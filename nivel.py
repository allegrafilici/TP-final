"""
Este archivo detecta cuando el jugador completa el nivel y avanza al proximo.
 
El jugador empieza en el nivel 1 con el mapa lleno de puntos (.) y power pellets (o).
Cuando no queda ninguno, el nivel termina. El mapa se resetea, el numero de nivel
sube, y los fantasmas se mueven un poco mas rapido.
"""
 
 
def verificar_nivel_completo(mapa):
    """
    Revisa si el jugador comio todos los puntos del mapa.
 
    Recorre cada celda del tablero buscando "." o "o".
    En cuanto encuentra uno, para y devuelve False (nivel en curso).
    Si recorre todo sin encontrar ninguno, devuelve True (nivel completo).
 
    Parametros:
        mapa : Mapa
            El objeto Mapa que contiene mapa.grilla, mapa.filas y mapa.columnas.
 
    Retorna:
        True  = no quedan puntos = nivel completo
        False = hay al menos un punto sin comer = nivel en curso
    """
 
    # FOR EXTERIOR: recorre cada fila del mapa de arriba a abajo
    for fila in range(mapa.filas):
 
        # FOR INTERIOR: por cada fila, recorre cada columna de izquierda a derecha
        for columna in range(mapa.columnas):
 
            # Lee el contenido de la celda en esta posicion exacta
            tile = mapa.grilla[fila, columna]
 
            # Si encuentra un punto o power pellet, el nivel NO termino todavia
            # return False para inmediatamente, no tiene sentido seguir buscando
            if tile in [".", "o"]:
                return False
 
    # Recorrio TODO el mapa sin encontrar puntos: nivel completo
    return True
 
 
def subir_nivel(score_manager, mapa, tiempo_por_paso):
    """
    Ejecuta la transicion al siguiente nivel.
 
    Hace tres cosas:
        1. Sube el numero de nivel en ScoreManager.
        2. Resetea el mapa (vuelven todos los puntos al tablero).
        3. Aumenta la dificultad reduciendo tiempo_por_paso.
 
    ¿Que es tiempo_por_paso?
        En el loop principal (main.py), el juego avanza un "paso" cada cierta
        cantidad de segundos. Ese valor es tiempo_por_paso (arranca en 0.15 seg).
        Cuanto MAS CHICO, mas seguido avanza el juego = mas rapido = mas dificil.
 
        Progresion por nivel:
            Nivel 1 -> 0.15 seg por paso  (velocidad inicial)
            Nivel 2 -> 0.13 seg por paso  (un poco mas rapido)
            Nivel 3 -> 0.11 seg por paso
            Nivel 4 -> 0.09 seg por paso
            Nivel 5 -> 0.07 seg por paso
            Nivel 6 -> 0.05 seg por paso  (limite minimo, sigue siendo jugable)
 
    Parametros:
        score_manager : ScoreManager
            El objeto que lleva el puntaje, vidas y nivel actual.
 
        mapa : Mapa
            El objeto Mapa. Se usa para resetear la grilla con todos los puntos.
 
        tiempo_por_paso : float
            Cuantos segundos dura cada paso del juego. Arranca en 0.15.
 
    Retorna:
        float - El nuevo tiempo_por_paso, reducido en 0.02 segundos.
                Nunca baja de 0.05 para que el juego siga siendo jugable.
    """
 
    # Suma 1 al nivel actual. Si estabas en nivel 1, ahora vale 2.
    score_manager.nivel += 1
 
    # Lee el archivo mapa.txt desde cero y reconstruye la grilla completa.
    # Esto hace que vuelvan todos los "." y "o" al tablero.
    mapa.grilla = mapa.iniciar_mapa()
 
    # Reduce el tiempo entre pasos en 0.02 segundos (los fantasmas van mas rapido).
    # max(0.05, ...) asegura que nunca baje de 0.05 -> limite minimo de velocidad.
    #
    # Ejemplos:
    #   max(0.05, 0.15 - 0.02) -> max(0.05, 0.13) -> 0.13
    #   max(0.05, 0.07 - 0.02) -> max(0.05, 0.05) -> 0.05
    #   max(0.05, 0.06 - 0.02) -> max(0.05, 0.04) -> 0.05  (toca el limite)
    nuevo_tiempo = max(0.05, tiempo_por_paso - 0.02)
 
    # Devuelve el nuevo tiempo para que el loop principal lo use
    return nuevo_tiempo