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
    def is_valid_play(card: Card, game: 'Game') -> bool:
        """Check if a card can be played on top of the current discard pile."""
        top = game.deck.discard_pile[-1]
        return (
            card.color == BLACK_COLOR or
            card.color == top.color or
            card.sort == top.sort and card.value == top.value
        )

    @staticmethod
    def is_able_to_play(player: Player, game: 'Game') -> bool:
        """Check if the player is able to play any card."""
        return any(Rules.is_valid_play(card, game) for card in player.hand)

    @staticmethod
    def apply_special_effects(card: Card, game: 'Game'):
        """Apply the special effects of a card to the game state."""
        if card.sort == 'skip':
            game.turn += int(game.reverse)
        elif card.sort == 'reverse':
            if len(game.players) == 2:
                game.turn -= 1
            else:
                game.reverse = not game.reverse
        elif card.sort == 'draw_two':
            game.draw += 2
        elif card.sort == 'draw_four':
            game.draw += 4

    @staticmethod
    def is_winner(player: Player) -> bool:
        """Check if the player has won the game."""
        return not player.hand

    @staticmethod
    def score(game: 'Game') -> int:
        """Calculate the total score of all players' hands in the game."""
        return sum(
            sum(card.value for card in player.hand)
            for player in game.players
        )
