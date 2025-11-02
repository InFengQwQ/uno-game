from . import BUFFER_SIZE, to_bytes, from_stream, Info, Request, Response, Room
import socket


class Client:
    def __init__(self, name: str):
        if not (0 < len(name) < BUFFER_SIZE / 32):
            raise ValueError("Name is empty or too long")

        self.name = name

        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room: Room

    def reset(self):
        """Reset the client."""

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(self, 'room'):
            del self.room

    def join(self, info: Info, password: int):
        """Join a room."""

        self.sock.settimeout(5)
        try:
            self.sock.connect(info.addr)
        except TimeoutError:
            raise OSError("Timeout or game is ongoing")
        except ConnectionRefusedError:
            raise OSError("Host is busy or room does not exist")
        else:
            request = Request(self.name, password)
            try:
                self.sock.send(to_bytes(request.to_dict()))
            except ConnectionAbortedError as e:
                self.reset()
                raise e
            else:
                try:
                    data = self.sock.recv(BUFFER_SIZE)
                except TimeoutError as e:
                    self.reset()
                    raise OSError("Timeout or room is full")
                except ConnectionResetError:
                    self.reset()
                    raise OSError("Room has been closed")
                else:
                    for obj in from_stream(data):
                        if response := Response.from_dict(obj):
                            if response.status:
                                self.sock.setblocking(False)
                                self.room = Room(info.name, password, info.addr)
                            else:
                                self.reset()
                                raise Exception(response.message)

    def sync(self):
        """Synchronize room members."""

        try:
            data = self.sock.recv(BUFFER_SIZE)
        except BlockingIOError:
            pass
        except ConnectionResetError:
            self.reset()
            raise OSError("Room has been closed")
        except OSError as e:
            self.reset()
            raise e
        else:
            for obj in from_stream(data):
                if info := Info.from_dict(obj, ''):
                    self.room.players[:] = info.players