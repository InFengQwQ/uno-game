import os
import logging
from functools import wraps
from typing import Any, Callable, override

import pygame

from config import (
    W, H,
    FPS,
    MESSAGE_BOX_WIDTH, MESSAGE_BOX_HEIGHT,
    MESSAGE_BOX_TOP_MARGIN, MESSAGE_TEXT_LEFT_MARGIN,
    MESSAGE_DISPLAY_TIME,
    UI_ELEMENT_PADDING
)

from .constants import (
    HIGHLIGHT, TRANSPARENT,
    TEXT_COLOR, HINT_COLOR
)
from .utils import slice_scale

__all__ = [
    'Element',
    'Column', 'Input', 'Button', 'Message'
]


LOG_FILE = os.path.join(os.path.expanduser('~'), 'message.log')

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
    ]
)
_logger = logging.getLogger(__name__)


class Element(pygame.Surface):
    """Common template of UI elements.

    Holds the screen position and the
    per-class registry.
    """
    elements: list[Any]
    registry: list[type['Element']] = []

    def __init_subclass__(cls):
        super().__init_subclass__()
        Element.registry.append(cls)

    def __init__(self, rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)):
        super().__init__(rect.size, pygame.SRCALPHA)
        self._top_left = rect.topleft

    @override
    def get_rect(self, **kwargs: Any) -> pygame.Rect:
        return super().get_rect(
            topleft=getattr(self, '_top_left', (0, 0)),
            **kwargs
        )

    def handle(self, event: pygame.event.Event) -> None: ...

    def draw(self) -> None:
        raise NotImplementedError

    @classmethod
    def handle_all(cls, events: list[pygame.event.Event]):
        """Handle all elements.

        Args:
            events: The events to handle with.
        """
        for element in cls.elements.copy():
            for event in events:
                element.handle(event)

    @classmethod
    def draw_all(cls):
        for element in cls.elements.copy():
            element.draw()


class Column(Element):
    """Information column.

    A column element that's generated from two images,
    which displays a tag and several lines of content.
    """
    elements: list['Column'] = []

    @classmethod
    def init(cls,
        tag_font: pygame.font.Font,
        content_font: pygame.font.Font,
        back_image: pygame.Surface,
        face_image: pygame.Surface,
        divider_image: pygame.Surface
    ):
        cls._tag_font = tag_font
        cls._content_font = content_font
        cls._back_image = back_image
        cls._face_image = face_image
        cls._divider_image = divider_image

    def __init__(self,
        rect: pygame.Rect,
        tag: str,
        head: float = 48,
        contents: list[str] = []
    ):
        super().__init__(rect=rect)

        self._tag = tag
        self._contents = contents

        self._back_surface = slice_scale(
            self._back_image,
            rect.size
        )
        self._face_surface = slice_scale(
            self._face_image,
            (rect.w, rect.h - head)
        )

    def get_head(self) -> int:
        return (
            self._back_surface.get_height() -
            self._face_surface.get_height()
        )

    def draw(self):
        """Render the column element."""
        self.blit(self._back_surface, (0, 0))

        if self._tag:
            tag_surface = self._tag_font.render(
                self._tag, True, TEXT_COLOR
            )
            tag_rect = tag_surface.get_rect(center=(
                self.get_width()/2, self.get_head()/2
            ))
            self.blit(tag_surface, tag_rect)

        self.blit(self._face_surface, (0, self.get_head()))

        for line, content in enumerate(self._contents):
            if content:
                content_surface = self._content_font.render(
                    content, True, TEXT_COLOR
                )
                content_rect = content_surface.get_rect(topleft=(
                    16, self.get_head()+16 + line * H * 1/20
                ))
                self.blit(content_surface, content_rect)
            else:
                divider_surface = pygame.transform.scale(
                    self._divider_image, (self.get_width() - 48, 4)
                )
                divider_rect = divider_surface.get_rect(topleft=(
                    24, self.get_head()+20 + line * H * 1/20
                ))
                self.blit(divider_surface, divider_rect)

