import json
import socket
import pygame
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.cards import Deck
from shared.cards import Card
from client.chips import Chips
WIDTH, HEIGHT = 1280, 720

class PokerGame:
    def __init__(self, screen, host, port):
        self.screen = screen
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.chips = Chips(screen)
        self.players = []
        self.community_cards = []
        self.pot = 0
        self.current_turn = 0
        self.card_images = self.load_card_images()
        self.bet_input = ""
        self.buttons = self.create_buttons()

        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()
    def update(self):
        """Actualiza el estado del juego según los datos recibidos del servidor."""
        # La escucha del servidor ya está manejada en el hilo separado.
        # Aquí puedes procesar actualizaciones adicionales si es necesario.
        pass

    def load_card_images(self):
        suits = ['C', 'D', 'H', 'S']
        values = list(range(2, 15))
        card_images = {}

        for suit in suits:
            for value in values:
                card_name = f"{value}{suit}.png"
                card_path = os.path.join("assets", card_name)
                if os.path.exists(card_path):
                    card_images[f"{value}{suit}"] = pygame.image.load(card_path)
        back_path = os.path.join("assets", "back.png")
        if os.path.exists(back_path):
            card_images["back"] = pygame.image.load(back_path)

        return card_images

    def create_buttons(self):
        font = pygame.font.Font(None, 36)
        buttons = {
            "bet": self.create_button("Bet", font, (200, 600)),
            "check": self.create_button("Check", font, (400, 600)),
            "fold": self.create_button("Fold", font, (600, 600)),
        }
        return buttons

    def create_button(self, text, font, position):
        text_surface = font.render(text, True, (255, 255, 255))
        rect = text_surface.get_rect(center=position)
        return {"text": text_surface, "rect": rect, "action": text.lower()}

    def listen(self):
        while True:
            data = self.client.recv(1024).decode()
            if data:
                message = json.loads(data)
                self.handle_server_message(message)

    def handle_server_message(self, message):
        if message["type"] == "state":
            self.players = message["players"]
            self.community_cards = [
                Card(card["value"], card["suit"]) for card in message["community_cards"]
            ]
            self.pot = message["pot"]
            self.current_turn = message["current_turn"]
        elif message["type"] == "update":
            self.players = message["players"]
            self.pot = message["pot"]
        elif message["type"] == "phase_update":
            self.community_cards = [
                Card(card["value"], card["suit"]) for card in message["community_cards"]
            ]
        elif message["type"] == "winner":
            winner_id = message["winner_id"]
            print(f"Player {winner_id} wins with {message['winning_hand']}!")

    def handle_mouse_click(self, pos):
        for button in self.buttons.values():
            if button["rect"].collidepoint(pos):
                action = button["action"]
                if action == "bet" and self.bet_input.isdigit():
                    amount = int(self.bet_input)
                    self.client.send(json.dumps({"type": "bet", "amount": amount}).encode())
                    self.bet_input = ""
                elif action == "check":
                    self.client.send(json.dumps({"type": "next_phase"}).encode())
                elif action == "fold":
                    print("Player folded!")

    def handle_key_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.bet_input = self.bet_input[:-1]
        elif event.unicode.isdigit():
            self.bet_input += event.unicode

    def draw(self):
        self.screen.fill((34, 139, 34))
        font = pygame.font.Font(None, 36)

        self.chips.draw_chips(self.pot, WIDTH // 2 - 50, 80)
        
        # Dibujar fichas de cada jugador
        for i, player in enumerate(self.players):
            x, y = 100, 100 + i * 150
            self.chips.draw_chips(player["stack"], x, y)

        # Dibujar cartas comunitarias
        for i, card in enumerate(self.community_cards):
            card_key = f"{card['value']}{card['suit']}"
            card_image = self.card_images.get(card_key)
            if card_image:
                self.screen.blit(card_image, (400 + i * 60, 200))

        # Dibujar jugadores
        for i, player in enumerate(self.players):
            x, y = 100, 100 + i * 150
            color = (255, 215, 0) if i == self.current_turn else (255, 255, 255)
            player_surface = font.render(f"Player {i}: {player['stack']} chips", True, color)
            self.screen.blit(player_surface, (x, y))

        # Dibujar el pot
        pot_surface = font.render(f"Pot: {self.pot}", True, (255, 255, 255))
        self.screen.blit(pot_surface, (WIDTH // 2, 50))

        # Dibujar botones
        for button in self.buttons.values():
            pygame.draw.rect(self.screen, (0, 0, 0), button["rect"].inflate(20, 10), border_radius=5)
            self.screen.blit(button["text"], button["rect"])

        # Dibujar cuadro de entrada
        input_surface = font.render(f"Bet: {self.bet_input}", True, (255, 255, 255))
        self.screen.blit(input_surface, (200, 550))

        pygame.display.flip()
