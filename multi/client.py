from . import BUFFER_SIZE, Room
import json, socket
from typing import Any


class Client:
    def __init__(self, name: str, sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.name = name
        self.sock = sock
        self.actions: list[dict[str, Any]] = []

    def join(self, info: dict[str, Any], password: int):
        name, addr = info['name'], info['addr']
        self.sock.settimeout(5)
        try:
            self.sock.connect(addr)
        except TimeoutError:
            raise Exception("Timeout or game has been started")
        except ConnectionRefusedError:
            raise Exception("Host is busy or room does not exist")
        else:
            request: dict[str, str | int] = {
                'name': self.name,
                'password': password
            }
            try:
                self.sock.send(json.dumps(request).encode())
                reply: dict[str, bool | str] = json.loads(self.sock.recv(BUFFER_SIZE).decode())
            except OSError as e:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raise Exception(e)
            else:
                if reply['status']:
                    self.sock.setblocking(False)
                    self.room = Room(name, password, addr)
                else:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    raise Exception(reply['message'])

    def sync(self):
        """Synchronize room members."""

        try:
            info = json.loads(self.sock.recv(BUFFER_SIZE).decode())
        except BlockingIOError:
            pass
        except OSError as e:
            raise Exception(e)
        else:
            if isinstance(info, dict) and 'players' in info:
                self.room.players[:] = info['players']