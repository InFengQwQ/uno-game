"""Module defining the rules of the UNO game."""

from typing import TYPE_CHECKING, Optional

from .constants import BLACK_COLOR
from .card import Card
from .player import Player

if TYPE_CHECKING:
    from .game import Game


class Rules:
    """Defines the rules and logic of the UNO game."""
    
    @staticmethod
    def is_valid_play(card: Card, game: 'Game') -> bool:
        """Check if a card can be played on top of the current discard pile.
        
        Args:
            card: The card to play
            game: The current game state
            
        Returns:
            True if the card can be played, False otherwise
        """
        top = game.deck.discard_pile[-1]
        return (
            card.color == BLACK_COLOR or
            card.color == top.color or
            card.sort == top.sort and card.value == top.value
        )

    @staticmethod
    def is_able_to_play(player: Player, game: 'Game') -> bool:
        """Check if the player is able to play any card.
        
        Args:
            player: The player to check
            game: The current game state
            
        Returns:
            True if player has at least one playable card
        """
        return any(Rules.is_valid_play(card, game) for card in player.hand)

    @staticmethod
    def apply_special_effects(card: Card, game: 'Game') -> None:
        """Apply the special effects of a card to the game state.
        
        Args:
            card: The card whose effects to apply
            game: The current game state
        """
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
        """Check if the player has won the game.
        
        Args:
            player: The player to check
            
        Returns:
            True if player has no cards left
        """
        return not player.hand

    @staticmethod
    def score(game: 'Game') -> int:
        """Calculate the total score of all players' hands in the game.
        
        Args:
            game: The current game state
            
        Returns:
            Total score value of all cards in all players' hands
        """
        return sum(
            sum(card.value for card in player.hand)
            for player in game.players
        )
    
    @staticmethod
    def get_playable_cards(player: Player, game: 'Game') -> list[Card]:
        """Get all cards that the player can currently play.
        
        Args:
            player: The player whose cards to check
            game: The current game state
            
        Returns:
            List of playable cards
        """
        return [card for card in player.hand if Rules.is_valid_play(card, game)]
    
    @staticmethod
    def can_challenge_draw_four(challenger: Player, challenged_card_player: Player, 
                                 previous_top_color: str) -> bool:
        """Check if a draw four challenge would be successful.
        
        Args:
            challenger: The player challenging the draw four
            challenged_card_player: The player who played the draw four
            previous_top_color: The color of the card before the draw four
            
        Returns:
            True if challenge succeeds (player had matching color), False otherwise
        """
        for card in challenged_card_player.hand:
            if card.color == previous_top_color and card.color != BLACK_COLOR:
                return True
        return False
