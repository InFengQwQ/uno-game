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
    scene.__init__((W, H), flags=pygame.SRCALPHA)
    columns.clear()
    inputs.clear()
    buttons.clear()

def update() -> bool:
    screen.fill(BACKGROUND_COLOR)
    screen.blit(scene, (0, 0))
    for column in columns:
        screen.blit(column, column.rect)
        column.update()
    for button in buttons:
        screen.blit(button, button.rect)
    for input in inputs:
        screen.blit(input, input.rect)
    for event in pygame.event.get():
        for input in inputs.copy():
            input.update(event)
        for button in buttons.copy():
            button.update(event)
        if event.type == pygame.QUIT:
            return False
    pygame.display.flip()

    clock.tick(FPS)

    if any(input.hover for input in inputs):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    return True