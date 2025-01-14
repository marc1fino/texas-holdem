import random

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value}{self.suit}"

    def to_dict(self):
        """Convierte el objeto Card en un diccionario."""
        return {"value": self.value, "suit": self.suit}


class Deck:
    def __init__(self):
        suits = ['C', 'D', 'H', 'S']  # Palos: tréboles, diamantes, corazones, picas
        values = list(range(2, 15))  # Valores: 2-10, J=11, Q=12, K=13, A=14
        self.cards = [Card(value, suit) for suit in suits for value in values]
        random.shuffle(self.cards)

    def deal(self, count):
        """Devuelve una lista con `count` cartas del mazo."""
        return [self.cards.pop() for _ in range(count)]
