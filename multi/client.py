from . import BUFFER_SIZE, to_stream, from_stream, Room
import socket


class Client:
    def __init__(self, name: str):
        self.name = name

        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room: Room

    def reset(self):
        """Reset the client."""

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(self, 'room'):
            del self.room

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
                self.sock.send(to_stream(request))
                reply: dict[str, bool | str] = from_stream(self.sock.recv(BUFFER_SIZE))[-1]
            except Exception as e:
                self.reset()
                raise e
            else:
                if reply['status']:
                    self.sock.setblocking(False)
                    self.room = Room(name, password, addr)
                else:
                    self.reset()
                    raise Exception(reply['message'])

    def sync(self):
        """Synchronize room members."""

        try:
            info = Room.Info.from_dict(from_stream(self.sock.recv(BUFFER_SIZE))[-1])
        except (BlockingIOError, IndexError):
            pass
        except ConnectionResetError:
            self.reset()
            raise Exception("Room has been closed")
        except OSError as e:
            self.reset()
            raise e
        else:
            self.room.players[:] = info.players