import random
from typing import Optional

from config import INITIAL_HAND_SIZE

from .card import (
    CardSort,
    Card
)
from .deck import Deck
from .player import *

__all__ = ['Game']


class Game:
    """Single UNO game.

    Attributes:
        deck: The deck of the game.
        players: The players list of the game.

        turn: The index of the current player in players list.
        reverse: If the game in reverse order.
        to_draw: The num of cards the next player has to draw.
        target_player: The last acting player.

        player: The current player.
        is_end: Whether the game has ended.
    """
    def __init__(self, players: list[str]):
        self.deck = Deck()
        self.players = [Player(name) for name in players]

        self.turn = -1  # counterclockwise [+] (default = clockwise [-])
        self.reverse = False
        self.to_draw = 0
        self.target_player: Optional[Player] = None

        for _ in self.players:
            self.to_draw = INITIAL_HAND_SIZE
            self.draw()

        while (top := self.deck.draw_pile.pop()).is_pending:
            self.deck.draw_pile.insert(
                random.choice(range(len(self.deck.draw_pile))),
                top
            )

        self._apply_effects(top)
        self.deck.discard_pile.append(top)
        self.turn += int(self.reverse)
        self.turn %= len(self.players)

    @property
    def player(self) -> Player:
        return self.players[self.turn]

    @property
    def is_end(self) -> bool:
        return not (
            self.target_player is None or
            self.target_player.hand
        )

    def _next_turn(self):
        if self.is_end and not self.to_draw:
            pass # end

        self.to_draw = 0 if self.to_draw == -1 else self.to_draw
        self.turn += 1 if self.reverse else -1
        self.turn %= len(self.players)

    def _prev_turn(self):
        self.to_draw = 0 if self.to_draw == -1 else self.to_draw
        self.turn -= 1 if self.reverse else -1
        self.turn %= len(self.players)

    def _apply_effects(self, card: Card):
        match card.sort:
            case CardSort.DRAW_2:
                self.to_draw = 2
            case CardSort.REVERSE:
                if len(self.players) > 2:
                    self.reverse = not self.reverse
                else:
                    self._next_turn()
            case CardSort.SKIP:
                self._next_turn()
            case CardSort.WILD:
                pass
            case CardSort.WILD_DRAW_4:
                self.to_draw = 4
            case _: ...

    def play(self, card: Card):
        """Play the chosen card from the player's hand.

        Args:
            card: The card to play, affect game.
        """
        self.target_player = self.player

        self.player.hand.remove(card)
        self.deck.discard_pile.append(card)
        self._apply_effects(card)
        self._next_turn()

    def draw(self):
        """"""
        self.target_player = None if not self.is_end else self.target_player

        match self.to_draw:
            case -1:
                self._next_turn()
            case 0:
                if card := self.deck.draw():
                    self.player.hand.append(card)
                    self.player.uno = False
                    self.to_draw = -1
                else:
                    self._next_turn()
            case _:
                for _ in range(self.to_draw):
                    self.to_draw -= 1
                    if card := self.deck.draw():
                        self.player.hand.append(card)
                        self.player.uno = False
                else:
                    self._next_turn()

    def challenge(self):
        """"""
        assert self.target_player

        color = self.deck.discard_pile[-2].color
        if any(card.color == color for card in self.target_player.hand):
            self._prev_turn()
        else:
            self.to_draw += 2

        self.target_player = None

    def catch(self, name: str):
        """"""
        assert self.target_player

        if name == self.target_player.name:
            self.target_player.uno = True
        else:
            self.to_draw = 4
            while self.player is not self.target_player:
                self._prev_turn()

        self.target_player = None
