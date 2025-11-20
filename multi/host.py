from . import HOST_PORT_RANGE, BUFFER_SIZE, to_bytes, from_stream, Request, Response, Action, SocketClosedMessage, Room
import socket


class Host:
    def __init__(self, name: str, room_name: str, password: int):
        if not (0 < len(name) < BUFFER_SIZE / 32):
            raise ValueError("Name is empty or too long")
        if not (0 < len(room_name) < BUFFER_SIZE / 32):
            raise ValueError("Room name is empty or too long")
        if not (0 <= password < 10 ** (BUFFER_SIZE / 32)):
            raise ValueError("Password is out of range")

        self.name = name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in HOST_PORT_RANGE:
            try:
                self.sock.bind(('0.0.0.0', port))
            except OSError:
                pass
            else:
                self.sock.listen(1)
                self.sock.setblocking(False)
                break
        else:
            raise Exception("Can not find a free port")
        self.room = Room(room_name, password, ('127.0.0.1', port))
        self.room.players.append(self.name)
        self.connections: dict[str, dict[str, socket.socket]] = {
            'unverified': {}, 'verified': {}
        }

        self.actions: list[Action] = []

    def close(self, reason: Exception | str = ''):
        self.sock.close()
        for conn in self.connections['unverified'].values():
            conn.close()
        for conn in self.connections['verified'].values():
            conn.close()
        raise SocketClosedMessage(reason)

    def wait(self):
        while True:
            try:
                conn, addr = self.sock.accept()
            except BlockingIOError:
                break
            else:
                conn.setblocking(False)
                self.connections['unverified'][addr] = conn

        for addr, conn in self.connections['unverified'].copy().items():
            try:
                data = conn.recv(BUFFER_SIZE)
            except BlockingIOError:
                continue
            except ConnectionError:
                self.connections['unverified'].pop(addr)
            else:
                self.connections['unverified'].pop(addr)
                for obj in from_stream(data):
                    request = Request.from_dict(obj)
                    if len(self.room.players) < 10:
                        match request.name, request.password:
                            case name, _ if name in self.room.players:
                                response = Response(False, "Name is already taken")
                            case _, password if password != self.room.password:
                                response = Response(False, "Password is incorrect")
                            case _:
                                response = Response(True, '')
                                self.room.players.append(request.name)
                                self.connections['verified'][request.name] = conn
                    else:
                        response = Response(False, "Room is full")
                    try:
                        conn.send(to_bytes(response.to_dict()))
                    except ConnectionError:
                        pass

    def go(self):
        def action():   # 持续接收玩家行为
            for name, conn in self.connections['verified'].items():
                try:
                    data = conn.recv(BUFFER_SIZE)
                except BlockingIOError:
                    pass
                except ConnectionError:
                    self.connections['verified'].pop(name)
                else:
                    for obj in from_stream(data):
                        action = Action.from_dict(obj)
                        self.actions.append(action)

            for action in self.actions:
                for name, conn in self.connections['verified'].items():
                    if name != action.name:
                        conn.send(to_bytes(action.to_dict()))

        action()

    def sync(self):
        for name, conn in self.connections['verified'].copy().items():
            try:
                if not conn.recv(1, socket.MSG_PEEK):
                    self.room.players.remove(name)
                    self.connections['verified'].pop(name)
            except BlockingIOError:
                pass
        self.room.broadcast()

    def run(self):
        match self.room.status:
            case 0:
                self.wait()
            case 1:
                self.go()
            case _:
                pass
        self.sync()