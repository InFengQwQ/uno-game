"""Module defining the Card class for UNO game."""


class Card:
    """Represents a UNO card with color, sort, and value."""
    def __init__(self, color: str, sort: str, value: int):
        """
        Initialize a card.

        Args:
            color: Card color ("red", "green", "purple", "yellow", or "black")
            sort: Card sort (wilds, actions, or "number")
            value: Card value (score value)
        """
        self.color = color  # "Red" "Green" "Blue" "Yellow" or "Black"
        self.sort = sort    # wilds, actions or "Number"
        self.value = value  # value of score

    def __repr__(self) -> str:
        """Return a string representation of the card."""
        if self.value < 10:
            return f'Card({self.color}, {self.sort}, {self.value})'
        else:
            return f'Card({self.color}, {self.sort})'
