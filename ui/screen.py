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
    """Update all UI elements and handle user events each frame."""

    _clock.tick(FPS)

    events = pygame.event.get((pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN))
    for event in events if events else [pygame.event.Event(pygame.USEREVENT)]:
        Column.update_all()
        Input.update_all(event)
        Button.update_all(event)
        Message.update_all()
        if event.type == pygame.QUIT:
            pygame.quit()
            return 0

    _screen.fill(BACKGROUND_COLOR)
    _screen.blit(scene, (0, 0))
    _screen.blits([(column, column.get_rect()) for column in Column.columns])
    _screen.blits([(input, input.get_rect()) for input in Input.inputs])
    _screen.blits([(button, button.get_rect()) for button in Button.buttons])
    _screen.blits([(message, message.get_rect()) for message in Message.messages])
    pygame.display.flip()

    if any(input.is_hovered for input in Input.inputs):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return counter + 1