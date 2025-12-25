"""Module representing a player in the UNO game."""

from typing import Optional
from .card import Card
from .deck import Deck


class Player:
    """Represents a player in the UNO game."""
    
    def __init__(self, name: str):
        """Initialize a player.
        
        Args:
            name: The player's name
        """
        self.name = name
        self.hand: list[Card] = []
        self.score = 0  # Other players' hand cards when losing can be added here with a certain weight.

    def draw(self, deck: Deck, num: int = 1) -> list[Card]:
        """
        Draw cards from the deck to the player's hand.

        Args:
            deck: The game deck
            num: Number of cards to draw (default: 1)
            
        Returns:
            List of cards drawn
        """
        cards = deck.draw(num)
        self.hand.extend(cards)
        return cards

    def discard(self, deck: Deck, card: Card) -> None:
        """
        Discard a card from the player's hand to the discard pile.

        Args:
            deck: The game deck
            card: The card to discard
            
        Raises:
            ValueError: If card is not in player's hand
        """
        if card not in self.hand:
            raise ValueError("Card not in player's hand")
        self.hand.remove(card)
        deck.discard(card)
    
    def has_card(self, card: Card) -> bool:
        """Check if player has a specific card.
        
        Args:
            card: The card to check for
            
        Returns:
            True if player has the card, False otherwise
        """
        return card in self.hand
    
    def get_hand_value(self) -> int:
        """Calculate the total value of cards in player's hand.
        
        Returns:
            Total value of all cards in hand
        """
        return sum(card.value for card in self.hand)
    
    def is_empty_hand(self) -> bool:
        """Check if player's hand is empty.
        
        Returns:
            True if hand is empty, False otherwise
        """
        return len(self.hand) == 0
