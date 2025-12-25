"""UNO game management module."""

import random
from typing import Optional

from config import INITIAL_HAND_SIZE
from .card import Card
from .deck import Deck
from .player import Player
from .rules import Rules


class Game:
    """Manages the UNO game state and logic."""
    
    def __init__(self, players: list[Player]):
        """Initialize a new UNO game.
        
        Args:
            players: List of players participating in the game
            
        Raises:
            ValueError: If number of players is invalid
        """
        if len(players) < 2:
            raise ValueError("At least 2 players are required")
        
        self.deck = Deck()
        self.players = players
        self.turn = -1   # counterclockwise is positively increasing, and default clockwise
        self.reverse = False
        self.draw = 0
        self.winner: Optional[Player] = None

        for player in self.players:
            player.draw(self.deck, INITIAL_HAND_SIZE)

        # Draw initial card (re-shuffle if it's draw_four)
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
    
    def get_current_player(self) -> Player:
        """Get the current player whose turn it is.
        
        Returns:
            The current player
        """
        return self.player
    
    def get_top_card(self) -> Card:
        """Get the top card of the discard pile.
        
        Returns:
            The top card on the discard pile
        """
        return self.deck.discard_pile[-1]
    
    def next_turn(self) -> Player:
        """Advance to the next player's turn.
        
        Returns:
            The next player
        """
        self.turn += 1 if self.reverse else -1
        self.turn %= len(self.players)
        self.player = self.players[self.turn]
        return self.player
    
    def check_winner(self) -> Optional[Player]:
        """Check if the current player has won.
        
        Returns:
            The winning player if game is over, None otherwise
        """
        if Rules.is_winner(self.player):
            self.winner = self.player
            return self.player
        return None
