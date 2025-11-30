"""UNO game management module."""

import random

from config import INITIAL_HAND_SIZE
from .card import Card
from .deck import Deck
from .player import Player
from .rules import Rules


class Game:
    """Manages the UNO game state and logic."""
    def __init__(self, players: list[Player]):
        self.deck = Deck()
        self.players = players
        self.turn = -1   # counterclockwise is positively increasing, and default clockwise
        self.reverse = False
        self.draw = 0

        for player in self.players:
            player.draw(self.deck, INITIAL_HAND_SIZE)

        while (top := self.deck.draw_pile.pop()).sort == 'draw_four':
            self.deck.draw_pile.insert(
                random.choice(range(len(self.deck.draw_pile))),
                top
            )

        Rules.apply_special_effects(top, self)
        self.deck.discard_pile.append(top)
        self.turn += self.reverse
        self.player = self.players[self.turn]   # the first player

    def play_card(self, player: Player, card: Card) -> bool:
        """
        Attempt to play a card from a player's hand.

        Args:
            player: The player attempting to play the card
            card: The card to play

        Returns:
            True if the card was successfully played, False otherwise
        """
        if is_valid := Rules.is_valid_play(card, self):
            Rules.apply_special_effects(card, self)
            player.discard(self.deck, card)
        return is_valid
