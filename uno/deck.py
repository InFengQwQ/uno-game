import random

from .card import *

__all__ = [
    'NUMBERS', 'NONZERO_NUMBERS',
    'ACTION_SCORE', 'WILD_SCORE',
    'Deck'
]


NUMBERS = range(10)
NONZERO_NUMBERS = NUMBERS[1:]

ACTION_SCORE = 20
WILD_SCORE = 50


class Deck:
    """Full 108-card deck.

    With a draw pile and a discard pile,
    draw/discard or reshuffle to manage.

    Attributes:
        draw_pile: List of cards to draw from.
        discard_pile: List of discarded cards.

        top: The top card.
    """
    def __init__(self):
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []

        for color in COLORS:
            for NUMBER_G in NUMBERS, NONZERO_NUMBERS:
                for value in NUMBER_G:
                    self.draw_pile.append(Card(color, CardSort.NUMBER, value))
                for action in ACTIONS:
                    self.draw_pile.append(Card(color, action, ACTION_SCORE))
            for wild in WILDS:
                self.draw_pile.append(Card(CardColor.BLACK, wild, WILD_SCORE))

        random.shuffle(self.draw_pile)

    @property
    def top(self) -> Card:
        """The top card."""
        return self.discard_pile[-1]

    def _reshuffle(self):
        self.draw_pile = self.discard_pile[:-1]
        self.discard_pile = self.discard_pile[-1:]
        for card in filter(lambda c: c.sort in WILDS,
            self.draw_pile
        ):
            card.color = CardColor.BLACK

        random.shuffle(self.draw_pile)

    def draw(self) -> Card | None:
        """Draw a card.

        If no cards in the draw pile, reshuffle.
        If no cards in either pile, return None.

        Returns:
            Drawn card.
        """
        if not self.draw_pile:
            self._reshuffle()
        try:
            return self.draw_pile.pop()
        except IndexError:
            return None
