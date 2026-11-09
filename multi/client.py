import socket
from typing import Any, Optional

from config import BUFFER_SIZE, SOCKET_TIMEOUT

from .constants import *
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage, GameBeginMessage, GameEndedMessage
)
from .room import Room
from .mirror import Mirror

__all__ = ['Client']


class Client:
    """Client of a room.

    Attributes:
        name: Name of the player.

        room: Room of the client.
        mirror: Game info mirror.
    """
    def __init__(self, name: str):
        if not 0 < len(name) <= 7:
            raise ValueError("Name is empty or too long")

        self.name = name

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(SOCKET_TIMEOUT)
        self._messages: JsonMessage = {}

        self.room: Optional[Room] = None
        self.mirror: Optional[Mirror] = None

        self._token: str
        self._target: tuple[tuple[str, int], str]

    def close(self, reason: Exception = Exception()):
        self.room = None
        self._sock.close()
        raise SocketClosedMessage(reason) from reason

    def join(self, addr: tuple[str, int], password: str):
        """Connect and send a request to a room."""
        try:
            self._target = (addr, password)
            self._sock.connect(addr)
        except TimeoutError as e:
            raise TimeoutError(
                "Timeout or game is ongoing"
            ) from e
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                "Host is busy or room does not exist"
            ) from e
        except OSError as e:
            self.close(e)
        else:
            self.send({
                'request': {# request
                    'name': self.name,
                    'password': password
                }
            })
            self.recv()

            if response := self._messages.pop('response', None): # response
                if response['status']:
                    self.room = Room(**response['room'])
                    self._sock.setblocking(False)

                    self._token = response['token']
                else:
                    self.close(OSError(
                        response['message']
                    ))

    def reconnect(self):
        """Reconnect to the room."""
        assert self.room

        self._sock.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(SOCKET_TIMEOUT)
        self._messages.clear()

        addr, password = self._target
        self._sock.connect(addr)
        self._sock.sendall(to_bytes({
            'request': {# request
                'name': self.name,
                'password': password,
                'token': self._token
            }
        }))
        messages, end = from_stream(
            self._sock.recv(BUFFER_SIZE, socket.MSG_PEEK)
        )
        response = messages[0].get('response') if messages else None
        if not (end and response and response['status']): raise OSError
        self._sock.recv(end)
        self._sock.setblocking(False)

        self._token = response['token']

    def send(self, msg: JsonMessage):
        try:
            if self._sock.send(data := to_bytes(msg)) != len(data): raise OSError
        except OSError as e:
            try:
                self.reconnect()
            except OSError:
                self.close(e)

    def recv(self):
        try:
            peeked = self._sock.recv(BUFFER_SIZE, socket.MSG_PEEK)
            if not peeked:
                self.close(OSError(
                    "Connection is closed by the host"
                ))
            messages, end = from_stream(peeked)
            if not end:
                return
            self._sock.recv(end)
        except BlockingIOError: ...
        except OSError as e:
            try:
                self.reconnect()
            except OSError:
                self.close(e)
            return
        else:
            for jm in messages:
                self._messages.update(jm)

    def sync(self):
        """Synchronize message with the host."""
        assert self.room

        if game := self._messages.pop('game', None): # game
            snapshot = Mirror.from_dict(game)
            if mirror := self.mirror:
                mirror.update(snapshot)
            else:
                self.mirror = snapshot
                self.room.status = RoomStatus.ONGOING
                raise GameBeginMessage
        if room := self._messages.pop('room', None): # room
            self.room.players[:] = room['players']
            if self.room.status == RoomStatus.ONGOING:
                self.mirror = None
                self.room.status = room['status']
                raise GameEndedMessage
            self.room.status = room['status']

    def action(self, type: ActionType, **kwargs: Any):
        """Perform action."""
        if type in (ActionType.DRAW, ActionType.CHALLENGE, ActionType.CATCH):
            assert not kwargs
        elif type == ActionType.PLAY:
            assert 'card' in kwargs and 'uno' in kwargs
        self.send({
            'action': {# action
                'type': type.value,
                **kwargs
            }
        })

    def result(self):
        """Archive action."""
        if reply := self._messages.pop('reply', None): # reply
            if reply['status']:
                if reply.get('hand'):
                    pass    # TODO: 得到被质疑者手牌
            else:
                raise OSError(
                    reply['message']
                )

    def run(self):
        """Run the client role."""
        assert self.room
        self.recv()

        if self.room.status == RoomStatus.WAITING: ...
        if self.room.status == RoomStatus.ONGOING: self.result()

        self.sync()
