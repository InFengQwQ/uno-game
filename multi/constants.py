"""Constants."""

from typing import Any
from enum import Enum

# Note: Network configuration has been moved to config/network.py
# Note: RUN_INTERVAL, ROOM_UPDATE_INTERVAL, ROOM_RECEIVE_INTERVAL
# have been moved to config/settings.py

# Room status (internal state constants, not configuration)
ROOM_WAITING = 0
ROOM_ONGOING = 1

# Json serializable type
InfoDict = dict[str, Any]
JsonMessage = dict[str, InfoDict]


class Action(Enum):
    """Game action types for multiplayer communication."""
    # Room management actions
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    START_GAME = "start_game"
    END_GAME = "end_game"
    
    # Game actions
    PLAY_CARD = "play_card"
    DRAW_CARD = "draw_card"
    CHALLENGE_DRAW_FOUR = "challenge_draw_four"
    CHOOSE_COLOR = "choose_color"
    SAY_UNO = "say_uno"
    
    # State sync actions
    SYNC_GAME_STATE = "sync_game_state"
    SYNC_HAND = "sync_hand"
    SYNC_TOP_CARD = "sync_top_card"
    SYNC_TURN = "sync_turn"
    
    # Error actions
    INVALID_ACTION = "invalid_action"
    ERROR = "error"
