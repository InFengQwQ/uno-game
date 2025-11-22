from functools import wraps
from typing import Any, Callable
import logging

import pygame

from config import (
    W, FPS,
    MESSAGE_BOX_WIDTH, MESSAGE_BOX_HEIGHT, MESSAGE_BOX_TOP_MARGIN,
    MESSAGE_TEXT_LEFT_MARGIN, MESSAGE_DISPLAY_TIME
)
from .constants import TEXT_COLOR
from .utils import slice_scale

# MESSAGE_RECT is calculated based on screen width
MESSAGE_RECT = pygame.Rect(
    (W - MESSAGE_BOX_WIDTH) / 2,
    MESSAGE_BOX_TOP_MARGIN,
    MESSAGE_BOX_WIDTH,
    MESSAGE_BOX_HEIGHT
)

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

    elements: list['Message'] = []

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
        time: int = MESSAGE_DISPLAY_TIME
    ):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.blit(slice_scale(self._message_image, rect.size), (0, 0))
        if message:
            message_surface = self._message_font.render(
                str(message), True, TEXT_COLOR
            )
            message_rect = message_surface.get_rect(
                midleft=(MESSAGE_TEXT_LEFT_MARGIN, rect.h / 2)
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

    def update(self,):
        self._alpha = int(self._alpha - 255 * 1/(self._time * FPS))
        if self._alpha < 0:
            self.elements.remove(self)
        else:
            self.set_alpha(self._alpha)

    @classmethod
    def update_all(cls, events: list[pygame.event.Event]):
        for message in cls.elements:
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

                cls.elements.append(Message(e))

        return wrapper