import json, socket


class Room:
    RoomInfo = dict[str, str | tuple[str, int] | list[str]]
    rooms: list[RoomInfo] = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 50000))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton('239.255.0.0') + socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
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

    def broadcast(self):    # 向239.255.0.0:50000的组广播房间信息一次
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(json.dumps(self.info).encode(), ('239.255.0.0', 50000))

    @classmethod
    def receive(cls):  # 接收房间信息一次
        while True:
            try:
                data, (ip, _) = cls.sock.recvfrom(1024)
            except BlockingIOError:
                break
            else:
                rooms = {info['addr']: info for info in cls.rooms}
                info = json.loads(data.decode())
                addr = info['addr'] = (ip, info['addr'][1])
                rooms[addr] = info
                cls.rooms[:] = list(rooms.values())