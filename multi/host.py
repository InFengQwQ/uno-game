from . import Client, Room
import json, socket    # threading 仅用于测试，类定义中不用
from typing import Any
# TODO: 各种socket报错处理

class Host:
    def __init__(self, name: str, room_name: str, password: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        for port in range(50001, 51000):    # 同一设备可尝试占用999个端口用作游戏（TCP）
            try:
                self.sock.bind(('0.0.0.0', port))
            except OSError:
                continue
            else:
                break
        else:
            raise OSError
        self.sock.listen(10)
        sock, client_sock = socket.socketpair(socket.AF_INET, socket.SOCK_STREAM)
        self.connections: dict[str, socket.socket] = {name: sock}
        self.client = Client(name, client_sock)
        self.client.room = Room(room_name, password, ('127.0.0.1', port))

        self.actions: list[dict[str, Any]] = []   # TODO: [{player, type, ...}]

    def wait(self): # 一次健康的等待操作
        def admit():    # 接收玩家一次
            if len(self.connections) < 10:
                while True:
                    try:
                        conn, _ = self.sock.accept()
                    except BlockingIOError:
                        break
                    else:
                        conn.settimeout(1)
                        try:
                            request = json.loads(conn.recv(1024).decode())
                            if request['password'] == self.client.room.password and not (name := request['name']) in self.connections: # 游戏外重名
                                self.connections[name] = conn
                                conn.send(b'')
                            else:
                                raise ValueError('failed to identify')
                        except Exception as e:
                            print(e)
                            conn.close()

        def sync(): # 同步房间成员
            self.client.room.players[:] = list(self.connections)

            connections = self.connections.copy()
            for name, conn in self.connections.items():
                try:
                    conn.send(json.dumps(self.client.room.info).encode())
                except Exception:
                    conn.close()
                    del connections[name]
            self.connections.clear()
            self.connections.update(connections)

        sync()
        self.client.room.broadcast()
        admit()

    def go(self):
        def action():   # 持续接收玩家行为
            for conn in self.connections.values():
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