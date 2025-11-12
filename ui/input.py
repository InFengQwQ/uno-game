from collections import deque
from typing import Any

import pygame

from .constants import TEXT_COLOR, HINT_COLOR
from .utils import slice_scale


class Input(pygame.Surface):

    inputs: list['Input'] = []

    @classmethod
    def init(
        cls,
        inactive_image: pygame.Surface,
        active_image: pygame.Surface,
        hint_font: pygame.font.Font,
        tap_sound: pygame.mixer.Sound
    ):          # TODO: 本地存储一些默认资源吧?
        cls._inactive_image = inactive_image
        cls._active_image = active_image
        cls._hint_font = hint_font
        cls._tap_sound = tap_sound

    def __init__(self, rect: pygame.Rect, hint: str = ''):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.inactive_surface = slice_scale(
            self._inactive_image, rect.size
        )

        self.active_surface = slice_scale(
            self._active_image, rect.size
        )

        self._rect_topleft = rect.topleft
        self._hint = hint
        self._text_area = self.subsurface(
            (8, 8), (rect.w - 16, rect.h - 16)
        )
        self._mask = pygame.mask.from_surface(self.inactive_surface)

        self.is_activated = False
        self.text = ''

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.is_activated = True
                self._tap_sound.play()
            else:
                self.is_activated = False

        if self.is_activated:
            if event.type == pygame.TEXTINPUT:
                self.text += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1] if self.text else ''
                if event.key == pygame.K_RETURN:
                    self.is_activated = False

            self.blit(self.active_surface, (0, 0))
        else:
            self.blit(self.inactive_surface, (0, 0))

        if self.text:
            font = pygame.font.SysFont(None, self._text_area.get_height() - 4)          # TODO: 初始化可带此字体

            text_surface = font.render(
                self.text, True, TEXT_COLOR
            )
            text_rect = text_surface.get_rect(
                midright=self._text_area.get_rect().midright
            )
            self._text_area.blit(text_surface, text_rect)
        elif self._hint:
            hint_surface = self._hint_font.render(
                self._hint, True, HINT_COLOR
            )
            hint_rect = hint_surface.get_rect(
                center=self._text_area.get_rect().center
            )
            self._text_area.blit(hint_surface, hint_rect)

    @classmethod
    def update_all(cls, events: list[pygame.event.Event]):
        if events:
            for input in cls.inputs:
                deque(map(input.update, events), maxlen=0)
        else:
            deque(map(Input.update, cls.inputs), maxlen=0)