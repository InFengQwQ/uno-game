from collections import defaultdict, deque
from typing import cast

from uno import (
    CardColor, CardSort,
    Card, Player,
    Game
)

from .constants import InfoDict

__all__ = [
    'CardInfo', 'PlayerInfo',
    'Mirror'
]


class CardInfo(Card):
    """Card carried by messages.

    Attributes:
        color: Card color (four and "black").
        sort: Card sort (wilds, actions, or "number").
        value: Card value (score value).
    """

    def to_dict(self) -> InfoDict:
        """Convert to a info dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'CardInfo':
        """Convert from a info dictionary."""
        return CardInfo(
            CardColor(value['color']), CardSort(value['sort']),
            value['value']
        )

class PlayerInfo(Player):
    """PlayerInfo class for messages.

    Attributes:
        uno: Whether this player called UNO.
        name: Name of the player.
        score: Score accumulated.

        size: Number of its hand.
    """
    def __init__(self, uno: bool, name: str, score: float, size: int):
        self.uno = uno
        self.name = name
        self.score = score

        self._size = size

    @property
    def size(self) -> int:
        return self._size

    def to_dict(self) -> InfoDict:
        """Convert to a info dictionary."""
        return {
            'uno': self.uno,
            'name': self.name,
            'score': self.score,
            'size': self.size
        }

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'PlayerInfo':
        """Convert from a info dictionary."""
        return PlayerInfo(**value)


class Mirror:
    """Client-side mirror of visible game state.

    This object is UI-facing only. It does not run rules or own authoritative
    state. The host should send snapshots, and the client updates this mirror.
    """
    def __init__(self,
        players: list[PlayerInfo],
        player: PlayerInfo,
        hand: list[CardInfo],
        top: CardInfo,
        to_draw: int,
        reverse: bool
    ):
        self.players = players
        self.player = player
        self.hand = hand
        self.top = top
        self.to_draw = to_draw
        self.reverse = reverse

    def update(self, other: 'Mirror'):
        for key, value in vars(other).items():
            current = getattr(self, key)
            if isinstance(current, list):
                indexes: defaultdict[object, deque[object]] = defaultdict(deque)
                for old in cast(list[object], current):
                    indexes[old].append(old)

                targets: list[object] = []
                for new in cast(list[object], value):
                    if queue := indexes.get(new):
                        old = queue.popleft()
                        old.__dict__.update(new.__dict__)
                        targets.append(old)
                    else:
                        targets.append(new)

                cast(list[object], current)[:] = targets
                continue
            if isinstance(current, Player):
                current.__dict__.update(value.__dict__)
                continue
            if isinstance(current, Card):
                current.__dict__.update(value.__dict__)
                continue

            setattr(self, key, value)

    def to_dict(self) -> InfoDict:
        return {
            'players': [
                player.to_dict()
                for player in self.players
            ],
            'player': self.player.to_dict(),
            'hand': [
                card.to_dict()
                for card in self.hand
            ],
            'top': self.top.to_dict(),
            'to_draw': self.to_draw,
            'reverse': self.reverse
        }

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'Mirror':
        return Mirror(
            [
                PlayerInfo.from_dict(player)
                for player in value['players']
            ],
            PlayerInfo.from_dict(value['player']),
            [
                CardInfo.from_dict(card)
                for card in value['hand']
            ],
            CardInfo.from_dict(value['top']),
            value['to_draw'],
            value['reverse']
        )

    @classmethod
    def of(cls, game: Game, name: str) -> 'Mirror':
        target = next(player for player in game.players if player.name == name)
        player = game.player
        return Mirror(
            [
                PlayerInfo(
                    player.uno, player.name,
                    player.score, player.size
                )
                for player in game.players
            ],
            PlayerInfo(
                player.uno, player.name,
                player.score, player.size
            ),
            [
                CardInfo.from_dict(card.__dict__)
                for card in target.hand
            ],
            CardInfo.from_dict(game.deck.top.__dict__),
            game.to_draw,
            game.reverse
        )
