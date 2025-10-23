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
        # Always use TCP loopback to create a connected socket pair
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(listener.getsockname())
        sock, _ = listener.accept()
        listener.close()
        self.connections: dict[str, dict[str, socket.socket]] = {'unverified': {}, 'verified': {name: sock}}
        self.client = Client(name, client_sock)
        self.client.room = Room(room_name, password, ('127.0.0.1', port))

        self.actions: list[dict[str, Any]] = []   # TODO: [{player, type, ...}]

    def wait(self): # 一次健康的等待操作    TODO: 完善所有的处理
        def admit():    # 接收玩家一次
            while len(self.connections['verified']) + len(self.connections['unverified']) < 10:
                try:
                    conn, _ = self.sock.accept()
                except BlockingIOError:
                    break
                else:
                    conn.setblocking(False)
                    self.connections['unverified'][conn.getpeername()] = conn

        def sync(): # 同步房间成员
            for addr, conn in self.connections['unverified'].copy().items():
                try:
                    request = json.loads(conn.recv(1024).decode())
                except BlockingIOError:
                    continue
                except Exception as e:
                    print(e)
                    conn.close()
                else:
                    if (name := request['name']) in self.connections['verified']: # 游戏外重名
                        conn.send(json.dumps({'status': False, 'message': 'NAME EXISTS'}).encode())
                        conn.close()
                    elif request['password'] != self.client.room.password:
                        conn.send(json.dumps({'status': False, 'message': 'PASSWORD INCORRECT'}).encode())
                        conn.close()
                    else:
                        conn.send(json.dumps({'status': True}).encode())
                        self.connections['verified'][name] = conn
                    del self.connections['unverified'][addr]

            self.client.room.players[:] = list(self.connections['verified'])
            for name, conn in self.connections['verified'].copy().items():
                try:
                    conn.send(json.dumps(self.client.room.info).encode())
                except Exception as e:
                    print(e)
                    conn.close()
                    del self.connections['verified'][name]   # 是否要直接删除？不过确实socket失效之后已经没必要存储了

        admit()
        sync()
        self.client.room.broadcast()

    def go(self):
        def action():   # 持续接收玩家行为
            for conn in self.connections['verified'].values():
                try:
                    action: dict[str, Any] = json.loads(conn.recv(1024).decode())
                except BlockingIOError:
                    continue
                else:
                    self.actions.append(action)

        def sync(): # 同步广播行为，在每次动画加载前执行
            for action in self.actions:
                for conn in self.connections['verified'].values():
                    if conn != self.connections['verified'][action['player']]:
                        conn.send(json.dumps(action).encode())

        action()
        sync()