from . import W, TEXT_COLOR, scale
import pygame


class Message(pygame.Surface):  # 弹出在屏幕上方的错误或提示
    message_image: pygame.Surface
    message_font: pygame.font.Font

    def __init__(self, message: Exception, rect: pygame.Rect = pygame.Rect((W - 288) // 2, 16, 288, 48), time: int = 2):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.blit(scale(self.message_image, rect.size), (0, 0))
        if message:
            message_surface = self.message_font.render(str(message), True, TEXT_COLOR)
            message_rect = message_surface.get_rect(midleft=(16, self.get_rect().h // 2))
            self.blit(message_surface, message_rect)

        self.rect = rect
        self.time = time
        self.alpha = 255

    def update(self, tick: int):
        self.alpha = max(0, int(self.alpha - 255 * (int(tick)/1000 / self.time)))
        self.set_alpha(self.alpha)