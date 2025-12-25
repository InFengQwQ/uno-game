"""UNO Deck Module"""

import random
from typing import Optional

from .constants import (
    COLORS, BLACK_COLOR,
    NUMBER, NUMBERS, NONZERO_NUMBERS,
    ACTIONS, ACTION_SCORE, WILDS, WILD_SCORE
)
from .card import Card


class Deck:
    """UNO Deck Class"""
    
    def __init__(self):
        """Initialize a standard UNO deck with all cards."""
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

    def _reshuffle(self) -> None:
        """Reshuffle discard pile into draw pile (keeping top card)."""
        self.draw_pile, self.discard_pile = self.discard_pile[:-1], self.discard_pile[-1:]

        for card in self.draw_pile:
            if card.sort in WILDS:
                card.color = BLACK_COLOR
        random.shuffle(self.draw_pile)

    def draw(self, num: int = 1) -> list[Card]:
        """Draw cards from draw pile.
        
        Args:
            num: Number of cards to draw (default: 1)
            
        Returns:
            List of drawn cards (may be fewer than requested if deck runs out)
        """
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

    def discard(self, card: Card) -> None:
        """Discard a card to the discard pile.
        
        Args:
            card: The card to discard
        """
        self.discard_pile.append(card)
    
    def get_top_discard(self) -> Optional[Card]:
        """Get the top card of the discard pile.
        
        Returns:
            The top card, or None if discard pile is empty
        """
        return self.discard_pile[-1] if self.discard_pile else None
    
    def is_empty(self) -> bool:
        """Check if both piles are empty.
        
        Returns:
            True if both draw and discard piles are empty
        """
        return not self.draw_pile and not self.discard_pile
