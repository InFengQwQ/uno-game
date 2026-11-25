import socket
from typing import Any, Optional

from config import BUFFER_SIZE, SOCKET_TIMEOUT

from .constants import *
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage, GameBeginMessage, GameEndedMessage,
    HandShownMessage
)
from .room import Room
from .mirror import (
    CardInfo,
    Mirror
)

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
        """Try to join a room.

        Args:
            addr: Address of target.
            password: Password of target.

        Raises:
            TimeoutError: Socket timeout.
            ConnectionRefusedError: Host rejection.
        """
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
                'request': {
                    'name': self.name,
                    'password': password
                }
            })

            data = b''
            while 'response' not in self._messages:
                if not (chunk := self._sock.recv(BUFFER_SIZE)):
                    raise OSError(
                        "Connection is closed by the host"
                    )

                data += chunk
                messages, end = from_stream(data)
                data = data[end:]

                for jm in messages:
                    self._messages.update(jm)

            response = self._messages.pop('response')
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
            'request': {
                'name': self.name,
                'password': password,
                'token': self._token
            }
        }))

        data = b''
        while 'response' not in self._messages:
            if not (chunk := self._sock.recv(BUFFER_SIZE)):
                raise OSError

            data += chunk
            messages, end = from_stream(data)
            data = data[end:]

            for jm in messages:
                self._messages.update(jm)

        response = self._messages.pop('response')
        if response['status']:
            self._sock.setblocking(False)
            self._token = response['token']
        else:
            raise OSError

    def send(self, msg: JsonMessage):
        try:
            if self._sock.send(data := to_bytes(msg)) != len(data): raise OSError
        except OSError as e:
            self.close(Exception(str(e) or
                "Failed to send data to the host"
            ))

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
        else:
            for jm in messages:
                self._messages.update(jm)

    def sync(self):
        assert self.room

        if game := self._messages.pop('game', InfoDict()):
            snapshot = Mirror.from_dict(game)
            if mirror := self.mirror:
                mirror.update(snapshot)
            else:
                self.mirror = snapshot
                self.room.status = RoomStatus.ONGOING
                raise GameBeginMessage
        if room := self._messages.pop('room', InfoDict()):
            self.room.players[:] = room['players']
            if self.room.status == RoomStatus.ONGOING:
                self.mirror = None
                self.room.status = room['status']
                raise GameEndedMessage
            self.room.status = room['status']

    def action(self, type: ActionType, **kwargs: Any):
        """Perform action.

        Args:
            type: One of the action types.
            kwargs: Other arguments.
        """
        if type in (ActionType.DRAW, ActionType.CHALLENGE, ActionType.CATCH):
            assert not kwargs
        elif type == ActionType.PLAY:
            assert 'card' in kwargs and 'uno' in kwargs
        self.send({
            'action': {
                'type': type.value,
                **kwargs
            }
        })

    def result(self):
        """Archive action.

        Raises:
            OSError: If the action is invalid.
        """
        def hint(reply: InfoDict):
            hand = [
                CardInfo.from_dict(card)
                for card in reply['hand']
            ]
            raise HandShownMessage(hand)
        if reply := self._messages.pop('reply', InfoDict()):
            if reply['status']: 
                hint(reply) if 'hand' in reply else None
            else:
                raise OSError(
                    reply['message']
                )

    def run(self):
        assert self.room
        self.recv()

        if self.room.status == RoomStatus.WAITING: ...
        if self.room.status == RoomStatus.ONGOING: self.result()

        self.sync()
