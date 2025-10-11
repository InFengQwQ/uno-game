from . import Room
import json, socket, time
from typing import Any
# socket udp组播地址：239.255.0.0:50000+ 局域网使用

class Client:
    def __init__(self, name: str):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.name = name
        self.room: Room # TODO

        # self.actions = []

    def receive(self):  # 接收一秒内所有房间信息
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('0.0.0.0', 50000))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton('239.255.0.0') + socket.inet_aton('0.0.0.0'))
            sock.setblocking(False)

            rooms: dict[tuple[str, int], dict[str, Any]] = {}
            start_time = time.time()
            while time.time() - start_time < 1:
                try:
                    data, (ip, _) = sock.recvfrom(1024)
                    info: dict[str, Any] = json.loads(data.decode())
                    addr = (ip, info.pop('port'))
                    rooms[addr] = info
                except BlockingIOError:
                    continue
                except:
                    break
        return rooms

    def join(self, addr: tuple[str, int], name: str, password: int):   # player name and password input
        self.sock.connect(addr)
        self.sock.setblocking(False)
        request: dict[str, Any] = {
            'name': name,
            'password': password
        }
        self.sock.send(json.dumps(request).encode())
        if names := json.loads(self.sock.recv(1024).decode()):
            self.connections: list[str] = names

    def sync(self): # 同步，兼分数结算(此时打破循环)
        while True:
            pass