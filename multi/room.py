from . import MULTICAST_GROUP, MULTICAST_PORT, BUFFER_SIZE
import json, socket
# TODO: 一个房间关闭之后，rooms列表中会保留，这是个问题，应该在主机关闭时删除

class Room:
    RoomInfo = dict[str, str | tuple[str, int] | list[str]]
    rooms: list[RoomInfo] = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', MULTICAST_PORT))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.setblocking(False)

    def __init__(self, name: str, password: int, addr: tuple[str, int]):
        self.password = password

        self.name = name
        self.addr = addr
        self.players: list[str] = []

    @property
    def info(self) -> RoomInfo:
        return {
            'name': self.name,
            'addr': self.addr,
            'players': self.players,
        }

    def broadcast(self):
        """Broadcast room information to the multicast group."""

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
                sock.sendto(json.dumps(self.info).encode(), (MULTICAST_GROUP, MULTICAST_PORT))
        except OSError:
            pass

    @classmethod
    def receive(cls):
        """Receive room information from the multicast group."""

        while True:
            try:
                data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
            except BlockingIOError:
                break
            else:
                rooms = {info['addr']: info for info in cls.rooms}
                info = json.loads(data.decode())
                port = info['addr'][1]
                info['addr'] = (ip, port)
                rooms[info['addr']] = info
                cls.rooms[:] = sorted(list(rooms.values()), key=lambda info: info['name'])