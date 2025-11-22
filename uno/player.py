from . import Card, Deck


class Player:
    """Represents a player in the UNO game."""

    def __init__(self, name: str):
        """
        Initialize a player.

        Args:
            name: Player's name
        """
        self.name = name
        self.hand: list[Card] = []
        self.score = 0  # Other players' hand cards when losing can be added here with a certain weight.

    def draw(self, deck: Deck, num: int = 1):
        """
        Draw cards from the deck to the player's hand.

        Args:
            deck: The game deck
            num: Number of cards to draw (default: 1)
        """
        self.hand.extend(deck.draw(num))

    def discard(self, deck: Deck, card: Card):
        """
        Discard a card from the player's hand to the discard pile.

        Args:
            deck: The game deck
            card: The card to discard
        """
        self.hand.remove(card)
        deck.discard(card)