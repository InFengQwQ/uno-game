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
            except ConnectionError as e:
                self.reset()
                raise e
            else:
                try:
                    data = self.sock.recv(BUFFER_SIZE)
                except TimeoutError as e:
                    self.reset()
                    raise OSError("Timeout or room is full")
                except ConnectionError:
                    self.reset()
                    raise OSError("Room has been closed")
                else:
                    for obj in from_stream(data):
                        response = Response.from_dict(obj)
                        if response.status:
                            self.sock.setblocking(False)
                            self.room = Room(info.name, password, info.addr)
                        else:
                            self.reset()
                            raise Exception(response.message)

    def run(self):
        """Run the client."""

        def sync(): # 但是没法回到主界面啊...
            try:
                if not self.sock.recv(1, socket.MSG_PEEK):
                    raise ConnectionError
            except BlockingIOError:
                pass
            except ConnectionError:
                self.reset()

        Room.receive()
        if hasattr(self, 'room'):
            if info := Room.rooms.get(self.room.addr):
                self.room.players[:] = info.players
                self.room.status = info.status
            sync()