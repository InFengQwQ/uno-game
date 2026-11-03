from .card import Card

__all__ = ['Player']


class Player:
    """Player of a single game.

    Attributes:
        uno: Whether this player called UNO.
        name: Name of the player.
        score: Score accumulated.

        hand: The held card list.
    """
    def __init__(self, name: str):
        self.uno = False
        self.name = name
        self.score = 0.0
        # TODO: Optionally incorporate other players' remaining cards at game over
        # into this player's score using a configurable weight.

        self.hand: list[Card] = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.name == other.name
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def size(self) -> int:
        return len(self.hand)
