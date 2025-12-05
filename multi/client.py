"""The client side of a multiplayer UNO game."""

import socket
from typing import Optional

from config import BUFFER_SIZE, SOCKET_TIMEOUT
from .constants import (
    ROOM_ONGOING, ROOM_WAITING,
    JsonMessage
)
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage, GameStartedMessage, GameEndedMessage
)
from .room import Room


class Client:
    """The client side of a multiplayer UNO game."""
    def __init__(self, name: str):
        if not 0 < len(name) < BUFFER_SIZE / 32:
            raise ValueError(
                "Name is empty or too long"
            )

        self.name = name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages: JsonMessage = {}
        self.room: Optional[Room] = None

    def close(self, reason: Exception = Exception()):
        """Close the client connection,
        and raise a SocketClosedMessage.

        Args:
            reason: The reason for closing the connection.
        """
        self.sock.close()
        self.room = None
        raise SocketClosedMessage(reason)

    def send(self, msg: JsonMessage):
        """Send a message."""
        try:
            self.sock.send(to_bytes(msg))
        except OSError as e:
            self.close(reason=e)

    def recv(self):
        """Receive data and update the messages dictionary."""
        try:
            if not (data := self.sock.recv(BUFFER_SIZE)):
                raise ConnectionError(
                    "Host has closed the connection"
                )
        except (TimeoutError, ConnectionError) as e:
            self.close(reason=e)
        except BlockingIOError:
            pass
        else:
            self.messages.update(from_stream(data))

    def extract(self, key: str):
        """Extract data from the messages dictionary."""
        self.messages.setdefault(key, {})
        return self.messages.pop(key)

    def join(self, addr: tuple[str, int], password: int):
        """Join a room."""
        self.sock.settimeout(SOCKET_TIMEOUT)
        try:
            self.sock.connect(addr)
        except TimeoutError as e:
            raise TimeoutError(
                "Timeout or game is ongoing"
            ) from e
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                "Host is busy or room does not exist"
            ) from e
        else:
            msg: JsonMessage = {'request': {
                'name': self.name,
                'password': password
            }}
            self.send(msg)
            self.sync()

    def sync(self):
        """Synchronize the client with the host."""
        self.recv()

        if response := self.extract('response'):
            if response['status']:
                self.sock.setblocking(False)
                self.room = Room(**response['room'])        # 使用重接收的房间数据
            else:
                self.close(response['message'])

        assert self.room

        if room := self.extract('room'):
            self.room.players[:] = room['players']
            if (
                room['status'] is ROOM_ONGOING and
                self.room.status is ROOM_WAITING
            ):
                self.room.status = ROOM_ONGOING
                raise GameStartedMessage
            elif (
                room['status'] is ROOM_WAITING and
                self.room.status is ROOM_ONGOING
            ):
                self.room.status = ROOM_WAITING
                raise GameEndedMessage

    def go(self):
        """Handle game messages."""
        assert self.room

    def run(self):
        """Run the client."""
        assert self.room

        self.sync()
        if self.room.status is ROOM_ONGOING:
            self.go()
