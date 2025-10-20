from . import Room
import json, socket
from typing import Any
# socket udp组播地址：239.255.0.0:50000 局域网使用

class Client:
    def __init__(self, name: str, sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.name = name
        self.sock = sock
        self.room: Room

        self.actions: list[dict[str, Any]] = []

    def join(self, info: dict[str, Any], password: int):
        name, addr = info['name'], info['addr']
        self.sock.connect(addr)
        request: dict[str, Any] = {
            'name': self.name,
            'password': password
        }
        self.sock.send(json.dumps(request).encode())
        reply = json.loads(self.sock.recv(1024).decode())
        if reply['status']:
            self.sock.setblocking(False)
            self.room = Room(name, password, addr)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raise Exception(reply['message']) # Message()

    # @property
    # def connected(self):
    #     try:
    #         self.sock.recv(0)?
    #     except Exception as e:  # 问题是如果缓冲区满，即使连接健康也可能报False
    #         print(e)
    #         return False
    #     else:
    #         return True

    def sync(self): # 同步，兼分数结算(此时打破循环)
        try:
            info = json.loads(self.sock.recv(1024).decode())
        except BlockingIOError:
            pass
        else:
            self.room.players[:] = info['players']

        # try:
        #     self.actions.append(json.loads(self.sock.recv(1024).decode()))
        # except:
        #     pass