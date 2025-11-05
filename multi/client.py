from . import BUFFER_SIZE, to_bytes, from_stream, Info, Request, Response, ClosedError, Room
import socket


class Client:
    def __init__(self, name: str):
        if not (0 < len(name) < BUFFER_SIZE / 32):
            raise ValueError("Name is empty or too long")

        self.name = name

        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room: Room

    def close(self, reason: Exception | str = ''):
        self.sock.close()
        if hasattr(self, 'room'):
            del self.room
        raise ClosedError(reason)

    def join(self, info: Info, password: int):
        """Join a room."""

        self.sock.settimeout(5)
        try:
            self.sock.connect(info.addr)
        except TimeoutError:
            raise TimeoutError("Timeout or game is ongoing")
        except ConnectionRefusedError:
            raise ConnectionRefusedError("Host is busy or room does not exist")
        else:
            request = Request(self.name, password)
            try:
                self.sock.send(to_bytes(request.to_dict()))
            except ConnectionError as e:
                self.close(e)
            else:
                try:
                    data = self.sock.recv(BUFFER_SIZE)
                except TimeoutError as e:
                    self.close(e)
                except ConnectionError as e:
                    self.close(e)
                else:
                    for obj in from_stream(data):
                        response = Response.from_dict(obj)
                        if response.status:
                            self.sock.setblocking(False)
                            self.room = Room(info.name, password, info.addr)
                        else:
                            self.close(response.message)

    def wait(self):
        pass

    def sync(self): # 但是没法回到主界面啊...
        Room.receive()
        if info := Room.rooms.get(self.room.addr):
            self.room.players[:] = info.players
            self.room.status = info.status

        try:
            if not self.sock.recv(1, socket.MSG_PEEK):
                self.close("Failed to connect to the host")
        except BlockingIOError:
            pass

    def run(self):
        if hasattr(self, 'room'):
            self.wait()
            self.sync()