"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
import os
import random
import sys

if sys.platform != "linux":
    # El core activa el driver "dummy" si no existe DISPLAY (solo existe en Linux).
    os.environ.setdefault("DISPLAY", ":0")

from arkanoid_core import *
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""

    # - Comprueba que `self.level_path` existe y es fichero.
    if not self.level_path.is_file():
        raise FileNotFoundError(f"El nivel no existe: {self.level_path}")
    
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    texto = self.level_path.read_text(encoding="utf-8")
    lineas = [linea.strip() for linea in texto.splitlines()]
    lineas_limpias = [linea for linea in lineas if linea != ""]

    if not lineas_limpias:
        raise ValueError("El archivo de nivel está vacío.")
    
    ancho_referencia = len(lineas_limpias[0])
    for linea in lineas_limpias:
        if len(linea) != ancho_referencia:
            raise ValueError("Todas las filas del nivel deben tener la misma longitud.")
        
    # - Guarda el resultado en `self.layout` y devuélvelo.
    self.layout = lineas_limpias
    return self.layout

@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""

    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    ancho, alto = self.PADDLE_SIZE
    self.paddle = self.crear_rect(0, 0, ancho, alto)
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.PADDLE_OFFSET)

    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    self.score = 0
    self.lives = 3
    self.end_message = ""

    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.reiniciar_bola((random.choice((-1, 1)), -1))

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""

    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()

    # - Recorre `self.layout` para detectar símbolos de bloque.
    for fila, linea in enumerate(self.layout):
        for columna, simbolo in enumerate(linea):
            if simbolo not in self.BLOCK_COLORS:
                continue

    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
            self.blocks.append(self.calcular_posicion_bloque(fila, columna))
            self.block_colors.append(self.BLOCK_COLORS[simbolo])
            self.block_symbols.append(simbolo)

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""

    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    teclas = self.obtener_estado_teclas()

    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    if teclas[self.KEY_LEFT] or teclas[self.KEY_A]:
        self.paddle.x -= self.PADDLE_SPEED
    if teclas[self.KEY_RIGHT] or teclas[self.KEY_D]:
        self.paddle.x += self.PADDLE_SPEED

    # - Limita la posición para que no salga de la pantalla.
    if self.paddle.left < 0:
        self.paddle.left = 0

    if self.paddle.right > self.SCREEN_WIDTH:
        self.paddle.right = self.SCREEN_WIDTH

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""

    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    self.ball_pos += self.ball_velocity

    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    radio = self.BALL_RADIUS

    if self.ball_pos.x - radio <= 0:
        self.ball_pos.x = radio
        self.ball_velocity.x = abs(self.ball_velocity.x)

    if self.ball_pos.x + radio >= self.SCREEN_WIDTH:
        self.ball_pos.x = self.SCREEN_WIDTH - radio
        self.ball_velocity.x = -abs(self.ball_velocity.x)

    if self.ball_pos.y - radio <= 0:
        self.ball_pos.y = radio
        self.ball_velocity.y = abs(self.ball_velocity.y)

    ball_rect = self.obtener_rect_bola()

    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        desplazamiento = (self.ball_pos.x - self.paddle.centerx) / (self.paddle.width / 2)
        desplazamiento = max(-1.0, min(1.0, desplazamiento))

        direccion = Vector2(desplazamiento, -1)
        self.ball_velocity = direccion.normalize() * self.BALL_SPEED
        self.ball_pos.y = self.paddle.top - radio - 1

    for i, bloque in enumerate(self.blocks):
        if ball_rect.colliderect(bloque):
            solape_x = min(ball_rect.right, bloque.right) - max(ball_rect.left, bloque.left)
            solape_y = min(ball_rect.bottom, bloque.bottom) - max(ball_rect.top, bloque.top)

            if solape_x < solape_y:
                self.ball_velocity.x *= -1
            else:
                self.ball_velocity.y *= -1

            simbolo = self.block_symbols[i]
            self.score += self.BLOCK_POINTS.get(simbolo, 0)

            self.blocks.pop(i)
            self.block_colors.pop(i)
            self.block_symbols.pop(i)
            break

    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.
    if not self.blocks:
        self.running = False
        self.end_message = "¡VICTORIA!"
        return

    if self.ball_pos.y - radio > self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives > 0:
            self.reiniciar_bola((random.choice((-1, 1)), -1))
        else:
            self.running = False
            self.end_message = "GAME OVER"

@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""

    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    if not self.screen:
        return
    
    self.screen.fill(self.BACKGROUND_COLOR)

    for bloque, color in zip(self.blocks, self.block_colors):
        self.dibujar_rectangulo(bloque, color)

    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)

    centro_bola = (int(self.ball_pos.x), int(self.ball_pos.y))
    self.dibujar_circulo(centro_bola, self.BALL_RADIUS, self.BALL_COLOR)

    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    self.dibujar_texto(f"Puntos: {self.score}", (16, 16))
    self.dibujar_texto(f"Vidas: {self.lives}", (self.SCREEN_WIDTH - 120, 16))

    if self.end_message:
        self.dibujar_texto(self.end_message, (self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2), grande=True)

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""

    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    self.inicializar_pygame()

    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()

    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    self.running = True

    while self.running:
        for evento in self.iterar_eventos():
            if evento.type == self.EVENT_QUIT:
                self.running = False
            elif evento.type == self.EVENT_KEYDOWN:
                if evento.key == self.KEY_ESCAPE:
                    self.running = False

        if self.running:
            self.procesar_input()
            self.actualizar_bola()
            self.dibujar_escena()
            self.actualizar_pantalla()

            if self.clock:
                self.clock.tick(self.FPS)

    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.
    if self.end_message:
        self.dibujar_escena()
        self.actualizar_pantalla()
        self.esperar(2000)

    self.finalizar_pygame()

def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()
