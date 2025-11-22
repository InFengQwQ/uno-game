from .settings import *
from .ui import *
from .network import *
from .game_rules import *

__all__ = [
    # Screen settings
    'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'W', 'H', 'FPS',
    # Main loop intervals
    'RUN_INTERVAL', 'ROOM_UPDATE_INTERVAL', 'ROOM_RECEIVE_INTERVAL',
    # UI settings
    'WINDOW_TITLE', 'WINDOW_ICON_SIZE',
    'KEY_REPEAT_DELAY', 'KEY_REPEAT_INTERVAL',
    'MESSAGE_BOX_WIDTH', 'MESSAGE_BOX_HEIGHT', 'MESSAGE_BOX_TOP_MARGIN',
    'MESSAGE_TEXT_LEFT_MARGIN', 'MESSAGE_DISPLAY_TIME',
    'UI_ELEMENT_PADDING',
    # Network settings
    'MULTICAST_GROUP', 'MULTICAST_PORT', 'HOST_PORT_RANGE',
    'BUFFER_SIZE', 'SOCKET_TIMEOUT', 'ROOM_CAPACITY',
    # Game rules
    'INITIAL_HAND_SIZE', 'MIN_PLAYERS', 'MAX_PLAYERS',
]

