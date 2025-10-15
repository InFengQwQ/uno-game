from . import Client, Room
import json, socket    # threading 仅用于测试，类定义中不用
from typing import Any
# TODO: 各种socket报错处理

class Host:
    def __init__(self, name: str, room_name: str, password: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in range(50001, 51000):    # 同一设备可尝试占用999个端口用作游戏（TCP）
            try:
                self.sock.bind(('0.0.0.0', port))
            except OSError:
                continue
            else:
                self.sock.listen(10)
                self.sock.settimeout(1)
                sock, client_sock = socket.socketpair(socket.AF_INET, socket.SOCK_STREAM)
                self.connections: dict[str, socket.socket] = {name: sock}
                self.client = Client(name, client_sock)
                self.client.room = Room(room_name, password, ('127.0.0.1', port))
                break
        else:
            raise OSError

        self.actions: list[dict[str, Any]] = []   # TODO: [{player, type, ...}]

    def wait(self):
        def broadcast():    # 向239.255.0.0:50000的组广播房间信息一次
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(json.dumps(self.client.room.info).encode(), ('239.255.0.0', 50000))

        def admit():    # 接收玩家一次（已设置1秒超时）
            if len(self.connections) < 10:
                while True:
                    try:
                        conn, _ = self.sock.accept()
                    except TimeoutError:
                        break
                    else:
                        try:
                            request = json.loads(conn.recv(1024).decode())
                            if request['password'] == self.client.room.password and not (name := request['name']) in self.connections: # 游戏外重名
                                self.connections[name] = conn
                                conn.send(b'')
                            else:
                                raise ValueError
                        except:
                            conn.close()

        while self.client.room.status == 0:
            self.client.room.players = list(self.connections)
            print(self.connections)
            print(self.client.room.players)
            broadcast()
            admit()

    def go(self):
        def action():   # 持续接收玩家行为
            for conn in self.connections.values():
                conn.setblocking(False)
                try:
                    action: dict[str, Any] = json.loads(conn.recv(1024).decode())
                except BlockingIOError:
                    continue
                else:
                    self.actions.append(action)

        def sync(): # 同步广播行为，在每次动画加载前执行
            for action in self.actions:
                for conn in self.connections.values():
                    if conn != self.connections[action['player']]:
                        conn.send(json.dumps(action).encode())

        while self.client.room.status == 1:
            action()
            sync()