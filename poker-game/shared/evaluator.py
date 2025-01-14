from collections import Counter

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards):
        """Evalúa la mejor combinación posible en las 7 cartas."""
        values = sorted([card.value for card in cards], reverse=True)
        suits = [card.suit for card in cards]
        value_counts = Counter(values)

        # Clasificaciones
        is_flush = HandEvaluator.is_flush(cards)
        is_straight, straight_high = HandEvaluator.is_straight(values)
        counts = sorted(value_counts.values(), reverse=True)

        if is_flush and is_straight:
            return (9, straight_high)  # Straight Flush
        if counts[0] == 4:
            return (8, HandEvaluator.get_rank_by_count(value_counts, 4))  # Four of a Kind
        if counts[0] == 3 and counts[1] == 2:
            return (7, HandEvaluator.get_rank_by_count(value_counts, 3))  # Full House
        if is_flush:
            return (6, values)  # Flush
        if is_straight:
            return (5, straight_high)  # Straight
        if counts[0] == 3:
            return (4, HandEvaluator.get_rank_by_count(value_counts, 3))  # Three of a Kind
        if counts[0] == 2 and counts[1] == 2:
            return (3, HandEvaluator.get_rank_by_count(value_counts, 2, 2))  # Two Pair
        if counts[0] == 2:
            return (2, HandEvaluator.get_rank_by_count(value_counts, 2))  # One Pair
        return (1, values)  # High Card

    @staticmethod
    def is_flush(cards):
        suits = [card.suit for card in cards]
        suit_counts = Counter(suits)
        for suit, count in suit_counts.items():
            if count >= 5:
                return True
        return False

    @staticmethod
    def is_straight(values):
        """Detecta si hay una escalera en los valores."""
        unique_values = sorted(set(values), reverse=True)
        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i + 4] == 4:
                return True, unique_values[i]
        # Caso especial A-5
        if {14, 2, 3, 4, 5}.issubset(unique_values):
            return True, 5
        return False, None

    @staticmethod
    def get_rank_by_count(value_counts, count, secondary_count=None):
        """Obtiene el valor más alto de una combinación específica."""
        ranks = [value for value, cnt in value_counts.items() if cnt == count]
        if secondary_count:
            secondary_ranks = [value for value, cnt in value_counts.items() if cnt == secondary_count]
            return ranks + secondary_ranks
        return ranks
