"""Resource manager for loading and managing game assets."""

from os.path import abspath, dirname, join
import sys
import pygame

from uno.constants import COLORS, BLACK_COLOR, NUMBERS, ACTIONS, WILDS


def getpath(path: str) -> str:
    """Get the absolute path to a resource file."""
    base = getattr(sys, '_MEIPASS', None)
    if base is None:
        # When running as script, use project root
        base = dirname(abspath(__file__))
    return join(base, path)


class ResourceManager:
    """Manages loading and access to game resources."""
    
    # Button configuration
    BUTTON_SHAPES = ['square', 'round']
    BUTTON_STYLES = ['basic', 'line', 'color']
    ARROW_DIRECTIONS = ['left', 'right', 'up', 'down']
    
    # Font configuration
    LARGE_TEXTS = ['tag']
    DEFAULT_TEXTS = ['hint', 'text']
    SMALL_TEXTS = ['message']
    NARROW_TEXTS = ['content']
    
    def __init__(self):
        """Initialize and load all resources."""
        self.images: dict[str, dict[str, pygame.Surface]] = {}
        self.fonts: dict[str, pygame.font.Font] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        
        self._load_images()
        self._load_fonts()
        self._load_sounds()
    
    def _load_images(self):
        """Load all image resources."""
        # Info images
        self.images['info'] = {
            'cards_text': pygame.image.load(
                getpath('assets/images/info/cards_text.svg')
            ).convert_alpha(),
            'players_2_10': pygame.image.load(
                getpath('assets/images/info/players_2_10.svg')
            ).convert_alpha(),
        }
        
        # Column images
        self.images['column'] = {
            'back': pygame.image.load(
                getpath('assets/images/column/back.svg')
            ).convert_alpha(),
            'front': pygame.image.load(
                getpath('assets/images/column/front.svg')
            ).convert_alpha(),
            'divider': pygame.image.load(
                getpath('assets/images/column/divider.svg')
            ).convert_alpha(),
        }
        
        # Input images
        self.images['input'] = {
            'inactive': pygame.image.load(
                getpath('assets/images/input/inactive.svg')
            ).convert_alpha(),
            'active': pygame.image.load(
                getpath('assets/images/input/active.svg')
            ).convert_alpha(),
        }
        
        # Button images
        self.images['button'] = {
            **{
                f'{shape}_{style}': pygame.image.load(
                    getpath(f'assets/images/button/default/{shape}_{style}.svg')
                ).convert_alpha()
                for shape in self.BUTTON_SHAPES
                for style in self.BUTTON_STYLES
            },
            **{
                f'arrow_{direction}': pygame.image.load(
                    getpath(f'assets/images/button/arrow/{direction}.svg')
                ).convert_alpha()
                for direction in self.ARROW_DIRECTIONS
            },
        }
        
        # Message images
        self.images['message'] = {
            'box': pygame.image.load(
                getpath('assets/images/message/box.svg')
            ).convert_alpha(),
        }
        
        # Card images
        self.images['cards'] = {
            'back': pygame.image.load(
                getpath('assets/images/cards/back.png')
            ).convert_alpha(),
            **{
                f'{color}_empty': pygame.image.load(
                    getpath(f'assets/images/cards/{color}_empty.png')
                ).convert_alpha()
                for color in COLORS
            },
            **{
                f'{color}_{value}': pygame.image.load(
                    getpath(f'assets/images/cards/numbers/{color}_{value}.png')
                ).convert_alpha()
                for color in COLORS
                for value in NUMBERS
            },
            **{
                f'{color}_{action}': pygame.image.load(
                    getpath(f'assets/images/cards/actions/{color}_{action}.png')
                ).convert_alpha()
                for color in COLORS
                for action in ACTIONS
            },
            **{
                f'{BLACK_COLOR}_{wild}': pygame.image.load(
                    getpath(f'assets/images/cards/wilds/{BLACK_COLOR}_{wild}.png')
                ).convert_alpha()
                for wild in WILDS
            }
        }
    
    def _load_fonts(self):
        """Load all font resources."""
        self.fonts = {
            **{
                large: pygame.font.Font(
                    getpath('assets/fonts/Kenney Future.ttf'), 24
                )
                for large in self.LARGE_TEXTS
            },
            **{
                default: pygame.font.Font(
                    getpath('assets/fonts/Kenney Future.ttf'), 16
                )
                for default in self.DEFAULT_TEXTS
            },
            **{
                small: pygame.font.Font(
                    getpath('assets/fonts/Kenney Future.ttf'), 8
                )
                for small in self.SMALL_TEXTS
            },
            **{
                narrow: pygame.font.Font(
                    getpath('assets/fonts/Kenney Future Narrow.ttf'), 16
                )
                for narrow in self.NARROW_TEXTS
            },
        }
    
    def _load_sounds(self):
        """Load all sound resources."""
        self.sounds = {
            'click': pygame.mixer.Sound(
                getpath('assets/sounds/click.ogg')
            ),
            'tap': pygame.mixer.Sound(
                getpath('assets/sounds/tap.ogg')
            ),
        }

