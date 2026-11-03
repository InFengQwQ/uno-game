from enum import IntEnum, StrEnum
from typing import Any

__all__ = [
    'RoomStatus', 'ActionType',
    'InfoDict', 'JsonMessage'
]


class RoomStatus(IntEnum):
    WAITING = 0
    ONGOING = 1

class ActionType(StrEnum):
    PLAY = 'play'
    DRAW = 'draw'
    CHALLENGE = 'challenge'
    CATCH = 'catch'


# Json serializable
InfoDict = dict[str, Any]
JsonMessage = dict[str, InfoDict]
