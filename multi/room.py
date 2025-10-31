from . import MULTICAST_GROUP, MULTICAST_PORT, BUFFER_SIZE, to_bytes, from_packet, Info
import socket
# TODO: 一个房间关闭之后，rooms列表中会保留，这是个问题，应该在主机关闭时删除

class Room:
    """A room in the multiplayer game."""

    rooms: set[Info] = set()

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

    def broadcast(self):
        """Broadcast room information to the multicast group."""

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(to_bytes(Info(self.name, self.addr, self.players).to_dict()), (MULTICAST_GROUP, MULTICAST_PORT))

    @classmethod
    def receive(cls):
        """Receive room information from the multicast group."""

        try:
            data, (ip, _) = cls.sock.recvfrom(BUFFER_SIZE)
        except BlockingIOError:
            pass
        else:
            if obj := from_packet(data):
                if info := Info.from_dict(obj, ip):
                    cls.rooms.add(info)