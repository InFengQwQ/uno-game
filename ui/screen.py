from collections import deque

import pygame

from .constants import W, H, FPS, BACKGROUND_COLOR
from .column import Column
from .input import Input
from .button import Button
from .message import Message

pygame.init()

def _draw_icon():
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # 红绿蓝黄
    for i, color in enumerate(colors):
        rect = pygame.Rect(i % 2 * 16, i // 2 * 16, 16, 16)
        pygame.draw.rect(icon, color, rect)
    return icon

pygame.display.set_icon(_draw_icon())
pygame.display.set_caption('Game')
pygame.key.set_repeat(500, 50)
_screen = pygame.display.set_mode((W, H), flags=0)
_clock = pygame.time.Clock()

scene = pygame.Surface((W, H), pygame.SRCALPHA)

def clear():
    """Clear all UI elements and reset the scene surface."""

    scene.__init__((W, H), flags=pygame.SRCALPHA)
    Column.columns.clear()
    Input.inputs.clear()
    Button.buttons.clear()

def update(counter: int = 0):
    """Update all UI elements and handle events each frame."""

    _clock.tick(FPS)

    events = pygame.event.get((
        pygame.QUIT,
        pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN,
        pygame.MOUSEMOTION
    ))
    deque(
        map(
            lambda Element: Element.update_all(events),
            (Column, Input, Button, Message),
        ),
        maxlen=0
    )
    if pygame.event.Event(pygame.QUIT) in events:
        pygame.quit()
        return 0

    _screen.fill(BACKGROUND_COLOR)
    _screen.blit(scene, (0, 0))
    deque(
        map(
            lambda elements: _screen.blits(deque(map(
                lambda element: (element, element.get_rect()),
                elements
            ))),
            (Column.columns, Input.inputs, Button.buttons, Message.messages)
        ),
        maxlen=0
    )
    pygame.display.flip()

    if any(input.is_hovered for input in Input.inputs):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return counter + 1