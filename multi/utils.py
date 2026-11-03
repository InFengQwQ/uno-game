import json
from typing import Any

from config import BUFFER_SIZE

from .constants import JsonMessage

__all__ = [
    'to_bytes', 'from_package', 'from_stream',
    'SocketClosedMessage', 'GameBeginMessage', 'GameEndedMessage'
]


def to_bytes(obj: object) -> bytes:
    """Convert a json serializable object to a byte string."""
    data = (json.dumps(obj) + '\n').encode()
    assert len(data) <= BUFFER_SIZE
    return data

def from_package(b: bytes) -> Any:
    """Convert a package to a json serializable object."""
    try:
        return json.loads(b.decode())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

def from_stream(b: bytes) -> tuple[JsonMessage, int]:
    """Convert stream to a json message."""
    msgs: JsonMessage = {}
    data = b''
    span = 0
    for byte in b:
        data += bytes((byte,))
        try:
            msgs.update(json.loads(data))
        except (UnicodeDecodeError, json.JSONDecodeError): ...
        else:
            span += len(data)
            data = b''
    return msgs, span

class SocketClosedMessage(Exception):
    """Stack trace of the exception."""

class GameBeginMessage(Exception):
    """Stack trace of the exception."""

class GameEndedMessage(Exception):
    """Stack trace of the exception."""
