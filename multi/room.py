from . import MULTICAST_GROUP, MULTICAST_PORT, BUFFER_SIZE
import json, socket
# TODO: 一个房间关闭之后，rooms列表中会保留，这是个问题，应该在主机关闭时删除

class Room:
    """A room in the multiplayer game."""

    class Info():
        def __init__(self, name: str, ip: str, port: int, players: list[str]):
            self.name = name
            self.addr = self.ip, self.port = ip, port
            self.players = players

        def str(self):
            return json.dumps({
                'name': self.name,
                'ip': self.ip,
                'port': self.port,
                'players': self.players
            })

        def __eq__(self, other: object):
            return isinstance(other, Room.Info) and self.name == other.name

        def __lt__(self, other: object):
            if isinstance(other, Room.Info):
                return self.name < other.name
            else:
                return NotImplemented

    rooms: dict[tuple[str, int], Info] = {}

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
        return Room.Info(self.name, self.ip, self.port, self.players)

    def broadcast(self):
        """Broadcast room information to the multicast group."""

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(str(self.info).encode(), (MULTICAST_GROUP, MULTICAST_PORT))

    @classmethod
    def receive(cls):
        """Receive room information from the multicast group."""

        while True:
            try:
                data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
            except BlockingIOError:
                break
            else:
                info = cls.Info(**json.loads(data.decode()))
                port = info.port
                info.addr = ip, port
                cls.rooms[info.addr] = info