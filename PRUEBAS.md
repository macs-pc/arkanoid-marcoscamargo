# Comprobaciones visibles de M2

Comprueba cada método antes de continuar con el siguiente:

# nivel válido y nivel inexistente;
Resultado: CORRECTO.

Al ejecutar python arkanoid_game.py niveles/demo.txt, la cuadrícula se carga correctamente y se construyen las entidades sin errores.

Al ejecutar con una ruta no existente (python arkanoid_game.py niveles/no_existe.txt), el método cargar_nivel() intercepta la ausencia del fichero y lanza la excepción FileNotFoundError con el mensaje informativo correspondiente, evitando que el programa falle de forma inesperada.

# nivel con filas de distinta longitud;
Resultado: CORRECTO.

Se probó con un archivo de nivel modificado intencionadamente para contener filas con diferente número de caracteres.

El método cargar_nivel() validó la longitud de cada línea respecto a la primera y lanzó la excepción ValueError ("Todas las filas del nivel deben tener la misma longitud"), impidiendo que se inicie el juego con una cuadrícula malformada.

# paleta en ambos límites de la pantalla;
Resultado: CORRECTO.

Desplazando la paleta hacia la izquierda con las teclas Izquierda o A, la posición se detiene exactamente en el margen paddle.left == 0.

Desplazando la paleta hacia la derecha con las teclas Derecha o D, la posición se detiene exactamente en paddle.right == SCREEN_WIDTH (800 px). La paleta no traspasa los bordes en ningún momento.

# rebote contra pared, paleta y cada tipo de bloque;
Resultado: CORRECTO.

Paredes y Techo: La bola invierte correctamente su velocidad en el eje correspondiente al colisionar con los bordes laterales y el borde superior.

Paleta: Al colisionar con la paleta, la velocidad vertical se invierte hacia arriba (y < 0) y la velocidad horizontal (x) se ajusta según la distancia del impacto respecto al centro de la paleta, permitiendo controlar el ángulo de disparo.

Bloques: Al impactar cualquier bloque, este es eliminado inmediatamente de las tres listas paralelas (blocks, block_colors, block_symbols), la bola invierte su dirección vertical y se suma la puntuación correspondiente según el símbolo:

[ # (Bloque estándar): 50 puntos. ]
[ @ (Bloque reforzado): 75 puntos. ]
[ % (Bloque bonus): 120 puntos. ]

# pérdida de una vida y reinicio de la bola;
Resultado: CORRECTO.

Cuando la posición de la bola supera la parte inferior de la pantalla (ball_pos.y - BALL_RADIUS > SCREEN_HEIGHT), la variable self.lives se decrementa en 1 unidad.

Se invoca automáticamente self.reiniciar_bola(), recolocando la bola sobre el centro de la paleta con la velocidad inicial restablecida para continuar la partida.

# victoria al eliminar el último bloque y derrota al agotar vidas;
Resultado: CORRECTO.

Victoria: Al destruir el último bloque disponible (len(self.blocks) == 0), el bucle principal finaliza la iteración, establece self.end_message = "¡VICTORIA!", renderiza el texto en el centro de la pantalla durante 2000 ms y cierra la aplicación limpiamente.

Derrota: Al perder la última vida (lives == 0), el juego asigna self.end_message = "GAME OVER", muestra el mensaje en pantalla durante 2 segundos y finaliza sin errores de ejecución.

# salida limpia con Escape y al cerrar la ventana.
Resultado: CORRECTO.

Al pulsar la tecla Escape (KEY_ESCAPE) o hacer clic en el botón de cierre de la ventana (EVENT_QUIT), la variable self.running pasa a False.

El programa sale del bucle while, ejecuta self.finalizar_pygame() para liberar la memoria y los recursos de Pygame, y retorna el control a la consola sin dejar procesos secundarios colgados ni lanzar excepciones de cierre.

Una mejora opcional no debe romper ninguno de estos casos.
