from .card import (
    WILDS,
    Card
)
from .player import *
from .game import *

__all__ = ['Rule']


class Rule:
    # Also use in the client, but host makes a sence
    @staticmethod
    def is_valid_play(card: Card, top: Card) -> bool:
        """If the card can be played."""
        return (
            (card.color == top.color) or
            (card.sort in WILDS) or
            (card.sort == top.sort and card.value == top.value)
        )

    # In the host
    @staticmethod
    def validplays(game: Game) -> list[Card]:
        """The cards the current player may play."""
        if game.to_draw < 0:
            return [
                card for card in game.player.hand[-1:]
                if Rule.is_valid_play(card, game.deck.top)
            ]
        if game.to_draw > 0:
            return []
        else:
            return [
                card for card in game.player.hand
                if Rule.is_valid_play(card, game.deck.top)
            ]

    @staticmethod
    def calculate_score(game: Game) -> dict[Player, int]:
        """Calculate score of each player."""
        total = sum(sum(
            card.value
            for card in player.hand)
            for player in game.players
        )
        return dict(zip(
            game.players,
            (total - sum(
                card.value
                for card in player.hand)
                for player in game.players
            )
        ))
