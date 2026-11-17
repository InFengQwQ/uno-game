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

def from_stream(b: bytes) -> tuple[list[JsonMessage], int]:
    """Convert a newline-delimited stream to json messages."""
    messages = list[JsonMessage]()
    span = 0

    while (sep := b.find(b'\n', span)) != -1:
        try:
            _message: JsonMessage = json.loads(b[span:sep].decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        else:
            messages.append(_message)
        finally:
            span = sep + 1

    return messages, span

class SocketClosedMessage(Exception):
    """Stack trace of the exception."""

class GameBeginMessage(Exception):
    """Stack trace of the exception."""

class GameEndedMessage(Exception):
    """Stack trace of the exception."""
