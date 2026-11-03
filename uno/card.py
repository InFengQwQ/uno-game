from enum import StrEnum

__all__ = [
    'CardColor', 'CardSort',
    'COLORS',
    'ACTIONS', 'WILDS',
    'Card'
]


class CardColor(StrEnum):
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'
    PURPLE = 'purple'
    BLACK = 'black'

class CardSort(StrEnum):
    NUMBER = 'number'
    DRAW_2 = 'draw_2'
    REVERSE = 'reverse'
    SKIP = 'skip'
    WILD = 'wild'
    WILD_DRAW_4 = 'wild_draw_4'

COLORS = tuple(
    color for color in CardColor
    if color is not CardColor.BLACK
)

ACTIONS = (CardSort.DRAW_2, CardSort.REVERSE, CardSort.SKIP)
WILDS = (CardSort.WILD, CardSort.WILD_DRAW_4)


class Card:
    """Number/action/wild sort card.

    Attributes:
        color: Card color (four and "black").
        sort: Card sort (wilds, actions, or "number").
        value: Card value (score value).
    """
    def __init__(self, color: CardColor, sort: CardSort, value: int):
        self.color = color
        self.sort = sort
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self) -> str:
        if self.sort == CardSort.NUMBER:
            assert self.color in COLORS
            return f'{self.color}_{self.value}'
        elif self.sort in ACTIONS:
            return f'{self.color}_{self.sort}'

        assert self.sort in WILDS
        return self.sort

    @property
    def is_pending(self) -> bool:
        """Whether the card needs a color choice."""
        return self.color == CardColor.BLACK
