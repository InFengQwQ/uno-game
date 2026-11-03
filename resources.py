import sys
import os

import pygame

from uno import (
    COLORS,
    ACTIONS, WILDS,
    NUMBERS
)

__all__ = ['ResourceManager']


def _getpath(path: str) -> str:
    base = getattr(sys, '_MEIPASS', None)
    if base is None:
        # When running as a script
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, path)


def _load_font(path: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(
        _getpath(f'assets/{path}'), size
    )

def _load_image(path: str) -> pygame.Surface:
    return pygame.image.load(
        _getpath(f'assets/{path}')
    ).convert_alpha()

def _load_sound(path: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(
        _getpath(f'assets/{path}')
    )


class ResourceManager:
    # level
    _FONTS = {
        'Kenney Future.ttf': {
            16: ['hint', 'text', 'size'],
            24: ['tag'],
            10: ['message']
        },
        'Kenney Future Narrow.ttf': {
            16: ['content', 'name']
        },
    }

    # button config
    _BUTTON_SHAPES = ['square', 'round']
    _BUTTON_STYLES = ['basic', 'line', 'color']
    _ARROW_DIRECTIONS = ['left', 'right', 'up', 'down']

    def __init__(self):
        self.fonts: dict[str, pygame.font.Font] = {
            name: _load_font(f'fonts/{font}', size)
            for font, sizes in self._FONTS.items()
            for size, names in sizes.items()
            for name in names
        }

        self.images: dict[str, dict[str, pygame.Surface]] = {
            'info': {
                'cards_text': _load_image('images/info/cards_text.svg'),
                'players_2_10': _load_image('images/info/players_2_10.svg'),
            },

            'column': {
                'back': _load_image('images/column/back.svg'),
                'face': _load_image('images/column/face.svg'),
                'divider': _load_image('images/column/divider.svg'),
            },
            'input': {
                'active': _load_image('images/input/active.svg'),
                'normal': _load_image('images/input/normal.svg'),
            },
            'button': {
                **{
                    f'{shape}_{style}': _load_image(
                        f'images/button/default/{shape}_{style}.svg'
                    )
                    for shape in self._BUTTON_SHAPES
                    for style in self._BUTTON_STYLES
                },
                **{
                    f'arrow_{direction}': _load_image(
                        f'images/button/arrow/{direction}.svg'
                    )
                    for direction in self._ARROW_DIRECTIONS
                },
            },
            'message': {
                'box': _load_image('images/message/box.svg'),
            },

            'cards': {
                'back': _load_image('images/cards/back.png'),
                **{
                    f'{color}_empty': _load_image(
                        f'images/cards/{color}_empty.png'
                    )
                    for color in COLORS
                },
                **{
                    f'{color}_{number}': _load_image(
                        f'images/cards/numbers/{color}_{number}.png'
                    )
                    for color in COLORS
                    for number in NUMBERS
                },
                **{
                    f'{color}_{action}': _load_image(
                        f'images/cards/actions/{color}_{action}.png'
                    )
                    for color in COLORS
                    for action in ACTIONS
                },
                **{
                    str(wild): _load_image(
                        f'images/cards/wilds/{wild}.png'
                    )
                    for wild in WILDS
                },
            },
        }

        self.sounds: dict[str, pygame.mixer.Sound] = {
            'click': _load_sound('sounds/click.ogg'),
            'tap': _load_sound('sounds/tap.ogg'),
        }
