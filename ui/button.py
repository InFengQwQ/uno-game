from . import TEXT_COLOR, HIGHLIGHT_COLOR, scale
import pygame
from typing import Callable


class Button(pygame.Surface):
    text_font: pygame.font.Font
    click_sound: pygame.mixer.Sound

    def __init__(self, image: pygame.Surface, rect: pygame.Rect, action: Callable[..., None], slice: bool = False, text: str = ''):
        super().__init__(rect.size, pygame.SRCALPHA)

        if slice:
            self.surface = scale(image, rect.size)
        else:
            self.surface = pygame.transform.smoothscale(image, rect.size)
        if text:
            text_surface = Button.text_font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=self.get_rect().center)
            self.surface.blit(text_surface, text_rect)

        self.rect = rect
        self.action = action
        self.mask = pygame.mask.from_surface(self.surface)
        self.highlight = self.mask.to_surface(setcolor=HIGHLIGHT_COLOR, unsetcolor=(0, 0, 0, 0))

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
                Button.click_sound.play()
                self.action()


buttons: list[Button] = []