from . import Room
import json, socket, time    # threading 仅用于测试，类定义中不用
from typing import Any
# TODO: 各种socket报错处理

class Host:
    def __init__(self, name: str, room_name: str, password: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in range(50001, 51000):
            try:
                self.sock.bind(('0.0.0.0', port))
                self.port = port
                break
            except OSError:
                continue
        self.sock.listen(10)
        self.sock.setblocking(False)
        self.connections: dict[str, socket.socket] = {}

        self.name = name
        self.room = Room(room_name, password)

        self.actions: list[dict[str, Any]] = []   # [{player, type, ...}]

    def broadcast(self):    # 持续广播房间信息，间隔一秒
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while self.room.status == 0:
                info: dict[str, Any] = {
                    'port': self.port,
                    'name': self.room.name,
                    'number': len(self.connections)
                }
                sock.sendto(json.dumps(info).encode(), ('255.255.255.255', 50000))
                time.sleep(1)

    def admit(self):    # 持续接收玩家
        while self.room.status == 0:
            if len(self.connections) < 10:
                try:
                    conn, _ = self.sock.accept()
                except BlockingIOError:
                    continue
                else:
                    conn.settimeout(1)
                    request: dict[str, Any] = json.loads(conn.recv(1024).decode())
                    if request['password'] == self.room.password:
                        names = list(self.connections.keys()) + [self.name]
                        if (name := request['name']) in names:    # 重名
                            conn.close()
                        else:
                            self.connections[name] = conn
                            conn.send(json.dumps(names).encode())
                    else:
                        conn.close()

    def action(self):   # 持续接收玩家行为
        while self.room.status == 1:
            for conn in self.connections.values():
                conn.setblocking(False)
                try:
                    action: dict[str, Any] = json.loads(conn.recv(1024).decode())
                except BlockingIOError:
                    continue
                else:
                    self.actions.append(action)

    def sync(self, action: dict[str, Any]): # 同步广播行为，在每次动画加载前执行
        for conn in self.connections.values():
            if conn != self.connections[action['player']]:
                conn.send(json.dumps(action).encode())