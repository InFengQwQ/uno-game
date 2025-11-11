import pygame

# screen
SCREEN_WIDTH = W = 800
SCREEN_HEIGHT = H = 600

assert W >= 800 and H >= 600

# FPS
FPS = 165

# colors
BACKGROUND_COLOR = pygame.Color('#3399D9')
TAG_COLOR = CONTENT_COLOR = TEXT_COLOR = pygame.Color('#000000')
HINT_COLOR = pygame.Color('#DDDDDD')
MESSAGE_COLOR = pygame.Color("#800000")
HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')

# surface
MESSAGE_RECT = pygame.Rect((W - 384) / 2, 16, 384, 48)