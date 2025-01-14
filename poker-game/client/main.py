import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client.poker_game import PokerGame
from shared.cards import Deck

WIDTH, HEIGHT = 1280, 720

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Texas Hold'em Poker")
    client_host = "127.0.0.1"  # Cambiar según el servidor
    client_port = 12345

    game = PokerGame(screen, client_host, client_port)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key_input(event)

        game.update()
        game.draw()
        pygame.time.Clock().tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

