import pygame


# screen 只会更大，不能再小了
SCREEN_WIDTH = W = 800
SCREEN_HEIGHT = H = 600
# FPS
FPS = 60
# colors
BACKGROUND_COLOR = pygame.Color('#3399D9')
TEXT_COLOR = pygame.Color('#000000')
HINT_COLOR = pygame.Color('#DDDDDD')
HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')
# surface
MESSAGE_RECT = pygame.Rect((W - 288) // 2, 16, 288, 48)