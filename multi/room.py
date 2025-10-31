from . import MULTICAST_GROUP, MULTICAST_PORT, BUFFER_SIZE, to_stream, from_stream
import socket
# TODO: 一个房间关闭之后，rooms列表中会保留，这是个问题，应该在主机关闭时删除

class Room:
    """A room in the multiplayer game."""

    class Info:
        """A room information as a dictionary."""

        def __init__(self, name: str, addr: tuple[str , int], players: list[str]):
            self.name = name
            self.addr = self.ip, self.port = addr
            self.players = players

        def __hash__(self):
            return hash(self.addr)

        def __eq__(self, other: object):
            if isinstance(other, Room.Info):
                return self.addr == other.addr
            else:
                return NotImplemented

        def __lt__(self, other: object):
            if isinstance(other, Room.Info):
                return self.name < other.name
            else:
                return NotImplemented

        def to_dict(self) -> dict[str, str | int | list[str]]:
            return {
                'name': self.name,
                'ip': self.ip,
                'port': self.port,
                'players': self.players
            }

        @classmethod
        def from_dict(cls, d: dict[str, str | int | list[str]]):
            name = d['name'] if isinstance(d['name'], str) else None
            addr = (d['ip'], d['port']) if isinstance(d['ip'], str) and isinstance(d['port'], int) else None
            players = d['players'] if isinstance(d['players'], list) else None
            if name and addr and players:
                return cls(name, addr, players)
            else:
                raise Exception('Invalid room information.')

    rooms: set[Info] = set()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.bind(('0.0.0.0', MULTICAST_PORT))
    sock.setblocking(False)

    def __init__(self, name: str, password: int, addr: tuple[str, int]):
        self.password = password
        self.name = name
        self.addr = self.ip, self.port = addr

        self.players: list[str] = []

    @property
    def info(self):
        return Room.Info(self.name, self.addr, self.players).to_dict()

    def broadcast(self):
        """Broadcast room information to the multicast group."""

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(to_stream(self.info), (MULTICAST_GROUP, MULTICAST_PORT))

    @classmethod
    def receive(cls):
        """Receive room information from the multicast group."""

        try:
            data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
        except BlockingIOError:
            pass
        else:
            for d in from_stream(data):
                info = Room.Info.from_dict(d)
                _, port = info.addr
                info.addr = ip, port
                cls.rooms.add(info)