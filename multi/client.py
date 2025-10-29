from . import BUFFER_SIZE, Room
import json, socket


class Client:
    def __init__(self, name: str):
        self.name = name

        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room: Room

    def join(self, info: Room.Info, password: int):
        """Join a room."""

        name, addr = info.name, info.addr
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
                self.reset()
                raise e
            else:
                if reply['status']:
                    self.sock.setblocking(False)
                    self.room = Room(name, password, addr)
                else:
                    self.reset()
                    raise Exception(reply['message'])

    def reset(self):
        """Reset the client."""

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(self, 'room'):
            del self.room

    def sync(self):
        """Synchronize room members."""

        try:
            info = Room.Info(**json.loads(self.sock.recv(BUFFER_SIZE).decode()))
        except BlockingIOError:
            pass
        except ConnectionResetError:
            raise Exception("Room has been closed")
        except OSError as e:
            raise e
        else:
            self.room.players[:] = info.players