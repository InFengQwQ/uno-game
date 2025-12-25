"""Utility functions for handling messages."""

import json
from typing import Any, Optional

from .constants import InfoDict, JsonMessage, Action


def to_bytes(obj: object) -> bytes:
    """Convert a json serializable object to a byte string.
    
    Args:
        obj: Any JSON-serializable object
        
    Returns:
        UTF-8 encoded JSON bytes
    """
    try:
        return json.dumps(obj).encode()
    except json.JSONDecodeError:
        return b''


def from_stream(b: bytes) -> JsonMessage:
    """Convert stream to a json message.
    
    Args:
        b: Bytes from network stream
        
    Returns:
        Dictionary of parsed JSON messages
    """
    data = ''
    result: JsonMessage = {}
    for c in b.decode():
        data += c
        try:
            result.update(json.loads(data))
        except json.JSONDecodeError:
            pass
        else:
            data = ''
    return result


def from_package(b: bytes) -> Optional[dict]:
    """Convert a package to a json serializable object.
    
    Args:
        b: Bytes from network package
        
    Returns:
        Parsed JSON object or None if invalid
    """
    try:
        return json.loads(b.decode())
    except json.JSONDecodeError:
        return None


def create_action_message(action: Action, data: Optional[InfoDict] = None) -> JsonMessage:
    """Create a standardized action message.
    
    Args:
        action: The action type
        data: Optional data payload for the action
        
    Returns:
        Formatted action message
    """
    message: JsonMessage = {
        'action': {
            'type': action.value,
            'data': data or {}
        }
    }
    return message


def create_error_message(error: str, details: Optional[str] = None) -> JsonMessage:
    """Create a standardized error message.
    
    Args:
        error: Error message
        details: Optional detailed error information
        
    Returns:
        Formatted error message
    """
    return {
        'error': {
            'message': error,
            'details': details or ''
        }
    }


def create_state_sync_message(game_state: InfoDict) -> JsonMessage:
    """Create a game state synchronization message.
    
    Args:
        game_state: Complete game state data
        
    Returns:
        Formatted state sync message
    """
    return {
        'state': game_state
    }


class RoomInfo():
    """RoomInfo class."""
    
    def __init__(
        self,
        name: str,
        port: int,
        players: list[str],
        status: int
    ):
        """Initialize room information.
        
        Args:
            name: Room name
            port: Room port number
            players: List of player names in the room
            status: Room status (ROOM_WAITING or ROOM_ONGOING)
        """
        self.name = name
        self.port = port
        self.players = players
        self.status = status

    def to_dict(self) -> InfoDict:
        """Convert to a info dictionary.
        
        Returns:
            Dictionary representation of room info
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'RoomInfo':
        """Convert from a info dictionary.
        
        Args:
            value: Dictionary containing room info
            
        Returns:
            RoomInfo instance
        """
        return cls(**value)


class SocketClosedMessage(Exception):
    """Exception raised when socket connection is closed."""
    pass


class GameStartedMessage(Exception):
    """Exception raised when game starts."""
    pass


class GameEndedMessage(Exception):
    """Exception raised when game ends."""
    pass
