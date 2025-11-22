from typing import Any

import pygame

from config import H
from .constants import TEXT_COLOR
from .utils import slice_scale


class Column(pygame.Surface):

    elements: list['Column'] = []

    @classmethod
    def init(
        cls,
        back_image: pygame.Surface,
        front_image: pygame.Surface,
        divider_image: pygame.Surface,
        tag_font: pygame.font.Font,
        content_font: pygame.font.Font
    ):
        cls._back_image = back_image
        cls._front_image = front_image
        cls._divider_image = divider_image
        cls._tag_font = tag_font
        cls._content_font = content_font

    def __init__(
        self,
        rect: pygame.Rect,
        head: float = 48,
        tag: str = '',
        contents: list[str] = []
    ):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.tag = tag
        self.contents = contents

        self.back_surface = slice_scale(
            self._back_image, rect.size
        )

        self.front_surface = slice_scale(
            self._front_image, (rect.w, rect.h - head) 
        )

        self._rect_topleft = rect.topleft

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

    def get_head(self) -> int:
        return (
            self.back_surface.get_height()
            - self.front_surface.get_height()
        )

    def update(self,):
        self.blit(self.back_surface, (0, 0))

        if self.tag:
            tag_surface = self._tag_font.render(
                self.tag, True, TEXT_COLOR
            )
            tag_rect = tag_surface.get_rect(
                center=(self.get_width() / 2, self.get_head() / 2)
            )
            self.blit(tag_surface, tag_rect)

        self.blit(self.front_surface, (0, self.get_head()))

        for line, content in enumerate(self.contents.copy()):
            if content:
                content_surface = self._content_font.render(
                    content, True, TEXT_COLOR
                )
                content_rect = content_surface.get_rect(
                    topleft=(16, self.get_head()+16 + line * H/20)
                )
                self.blit(content_surface, content_rect)
            else:
                divider_surface = pygame.transform.scale(
                    self._divider_image, (self.get_width() - 48, 4)
                )
                divider_rect = divider_surface.get_rect(
                    topleft=(24, self.get_head()+20 + line * H/20)
                )
                self.blit(divider_surface, divider_rect)

    @classmethod
    def update_all(cls, events: list[pygame.event.Event]):
        for column in cls.elements:
            column.update()