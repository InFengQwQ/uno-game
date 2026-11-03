import math
from collections.abc import Sequence
from functools import partial
from typing import Callable

import pygame

from config import (
    W, H,
    INITIAL_HAND_SIZE,
    MAX_PLAYERS
)
from uno import (
    CardColor, COLORS,
    Card, Player
)

from .constants import (
    HIGHLIGHT, TRANSPARENT,
    TEXT_COLOR
)
from .element import *

__all__ = ['Stage']


class Stage(Element):
    """Game tableau.

    Holds the table layout by regions.

    Attributes:
        roster: The room roster.
        pile: The center region.
        stripe: The hand stripe.
    """
    elements: list['Stage'] = []

    @classmethod
    def init(cls,
        name_font: pygame.font.Font,
        size_font: pygame.font.Font,
        card_images: dict[str, pygame.Surface]
    ):
        cls._name_font = name_font
        cls._size_font = size_font
        cls._card_images = card_images

    def __init__(self,
        players: Sequence[Player],
        player: Player,
        hand: Sequence[Card],
        top: Card,
        slot: int,
        rect: pygame.Rect = pygame.Rect( # MARGIN...
            0, H * 1/6, W, H * 2/3
        )
    ):
        super().__init__(rect=rect)
        hw = rect.w / INITIAL_HAND_SIZE

        self._roster_rect = pygame.Rect(0, 0, rect.w, hw)
        self._pile_rect = pygame.Rect(rect.w * 1/4, hw * 6/5, rect.w * 1/2, rect.h - hw * 12/5)
        self._stripe_rect = pygame.Rect(0, rect.h - hw, rect.w, hw)

        self.roster = Stage.Roster(self._roster_rect, players, player, top)
        self.pile = Stage.Pile(self._pile_rect, top)
        self.stripe = Stage.Stripe(self._stripe_rect, hand, slot)

    def draw(self):
        """Draw the stage."""
        self.roster.draw()
        self.pile.draw()
        self.stripe.draw()

        self.fill(TRANSPARENT)
        self.blit(self.roster, self._roster_rect)
        self.blit(self.pile, self._pile_rect)
        self.blit(self.stripe, self._stripe_rect)

    class Roster(pygame.Surface):
        def __init__(self,
            rect: pygame.Rect,
            players: Sequence[Player],
            player: Player,
            top: Card,
        ):
            super().__init__(rect.size, pygame.SRCALPHA)

            self._player = player
            self._players = players

            self._card_size = (rect.h - 32, rect.h - 32)
            self._back_surface = pygame.transform.scale(
                Stage._card_images['back'],
                self._card_size
            )
            self._top = top

        @property
        def _face_surface(self) -> pygame.Surface:
            return pygame.transform.scale(
                Stage._card_images[f'{self._top.color}_empty'],
                self._card_size
            )

        def draw(self):
            for i, player in enumerate(self._players):
                d = self.get_width()/(MAX_PLAYERS + 1)

                w, h = self._card_size
                if player == self._player:
                    self.blit(self._face_surface, (d * (i + 1) - w/2, 0))
                else:
                    self.blit(self._back_surface, (d * (i + 1) - w/2, 0))

                    size_surface = Stage._size_font.render(
                        str(player.size), True, TEXT_COLOR
                    )
                    size_rect = size_surface.get_rect(center=(
                        d * (i + 1), h / 2
                    ))
                    self.blit(size_surface, size_rect)

                name_surface = Stage._name_font.render(
                    player.name, True, TEXT_COLOR
                )
                name_rect = name_surface.get_rect(midtop=(
                    d * (i + 1), h + 8
                ))
                self.blit(name_surface, name_rect)

    class Pile(pygame.Surface):
        def __init__(self,
            rect: pygame.Rect,
            top: Card
        ):
            super().__init__(rect.size, pygame.SRCALPHA)

            self._card_size = (rect.h, rect.h)
            self._back_surface = pygame.transform.scale(
                Stage._card_images['back'],
                self._card_size
            )
            self._top = top

        @property
        def _face_surface(self) -> pygame.Surface:
            return pygame.transform.scale(
                Stage._card_images[self._top.id],
                self._card_size
            )

        def draw(self):
            w, _ = self._card_size
            self.blit(self._back_surface, (0, 0))
            self.blit(self._face_surface, (self.get_width() - w, 0))

    class Stripe(pygame.Surface):
        def __init__(self,
            rect: pygame.Rect,
            hand: Sequence[Card],
            slot: int
        ):
            super().__init__(rect.size, pygame.SRCALPHA)

            self._hand = hand
            self._slot = slot

            self._card_size = (rect.h, rect.h)

        def draw(self):
            self.fill(TRANSPARENT)

            w, hw = self._card_size
            n = len(self._hand)

            # 归一化
            def u(i: float):
                assert 0 <= i <= n - 1
                if i > 0:
                    return 2 * (i / (n - 1))
                else:
                    return 0
            def f(u: float):
                k = 1 # 幅度
                return math.tanh(k * u) / math.tanh(k)

            t = w * n * .5
            s = self._slot
            s = max(min(s, n - 1), 0)

            def x(i: float):
                return f(u(i) - u(s)) * (t / 2)

            for i, card in enumerate(self._hand):
                card_surface = pygame.transform.scale(
                    Stage._card_images[card.id], (w, hw)
                )
                card_rect = card_surface.get_rect(midtop=(
                    self.get_width() / 2 + x(i), 0
                ))
                self.blit(card_surface, card_rect)
    
                if i == s:
                    # 高亮
                    self.blit(
                        pygame.mask.from_surface(
                            card_surface
                        ).to_surface(
                            setcolor=HIGHLIGHT, unsetcolor=None
                        ),
                        card_rect
                    )


    class Selector:
        """Color Selector."""
        def __init__(self,
            rect: pygame.Rect,
            action: Callable[[CardColor], None]
        ):
            Column.elements.append(column := Column(
                rect, "Select from Choice"
            ))

            Button.elements.extend([
                Button(
                    pygame.Rect(
                        rect.centerx + (i * 5/4 - 19/8) * (
                            W / INITIAL_HAND_SIZE - 32
                        ),
                        rect.y + (
                            rect.h + column.get_head() -
                            W / INITIAL_HAND_SIZE + 32
                        ) / 2,
                        W / INITIAL_HAND_SIZE - 32,
                        W / INITIAL_HAND_SIZE - 32
                    ),
                    Stage._card_images[f'{color}_empty'],
                    partial(action, color),
                )
                for i, color in enumerate(COLORS)
            ])
