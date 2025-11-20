from typing import Any, Callable

import pygame

from .constants import TEXT_COLOR, HIGHLIGHT_COLOR
from .utils import slice_scale


class Button(pygame.Surface):

    elements: list['Button'] = []

    @classmethod
    def init(
        cls,
        text_font: pygame.font.Font,
        click_sound: pygame.mixer.Sound
    ):
        cls._text_font = text_font
        cls._click_sound = click_sound

    def __init__(
        self,
        image: pygame.Surface,
        rect: pygame.Rect,
        action: Callable[..., None],
        slice: bool = False,
        text: str = ''
    ):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.action = action

        if slice:
            self.surface = slice_scale(image, rect.size)
        else:
            self.surface = pygame.transform.smoothscale(
                image, rect.size
            )
        if text:
            text_surface = self._text_font.render(
                text, True, TEXT_COLOR
            )
            text_rect = text_surface.get_rect(
                center=self.surface.get_rect().center
            )
            self.surface.blit(text_surface, text_rect)

        self._rect_topleft = rect.topleft
        self._mask = pygame.mask.from_surface(self.surface)
        self._highlight = self._mask.to_surface(
            setcolor=HIGHLIGHT_COLOR,
            unsetcolor=pygame.Color('#00000000')
        )

    def get_rect(self, **kwargs: Any) -> pygame.Rect:
        """It works like pygame but with default topleft."""

        return super().get_rect(
            topleft=(
                self._rect_topleft
                if hasattr(self, '_rect_topleft')
                else (0, 0)
            ),
            **kwargs
        )

    @property
    def is_hovered(self) -> bool:
        mx, my = pygame.mouse.get_pos()
        x, y = self.get_rect().topleft
        rel_pos = mx - x, my - y

        return (
            self.get_rect().collidepoint(mx, my) and
            bool(self._mask.get_at(rel_pos))
        )

    def update(
        self,
        event: pygame.event.Event = pygame.event.Event(pygame.USEREVENT)
    ):
        self.blit(self.surface, (0, 0))

        if self.is_hovered:
            self.blit(self._highlight, (0, 0))

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._click_sound.play()
                self.action()

    @classmethod
    def update_all(cls, events: list[pygame.event.Event]):
        if events:
            for button in cls.elements:
                for event in events:
                    button.update(event)
        else:
            for button in cls.elements:
                button.update()