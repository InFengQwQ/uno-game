from . import scale
import pygame
from typing import Callable


pygame.init()

images = {}
fonts = {'button': pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)}

class Button(pygame.Surface):
    def __init__(self, image: pygame.Surface, rect: pygame.Rect, action: Callable[[], None], slice: bool = False, text: str = ''):
        super().__init__(rect.size, pygame.SRCALPHA)

        if slice:
            self.surface = scale(image, rect.size)
        else:
            self.surface = pygame.transform.scale(image, rect.size)
        if text:
            font = fonts['button']
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=self.get_rect().center)
            self.surface.blit(text_surface, text_rect)

        self.rect = rect
        self.action = action
        self.mask = pygame.mask.from_surface(self.surface)
        self.highlight = self.mask.to_surface(setcolor=HIGHLIGHT_COLOR, unsetcolor=(0, 0, 0, 0))

        buttons.append(self)

    @property
    def hover(self):
        mx, my = pygame.mouse.get_pos()
        x, y = self.rect.topleft
        pos = mx - x, my - y
        try:
            return self.mask.get_at(pos)
        except IndexError:
            return False

    def update(self, event: pygame.event.Event):
        self.blit(self.surface, (0, 0))
        if self.hover:
            self.blit(self.highlight, (0, 0))
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.action()

buttons: list[Button] = []