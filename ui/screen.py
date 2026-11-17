import itertools

import pygame

from config import (
    W, H,
    FPS,
    WINDOW_TITLE, WINDOW_ICON_SIZE,
    KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL
)

from .constants import BACKGROUND
from .element import (
    Element,
    Input, Message
)

__all__ = [
    'scene', 'clock',
    'update', 'clear',
]


pygame.init()

_icon = pygame.Surface(WINDOW_ICON_SIZE, pygame.SRCALPHA)
for i, color in enumerate(((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))):  # 红绿蓝黄
    rect = pygame.Rect(i % 2 * 16, i // 2 * 16, 16, 16)
    pygame.draw.rect(_icon, color, rect)

pygame.display.set_icon(_icon)
pygame.display.set_caption(WINDOW_TITLE)
pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
_screen = pygame.display.set_mode((W, H), flags=0)
scene = pygame.Surface((W, H), pygame.SRCALPHA)


clock = pygame.time.Clock()
def update(elapsed: int = 0):
    """Update all UI elements."""
    events = pygame.event.get((
        pygame.QUIT,
        pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN,
        pygame.MOUSEMOTION
    ))
    if pygame.event.Event(pygame.QUIT) in events:
        pygame.quit()
        return 0
    for element_type in Element.registry:
        element_type.handle_all(events)

    for element_type in Element.registry:
        element_type.draw_all()

    _screen.fill(BACKGROUND)
    _screen.blit(scene, (0, 0))
    for element in itertools.chain.from_iterable(
        element_type.elements for element_type in Element.registry
    ):
        _screen.blit(element, element.get_rect())
    pygame.display.flip()

    if any(element.is_hovered for element in Input.elements):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return elapsed + clock.tick(FPS)

def clear():
    scene.__init__((W, H), flags=pygame.SRCALPHA)
    for element_type in set(Element.registry) - {Message}:
        element_type.elements.clear()
