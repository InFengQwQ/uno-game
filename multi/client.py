"""Manages the client side of a multiplayer UNO game."""

import socket
from typing import Optional

from config import BUFFER_SIZE, SOCKET_TIMEOUT
from .constants import (
    ROOM_ONGOING, ROOM_WAITING
)
from .utils import (
    to_bytes, from_stream,
    Info, Request, Response,
    SocketClosedMessage, GameStartedMessage, GameEndedMessage
)
from .room import Room


class Client:
    """Manages the client side of a multiplayer UNO game."""

    room: Optional[Room] = None

    def __init__(self, name: str):
        if not 0 < len(name) < BUFFER_SIZE / 32:
            raise ValueError(
                "Name is empty or too long"
            )

        self.name = name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close(self, reason: Exception | str = ''):
        """
        Close the client connection and raise a SocketClosedMessage.

        Args:
            reason: The reason for closing the connection.
        """
        self.sock.close()
        self.room = None
        raise SocketClosedMessage(reason)

    def join(self, info: Info, password: int):
        """Join a room."""
        self.sock.settimeout(SOCKET_TIMEOUT)
        try:
            self.sock.connect(info.addr)
        except TimeoutError as e:
            raise TimeoutError(
                "Timeout or game is ongoing"
            ) from e
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                "Host is busy or room does not exist"
            ) from e
        else:
            request = Request(self.name, password)
            try:
                self.sock.send(to_bytes(request.to_dict()))
            except ConnectionError as e:
                self.close(e)
            else:
                try:
                    data = self.sock.recv(BUFFER_SIZE)
                except TimeoutError as e:
                    self.close(e)
                except ConnectionError as e:
                    self.close(e)
                else:
                    for obj in from_stream(data):
                        response = Response.from_dict(obj)
                        if response.status:
                            self.sock.setblocking(False)
                            self.room = Room(info.name, password, info.addr)
                        else:
                            self.close(response.message)

    def sync(self):
        """
        Synchronize the client state with the host.
        """
        assert self.room

        try:
            if not self.sock.recv(1, socket.MSG_PEEK):
                self.close(
                    "Host has closed the connection"
                )
        except BlockingIOError:
            pass
        except ConnectionError:
            self.close(
                "Failed to connect to the host"
            )

        if info := Room.rooms.get(self.room.addr):
            self.room.players[:] = info.players
            if (
                info.status is ROOM_ONGOING and
                self.room.status is ROOM_WAITING
            ):
                self.room.status = ROOM_ONGOING
                raise GameStartedMessage
            elif (
                info.status is ROOM_WAITING and
                self.room.status is ROOM_ONGOING
            ):
                self.room.status = ROOM_WAITING
                raise GameEndedMessage

    def go(self):
        """Start playing the game."""
        assert self.room

        pass

    def run(self):
        """Run the client to synchronize and start the game if ongoing."""
        assert self.room

        self.sync()
        if self.room.status is ROOM_ONGOING:
            self.go()
