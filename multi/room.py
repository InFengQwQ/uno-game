import socket

from .constants import (
    MULTICAST_GROUP, MULTICAST_PORT,
    BUFFER_SIZE,
    ROOM_WAITING
)
from .utils import (
    to_bytes, from_packet,
    Info
)


class Room:
    """A room in the multiplayer game."""

    buffer: list[Info] = []
    rooms: dict[tuple[str, int], Info] = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.bind(('0.0.0.0', MULTICAST_PORT))
    sock.setblocking(False)

    def __init__(self, name: str, password: int, addr: tuple[str, int]):
        self.name = name
        self.password = password
        self.addr = self.ip, self.port = addr

        self.players: list[str] = []
        self.status = ROOM_WAITING

    def broadcast(self):
        """Broadcast room information to the multicast group."""

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(to_bytes(Info(self.name, self.addr, self.players, self.status).to_dict()), (MULTICAST_GROUP, MULTICAST_PORT))

    @classmethod
    def receive(cls):
        """Receive room information from the multicast group."""

        while True:
            try:
                data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
            except BlockingIOError:
                break
            else:
                if obj := from_packet(data):
                    info = Info.from_dict(obj, ip)
                    cls.buffer.append(info)

    @classmethod
    def update(cls):
        """Merge room information from the buffer and update the rooms list."""

        cls.rooms.clear()
        while cls.buffer:
            info = cls.buffer.pop(0)
            cls.rooms[info.addr] = info