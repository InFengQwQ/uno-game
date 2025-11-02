from . import W, H, FPS, BACKGROUND_COLOR, Column, Input, Button, Message
import pygame


pygame.init()

pygame.display.set_icon(pygame.image.load('icon.png'))  # 也许可在加载资源之前执行？
pygame.display.set_caption('Uno Game')
pygame.key.set_repeat(500, 50)
screen = pygame.display.set_mode((W, H), flags=0)
clock = pygame.time.Clock()
scene = pygame.Surface((W, H), pygame.SRCALPHA)

def clear():
    """Clear all UI elements and reset the scene surface."""

    scene.__init__((W, H), flags=pygame.SRCALPHA)
    Column.columns.clear()
    Input.inputs.clear()
    Button.buttons.clear()

def update():
    """Update all UI elements and handle user events each frame."""

    clock.tick(FPS)

    events = pygame.event.get((pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN))
    for event in events if events else [pygame.event.Event(pygame.USEREVENT)]:
        Column.update_all()
        Input.update_all(event)
        Button.update_all(event)
        Message.update_all()
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

    screen.fill(BACKGROUND_COLOR)
    screen.blit(scene, (0, 0))
    screen.blits([(column, column.rect) for column in Column.columns])
    screen.blits([(input, input.rect) for input in Input.inputs])
    screen.blits([(button, button.rect) for button in Button.buttons])
    screen.blits([(message, message.rect) for message in Message.messages if message.alpha > 0])
    pygame.display.flip()

    if any(input.hover for input in Input.inputs):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return True