"""Module defining the rules of the UNO game."""

from typing import TYPE_CHECKING

from .constants import BLACK_COLOR
from .card import Card
from .player import Player

if TYPE_CHECKING:
    from .game import Game


class Rules:
    """Defines the rules and logic of the UNO game."""

    @staticmethod
    def is_valid_play(card: Card, game: 'Game'):
        """Check if a card can be played on top of the current discard pile."""

        top = game.deck.discard_pile[-1]
        if card.color == BLACK_COLOR:
            return True
        elif card.color == top.color or (card.type == top.type and card.value == top.value):
            return True
        else:
            return False

    @staticmethod
    def is_able_to_play(player: Player, game: 'Game'):
        """Check if the player is able to play any card."""

        return any(Rules.is_valid_play(card, game) for card in player.hand)

    @staticmethod
    def apply_special_effects(card: Card, game: 'Game'):
        """Apply the special effects of a card to the game state."""

        if card.type == 'skip':
            game.turn += 1 if game.reverse else -1
        elif card.type == 'reverse':
            if len(game.players) == 2:
                game.turn -= 1
            else:
                game.reverse = not game.reverse
        elif card.type == 'draw_two':
            game.draw += 2
        elif card.type == 'draw_four':
            game.draw += 4

    @staticmethod
    def is_winner(player: Player):
        """Check if the player has won the game."""

        return not player.hand

    @staticmethod
    def score(game: 'Game'):
        """Calculate the total score of all players' hands in the game."""

        return sum(sum(card.value for card in player.hand) for player in game.players)
