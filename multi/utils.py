"""Utility functions for handling messages."""

import json

from .constants import InfoDict, JsonMessage

def to_bytes(obj: object) -> bytes:
    """Convert a json serializable object to a byte string."""
    try:
        return json.dumps(obj).encode()
    except json.JSONDecodeError:
        return b''

def from_stream(b: bytes) -> JsonMessage:
    """Convert stream to a json message."""
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

def from_package(b: bytes):
    """Convert a package to a json serializable object."""
    try:
        return json.loads(b.decode())
    except json.JSONDecodeError:
        return None

class RoomInfo():
    """RoomInfo class."""
    def __init__(
        self,
        name: str,
        port: int,
        players: list[str],
        status: int
    ):
        self.name = name
        self.port = port
        self.players = players
        self.status = status

    def to_dict(self) -> InfoDict:
        """Convert to a info dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'RoomInfo':
        """Convert from a info dictionary."""
        return cls(**value)


class SocketClosedMessage(Exception):
    """Stack trace of the exception."""


class GameStartedMessage(Exception):
    """Stack trace of the exception."""


class GameEndedMessage(Exception):
    """Stack trace of the exception."""
