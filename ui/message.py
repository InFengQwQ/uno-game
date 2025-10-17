import pygame


class Message(pygame.Surface):  # 弹出在屏幕上方的错误或提示
    content_font: pygame.font.Font
    def __init__(self, content: str):   # 也不一定要叫content
        self.content = content