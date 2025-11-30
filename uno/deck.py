"""UNO Deck Module"""

import random

from .constants import (
    COLORS, BLACK_COLOR,
    NUMBER, NUMBERS, NONZERO_NUMBERS,
    ACTIONS, ACTION_SCORE, WILDS, WILD_SCORE
)
from .card import Card


class Deck:
    """UNO Deck Class"""
    def __init__(self):
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []

        for color in COLORS:
            for numbers in NUMBERS, NONZERO_NUMBERS:
                for value in numbers:
                    self.draw_pile.append(Card(color, NUMBER, value))
                for action in ACTIONS:
                    self.draw_pile.append(Card(color, action, ACTION_SCORE))
            for wild in WILDS:
                self.draw_pile.append(Card(BLACK_COLOR, wild, WILD_SCORE))
        random.shuffle(self.draw_pile)

    def _reshuffle(self):
        self.draw_pile, self.discard_pile = self.discard_pile[:-1], self.discard_pile[-1:]

        for card in self.draw_pile:
            if card.sort in WILDS:
                card.color = BLACK_COLOR
        random.shuffle(self.draw_pile)

    def draw(self, num: int = 1):
        """Draw Cards from Draw Pile"""
        cards: list[Card] = []
        for _ in range(num):
            try:
                if not self.draw_pile:
                    self._reshuffle()
            except IndexError:
                return cards
            else:
                cards.append(self.draw_pile.pop())
        return cards

    def discard(self, card: Card):
        """Discard Card to Discard Pile"""
        self.discard_pile.append(card)
