from . import Room
import json, socket, time
from typing import Any
# socket udp组播地址：239.255.0.0:50000 局域网使用

class Client:
    def __init__(self, name: str, sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.name = name
        self.sock = sock
        self.room: Room

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
                    info = json.loads(data.decode())
                    addr = info['addr'] = (ip, info['addr'][1])
                    rooms[addr] = info
                except BlockingIOError:
                    continue
                except:
                    break
        return list(rooms.values())

    def join(self, info: dict[str, Any], password: int):
        addr: Any = info['addr']
        self.sock.connect(addr)
        request: dict[str, Any] = {
            'name': self.name,
            'password': password
        }
        self.sock.send(json.dumps(request).encode())
        try:
            self.sock.recv(1024)
        except:
            return False
        else:
            self.room = Room(info['name'], password, info['addr'])
            return True

    def sync(self): # 同步，兼分数结算(此时打破循环)
        while True:
            pass