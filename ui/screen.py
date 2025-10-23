from . import W, H, FPS, BACKGROUND_COLOR, Column, Input, Button, Message
import pygame


pygame.init()

pygame.display.set_icon(pygame.image.load('icon.png'))  # 也许可在加载资源之前执行？
pygame.display.set_caption('Uno Game')
screen = pygame.display.set_mode((W, H), flags=0)

clock = pygame.time.Clock()

scene = pygame.Surface((W, H), pygame.SRCALPHA)
columns: list[Column] = []
inputs: list[Input] = []
buttons: list[Button] = []
messages: list[Message] = []

def clear():
    '''Clear all UI elements and reset the scene surface.'''
    scene.__init__((W, H), flags=pygame.SRCALPHA)
    columns.clear()
    inputs.clear()
    buttons.clear()

def update():
    '''Update all UI elements and handle user events each frame.'''
    tick = clock.tick(FPS)

    events = pygame.event.get((pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.TEXTINPUT, pygame.KEYDOWN))
    for event in events if events else [pygame.event.Event(pygame.USEREVENT)]:
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        for column in columns.copy():
            column.update()
        for input in inputs.copy():
            input.update(event)
        for button in buttons.copy():
            button.update(event)
        for message in messages.copy():
            message.update(tick)
            if message.alpha == 0:
                messages.remove(message)

    screen.fill(BACKGROUND_COLOR)
    screen.blit(scene, (0, 0))
    screen.blits([(column, column.rect) for column in columns])
    screen.blits([(input, input.rect) for input in inputs])
    screen.blits([(button, button.rect) for button in buttons])
    screen.blits([(message, message.rect) for message in messages if message.alpha > 0])
    pygame.display.flip()

    if any(input.hover for input in inputs):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return True