class Input(Element):
    """Text input.

    An input element that contains text,
    activated to be inputted when hovered and clicked,
    deactivated when clicked outside or pressed enter.

    Attributes:
        text: Contained text.
        hint: Hint text.
    """
    elements: list['Input'] = []

    @classmethod
    def init(cls,
        hint_font: pygame.font.Font,
        active_image: pygame.Surface,
        normal_image: pygame.Surface,
        tap_sound: pygame.mixer.Sound
    ):
        cls._hint_font = hint_font
        cls._active_image = active_image
        cls._normal_image = normal_image
        cls._tap_sound = tap_sound

    def __init__(self, rect: pygame.Rect, hint: str = ''):
        super().__init__(rect=rect)

        self._active_surface = slice_scale(
            self._active_image,
            rect.size
        )
        self._normal_surface = slice_scale(
            self._normal_image,
            rect.size
        )
        self._mask = pygame.mask.from_surface(self._normal_surface)

        self._is_activated = False

        self._txtarea = self.subsurface(
            (UI_ELEMENT_PADDING, UI_ELEMENT_PADDING),
            (
                rect.w - UI_ELEMENT_PADDING * 2,
                rect.h - UI_ELEMENT_PADDING * 2
            )
        )
        self.text = ''

        self.hint = hint

    @property
    def is_hovered(self) -> bool:
        mx, my = pygame.mouse.get_pos()
        x, y = self.get_rect().topleft
        rel_pos = mx - x, my - y

        return (
            self.get_rect().collidepoint(mx, my) and
            bool(self._mask.get_at(rel_pos))
        )

    def handle(self, event: pygame.event.Event):
        """Handle an element (with given event).

        Args:
            [event]: Given event to handle with.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                for element in self.elements:
                    element._is_activated = element is self
                self._tap_sound.play()
            else:
                self._is_activated = False

        if self._is_activated:
            if event.type == pygame.TEXTINPUT:
                self.text += event.text
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1] if self.text else ''
                if event.key == pygame.K_RETURN:
                    self._is_activated = False

    def draw(self):
        self.fill(TRANSPARENT)

        if self._is_activated:
            self.blit(self._active_surface, (0, 0))
        else:
            self.blit(self._normal_surface, (0, 0))

        if self.text:
            font = pygame.font.SysFont(
                None, self._txtarea.get_height() - 4
            )

            txt_surface = font.render(
                self.text, True, TEXT_COLOR
            )
            txt_rect = txt_surface.get_rect(
                midright=self._txtarea.get_rect().midright
            )
            self._txtarea.blit(txt_surface, txt_rect)
        else:
            hint_surface = self._hint_font.render(
                self.hint, True, HINT_COLOR
            )
            hint_rect = hint_surface.get_rect(
                center=self._txtarea.get_rect().center
            )
            self._txtarea.blit(hint_surface, hint_rect)

    @classmethod
    def handle_all(cls, events: list[pygame.event.Event]):
        for _ in (
            event for event in events
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB
        ):
            if not cls.elements:
                continue

            current = next((
                i for i, element in enumerate(cls.elements)
                if element._is_activated
            ), -1)
            cls.elements[current]._is_activated = False
            cls.elements[
                (current + 1) % len(cls.elements)
            ]._is_activated = True

        super().handle_all(events)

class Button(Element):
    """Clickable button.

    A button element that's generated from an image and text,
    when hovered and clicked, a given action will get called.
    """
    elements: list['Button'] = []

    @classmethod
    def init(cls,
        text_font: pygame.font.Font,
        click_sound: pygame.mixer.Sound
    ):
        cls._text_font = text_font
        cls._click_sound = click_sound

    @staticmethod
    def idle() -> str: return ""

    def __init__(self,
        rect: pygame.Rect,
        image: pygame.Surface,
        action: Callable[..., None],
        slice: bool = False,
        text: Callable[[], str] = idle
    ):
        super().__init__(rect=rect)

        self._action = action

        if slice:
            self._surface = slice_scale(image, rect.size)
        else:
            self._surface = pygame.transform.scale(
                image, rect.size
            )
        self._mask = pygame.mask.from_surface(self._surface)

        self.text = text

        self._highlight = self._mask.to_surface(
            setcolor=HIGHLIGHT, unsetcolor=None
        )

    @property
    def is_hovered(self) -> bool:
        mx, my = pygame.mouse.get_pos()
        x, y = self.get_rect().topleft
        rel_pos = mx - x, my - y

        return (
            self.get_rect().collidepoint(mx, my) and
            bool(self._mask.get_at(rel_pos))
        )

    def handle(self, event: pygame.event.Event):
        """Handle an element (with given event).

        Args:
            [event]: Given event to handle with.
        """
        if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN:
            self._click_sound.play()
            self._action()

    def draw(self):
        self.blit(self._surface, (0, 0))

        text = self.text()
        if text:
            text_surface = self._text_font.render(
                text, True, TEXT_COLOR
            )
            text_rect = text_surface.get_rect(
                center=self._surface.get_rect().center
            )
            self.blit(text_surface, text_rect)

        if self.is_hovered:
            self.blit(self._highlight, (0, 0))

class Message(Element):
    """Pop-up message.

    A message element that displays an
    exception message for a short time.

    Attributes:
        time: Display duration.
        alpha: Message Opacity.
    """
    elements: list['Message'] = []

    @classmethod
    def init(cls,
        message_font: pygame.font.Font,
        box_image: pygame.Surface
    ):
        cls._message_font = message_font
        cls._box_image = box_image

    def __init__(self,
        message: Exception,
        rect: pygame.Rect = pygame.Rect(
            (W - MESSAGE_BOX_WIDTH) / 2,
            MESSAGE_BOX_TOP_MARGIN,
            MESSAGE_BOX_WIDTH,
            MESSAGE_BOX_HEIGHT
        ),
        time: float = MESSAGE_DISPLAY_TIME
    ):
        super().__init__(rect=rect)

        self.blit(slice_scale(self._box_image, rect.size), (0, 0))
        message_surface = self._message_font.render(
            str(message), True, TEXT_COLOR
        )
        message_rect = message_surface.get_rect(midleft=(
            MESSAGE_TEXT_LEFT_MARGIN, rect.h / 2
        ))
        self.blit(message_surface, message_rect)

        self.time = time
        self.alpha = 255

    def draw(self):
        """Render the message element."""
        self.alpha = self.alpha - 255 * 1/(self.time * FPS)
        if self.alpha < 0:
            self.elements.remove(self)
        else:
            self.set_alpha(int(self.alpha))

    @classmethod
    def catch(cls, func: Callable[..., Any]) -> Callable[..., Any]:
        """Catch exceptions and display them as message.

        The caught exception will be logged into a file,
        creating a new message element.

        Args:
            func: The function to wrap.

        Returns:
            A wrapped function.
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, (ValueError, OSError)):
                    _logger.error(
                        f"From function {func.__name__}: {str(e)}",
                        exc_info=True
                    )

                cls.elements.append(Message(e))

        return wrapper
