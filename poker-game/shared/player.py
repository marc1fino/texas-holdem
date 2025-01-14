class Player:
    def __init__(self, id, stack=1000):
        self.id = id
        self.stack = stack
        self.hand = []
        self.bet = 0
        self.all_in = False

    def place_bet(self, amount):
        if amount >= self.stack:
            self.all_in = True
            self.bet += self.stack
            self.stack = 0
        else:
            self.stack -= amount
            self.bet += amount

    def reset_bet(self):
        self.bet = 0
