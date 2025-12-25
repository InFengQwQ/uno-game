"""A module to manage multiplayer game rooms using multicast networking."""

import socket
from typing import ClassVar

from config import MULTICAST_GROUP, MULTICAST_PORT, BUFFER_SIZE
from .constants import (
    ROOM_WAITING
)
from .utils import (
    to_bytes, from_package,
    RoomInfo
)


class Room:
    """A room in the multiplayer game."""
    
    # Class-level shared data for room discovery
    rooms: ClassVar[dict[tuple[str, int], RoomInfo]] = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(
        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    )
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.bind(('0.0.0.0', MULTICAST_PORT))
    sock.setblocking(False)

    def __init__(self, name: str, password: int, port: int):
        """Initialize a room.
        
        Args:
            name: Room name
            password: Room password
            port: Port number for the room
        """
        self.name = name
        self.password = password
        self.port = port

        self.players: list[str] = []
        self.status = ROOM_WAITING

    def broadcast(self) -> None:
        """Broadcast room information to the multicast group."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            info = RoomInfo(
                self.name,
                self.port,
                self.players,
                self.status
            ).to_dict()
            sock.sendto(to_bytes(info), (MULTICAST_GROUP, MULTICAST_PORT))

    @classmethod
    def recv(cls) -> None:
        """Receive room information from the multicast group."""
        cls.rooms.clear()
        while True:
            try:
                data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
            except BlockingIOError:
                break
            else:
                if info := from_package(data):
                    cls.rooms[(ip, info['port'])] = RoomInfo.from_dict(info)
