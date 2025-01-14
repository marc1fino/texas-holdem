import pygame

class Chips:
    def __init__(self, screen):
        self.screen = screen
        self.colors = {
            "red": (255, 0, 0),       # Rojo para fichas de 10
            "green": (0, 255, 0),     # Verde para fichas de 50
            "blue": (0, 0, 255)       # Azul para fichas de 100
        }
        self.values = {
            "red": 10,
            "green": 50,
            "blue": 100
        }

    def draw_chips(self, amount, x, y):
        """Dibuja fichas gráficas basadas en la cantidad."""
        for color, value in self.values.items():
            count = amount // value  # Cantidad de fichas de este valor
            for i in range(count):
                pygame.draw.circle(
                    self.screen, 
                    self.colors[color], 
                    (x + i * 15, y), 10  # Posición con desplazamiento para cada ficha
                )
            amount %= value
