import pygame

from config import W, H, FPS, WINDOW_TITLE, WINDOW_ICON_SIZE, KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL
from .constants import BACKGROUND_COLOR
from .column import Column
from .input import Input
from .button import Button
from .message import Message

pygame.init()

def _draw_icon():
    icon = pygame.Surface(WINDOW_ICON_SIZE, pygame.SRCALPHA)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # 红绿蓝黄
    for i, color in enumerate(colors):
        rect = pygame.Rect(i % 2 * 16, i // 2 * 16, 16, 16)
        pygame.draw.rect(icon, color, rect)
    return icon

pygame.display.set_icon(_draw_icon())
pygame.display.set_caption(WINDOW_TITLE)
pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
_screen = pygame.display.set_mode((W, H), flags=0)
_clock = pygame.time.Clock()

scene = pygame.Surface((W, H), pygame.SRCALPHA)

def clear():
    """Clear all UI elements and reset the scene surface."""

    scene.__init__((W, H), flags=pygame.SRCALPHA)
    for Element in (Column, Input, Button):
        Element.elements.clear()

def update(counter: int = 0):
    """Update all UI elements and handle events each frame."""

    _clock.tick(FPS)

    events = pygame.event.get((
        pygame.QUIT,
        pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN,
        pygame.MOUSEMOTION
    ))
    for Element in (Column, Input, Button, Message):
        Element.update_all(events)
    if pygame.event.Event(pygame.QUIT) in events:
        pygame.quit()
        return 0

    _screen.fill(BACKGROUND_COLOR)
    _screen.blit(scene, (0, 0))
    for Element in (Column, Input, Button, Message):
        for element in Element.elements:
            _screen.blit(element, element.get_rect())
    pygame.display.flip()

    if any(input.is_hovered for input in Input.elements):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return counter + 1