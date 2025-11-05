from . import MESSAGE_RECT, FPS, TEXT_COLOR, scale
import pygame
from functools import wraps
from typing import Callable
import logging

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('message.log'),  # 输出到文件
        logging.StreamHandler()            # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)


class Message(pygame.Surface):  # 弹出在屏幕上方的错误或提示
    messages: list['Message'] = []

    message_image: pygame.Surface
    message_font: pygame.font.Font

    def __init__(self, message: Exception, rect: pygame.Rect = MESSAGE_RECT, time: int = 5):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.blit(scale(self.message_image, rect.size), (0, 0))
        if message:
            message_surface = self.message_font.render(str(message), True, TEXT_COLOR)
            message_rect = message_surface.get_rect(midleft=(16, self.get_rect().h // 2))
            self.blit(message_surface, message_rect)

        self.rect = rect
        self.time = time
        self.alpha = 255

    def update(self):
        self.alpha = int(self.alpha - 255 * 1 / (self.time * FPS))
        if self.alpha < 0:
            Message.messages.remove(self)
        else:
            self.set_alpha(self.alpha)

    @classmethod
    def update_all(cls):
        for message in cls.messages.copy():
            message.update()

    @classmethod
    def catch(cls, func: Callable[..., None]) -> Callable[..., None]:
        """Catch exceptions and display them as messages."""

        @wraps(func)
        def wrapper(*args: ..., **kwargs: ...):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"函数 {func.__name__} 发生异常: {str(e)}", exc_info=True)
                cls.messages.append(Message(e))
        return wrapper