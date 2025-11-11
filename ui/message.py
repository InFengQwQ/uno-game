from functools import wraps
from typing import Any, Callable
import logging

import pygame

from .constants import MESSAGE_RECT, FPS, TEXT_COLOR
from .utils import slice_scale

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('message.log'),
    ]
)
_logger = logging.getLogger(__name__)


class Message(pygame.Surface):
    """Pop-up message."""

    messages: list['Message'] = []

    @classmethod
    def init(
        cls,
        message_image: pygame.Surface,
        message_font: pygame.font.Font
    ):
        cls._message_image = message_image
        cls._message_font = message_font

    def __init__(
        self,
        message: Exception,
        rect: pygame.Rect = MESSAGE_RECT,
        time: int = 5
    ):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.blit(slice_scale(self._message_image, rect.size), (0, 0))
        if message:
            message_surface = self._message_font.render(
                str(message), True, TEXT_COLOR
            )
            message_rect = message_surface.get_rect(
                midleft=(16, rect.h / 2)
            )
            self.blit(message_surface, message_rect)

        self._rect_topleft = rect.topleft
        self._time = time
        self._alpha = 255

    def get_rect(self, **kwargs: Any) -> pygame.Rect:
        """It works like pygame but with default topleft."""

        return super().get_rect(
            topleft=(
                self._rect_topleft
                if hasattr(self, '_rect_topleft')
                else (0, 0)
            ),
            **kwargs
        )

    def update(self):
        self._alpha = int(self._alpha - 255 * 1/(self._time * FPS))
        if self._alpha < 0:
            self.messages.remove(self)
        else:
            self.set_alpha(self._alpha)

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
                _logger.error(
                    f"From function {func.__name__}: {str(e)}",
                    exc_info=True
                )

                cls.messages.append(Message(e))

        return wrapper