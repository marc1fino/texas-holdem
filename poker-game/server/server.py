import socket
import threading
import json
import time
from game.cards import Deck

class PokerServer:
    def __init__(self, host='0.0.0.0', port=12345, max_players=6):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(max_players)
        self.clients = {}
        self.players = {}
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.phase = "pre-flop"
        self.current_turn = 0
        self.lock = threading.Lock()

    def broadcast(self, message):
        """Envia un mensaje a todos los clientes."""
        for client in self.clients.values():
            client.sendall(json.dumps(message).encode())

    def handle_client(self, client, address):
        """Maneja cada conexión de cliente."""
        with self.lock:
            player_id = str(address)
            if player_id not in self.players:
                self.players[player_id] = {
                    "id": player_id,
                    "stack": 1000,
                    "hand": self.deck.deal(2),
                    "all_in": False,
                    "connected": True,
                }

        self.clients[player_id] = client
        self.send_player_state(client, player_id)

        try:
            while True:
                data = client.recv(1024).decode()
                if data:
                    message = json.loads(data)
                    self.process_message(message, player_id)
        except ConnectionResetError:
            print(f"Player {player_id} disconnected")
            self.players[player_id]["connected"] = False

    def send_player_state(self, client, player_id):
        """Envía el estado del juego al jugador."""
        client.sendall(json.dumps({
            "type": "state",
            "player_id": player_id,
            "players": list(self.players.values()),
            "community_cards": self.community_cards,
            "pot": self.pot,
            "phase": self.phase,
            "current_turn": self.current_turn,
        }).encode())

    def process_message(self, message, player_id):
        """Procesa los mensajes de los clientes."""
        if message["type"] == "bet":
            player = self.players[player_id]
            amount = message["amount"]

            if amount >= player["stack"]:  # All-In
                amount = player["stack"]
                player["all_in"] = True

            player["stack"] -= amount
            self.pot += amount
            self.broadcast({"type": "update", "players": list(self.players.values()), "pot": self.pot})

        if message["type"] == "next_phase":
            self.next_phase()

    def next_phase(self):
        """Avanza a la siguiente fase."""
        if self.phase == "pre-flop":
            self.community_cards = self.deck.deal(3)
            self.phase = "flop"
        elif self.phase == "flop":
            self.community_cards.append(self.deck.deal(1)[0])
            self.phase = "turn"
        elif self.phase == "turn":
            self.community_cards.append(self.deck.deal(1)[0])
            self.phase = "river"
        elif self.phase == "river":
            self.resolve_round()
            self.phase = "pre-flop"

        self.broadcast({"type": "phase_update", "community_cards": self.community_cards, "phase": self.phase})

    def resolve_round(self):
        """Resuelve la ronda y determina el ganador."""
        best_hands = []
        for player_id, player in self.players.items():
            all_cards = player["hand"] + self.community_cards
            best_hand = HandEvaluator.evaluate_hand(all_cards)
            best_hands.append((player_id, best_hand))

        winner = max(best_hands, key=lambda x: x[1])
        winning_player = self.players[winner[0]]
        winning_player["stack"] += self.pot
        self.pot = 0

        self.broadcast({
            "type": "winner",
            "winner_id": winner[0],
            "winning_hand": winner[1],
            "players": list(self.players.values())
        })

        self.restart_game()

    def restart_game(self):
        """Reinicia el juego para la siguiente ronda."""
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.phase = "pre-flop"
        for player in self.players.values():
            player["hand"] = self.deck.deal(2)

        self.broadcast({
            "type": "restart",
            "players": list(self.players.values()),
            "community_cards": self.community_cards
        })

    def start(self):
        """Inicia el servidor."""
        threading.Thread(target=self.turn_timer, daemon=True).start()
        print("Server started...")
        while True:
            client, address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def turn_timer(self):
        """Temporizador para manejar turnos automáticamente."""
        while True:
            time.sleep(30)
            self.current_turn = (self.current_turn + 1) % len(self.players)
            self.broadcast({"type": "turn_update", "current_turn": self.current_turn})


if __name__ == "__main__":
    server = PokerServer()
    server.start()
