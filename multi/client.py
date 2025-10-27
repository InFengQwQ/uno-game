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
        except (socket.timeout, TimeoutError, OSError):
            raise Exception(f'TIMEOUT OR ROOM IS FULL')
        else:
            request: dict[str, Any] = {
                'name': self.name,
                'password': password
            }
            try:
                self.sock.send(json.dumps(request).encode())
                reply = json.loads(self.sock.recv(BUFFER_SIZE).decode())
            except socket.timeout:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raise Exception('TIMEOUT OR ROOM IS FULL')
            except json.JSONDecodeError:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raise Exception('SERVER RESPONSE FORMAT ERROR')
            except Exception as e:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raise Exception(f'CONNECTION ERROR: {str(e)}')
            
            if reply['status']:
                self.sock.setblocking(False)
                self.room = Room(name, password, addr)
                return True
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raise Exception(reply.get('message', 'UNKNOWN ERROR'))

    def sync(self):
        """Synchronize room members."""
        try:
            info = json.loads(self.sock.recv(BUFFER_SIZE).decode())
        except BlockingIOError:
            pass
        except json.JSONDecodeError:
            pass
        except Exception:
            pass
        else:
            if isinstance(info, dict) and 'players' in info:
                self.room.players[:] = info['players']