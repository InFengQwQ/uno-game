import socket

import psutil

from config import (
    MULTICAST_GROUP, MULTICAST_PORT,
    BUFFER_SIZE
)

from .constants import (
    RoomStatus,
    InfoDict
)
from .utils import (
    to_bytes, from_package
)

__all__ = [
    'RoomInfo',
    'Room'
]


def _iface_addrs():
    """List all IPv4 addresses of network interfaces."""
    return [
        a.address for v in psutil.net_if_addrs().values()
        for a in v if a.family == socket.AF_INET
    ]


class RoomInfo:
    """RoomInfo class for messages.

    Attributes:
        port: Port of the host.
        name: Name of the room.
        players: List of player names.
        status: As waiting or ongoing.
    """
    def __init__(self,
        port: int,
        name: str,
        players: list[str],
        status: RoomStatus, # int from json
    ):
        self.port = port
        self.name = name
        self.players = players
        self.status = status

    def to_dict(self) -> InfoDict:
        """Convert to a info dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(cls, value: InfoDict) -> 'RoomInfo':
        """Convert from a info dictionary."""
        return cls(**value)


class Room:
    """Multiplayer UNO game room.

    It uses multicast to broadcast
    name, port, players and status
    in a UDP package when waiting.

    Attributes:
        port: Linked listening port of the host.
        name: Visible room name from host input.
        password: Invisible room password from host input.

        players: List of player names.
        status: As waiting or ongoing.
    """
    rooms: dict[tuple[str, int], RoomInfo] = {}

    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    for _addr in _iface_addrs():
        try:
            _sock.setsockopt(
                socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(_addr)
            )
        except OSError: ...
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    _sock.bind(('0.0.0.0', MULTICAST_PORT))
    _sock.setblocking(False)

    def __init__(self, port: int, name: str, password: int):
        self.port = port
        self.name = name
        self.password = password

        self.players: list[str] = []
        self.status = RoomStatus.WAITING

    def broadcast(self):
        """Broadcast room information to the multicast group."""
        info = {k: v for k, v in vars(self).items() if k != 'password'}
        data = to_bytes(info)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            for addr in _iface_addrs():
                try:
                    sock.setsockopt(
                        socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                        socket.inet_aton(addr)
                    )
                    sock.sendto(data, (MULTICAST_GROUP, MULTICAST_PORT))
                except OSError: ...

    @classmethod
    def recv(cls):
        """Receive room information from the multicast group."""
        rooms = {}
        while True:
            try:
                data, (ip, _) = cls._sock.recvfrom(BUFFER_SIZE)
            except BlockingIOError:
                break
            else:
                assert (info := from_package(data))
                rooms[(ip, info['port'])] = RoomInfo.from_dict(info)

        cls.rooms = rooms
