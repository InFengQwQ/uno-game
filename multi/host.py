from . import HOST_PORT_RANGE, BUFFER_SIZE, to_bytes, from_stream, Request, Response, Action, ClosedError, Room
import socket


class Host:
    def __init__(self, name: str, room_name: str, password: int):
        if not (0 < len(name) < BUFFER_SIZE / 32):
            raise ValueError("Name is empty or too long")
        if not (0 < len(room_name) < BUFFER_SIZE / 32):
            raise ValueError("Room name is empty or too long")
        if not (0 < password < 2 ** (BUFFER_SIZE / 32)):
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
        self.connections: dict[str, dict[str, socket.socket]] = {'unverified': {}, 'verified': {}}

        self.actions: list[Action] = []

    def close(self):
        self.sock.close()
        for conn in self.connections['unverified'].values():
            conn.close()
        for conn in self.connections['verified'].values():
            conn.close()
        self.room.status = -1

    def reset(self):
        self.close()
        self.__init__(self.name, self.room.name, self.room.password)

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
                pass
            else:
                for obj in from_stream(data):
                    request = Request.from_dict(obj)
                    if 1 + len(self.connections['verified']) < 10:
                        match request.name, request.password:
                            case name, _ if name in self.connections['verified']:
                                response = Response(False, "Name is already taken")
                            case _, password if password != self.room.password:
                                response = Response(False, "Password is incorrect")
                            case _:
                                response = Response(True, '')
                                self.connections['verified'][request.name] = conn
                    else:
                        response = Response(False, "Room is full")
                    try:
                        conn.send(to_bytes(response.to_dict()))
                    except ConnectionError:
                        pass

            del self.connections['unverified'][addr]

    def go(self):
        def action():   # 持续接收玩家行为
            for name, conn in self.connections['verified'].items():
                try:
                    data = conn.recv(BUFFER_SIZE)
                except BlockingIOError:
                    pass
                except ConnectionError:
                    self.room.players.remove(name)
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
        self.room.players.clear()
        self.room.players.append(self.name)
        self.room.players.extend(self.connections['verified'])
        for name, conn in self.connections['verified'].copy().items():
            try:
                if not conn.recv(1, socket.MSG_PEEK):
                    raise ConnectionError
            except BlockingIOError:
                pass
            except ConnectionError:
                del self.connections['verified'][name]
        self.room.broadcast()

    def run(self):
        if self.room.status == -1:
            raise ClosedError
        match self.room.status:
            case 0:
                self.wait()
            case 1:
                self.go()
            case _:
                pass
        self.sync()