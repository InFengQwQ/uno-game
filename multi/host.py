from . import HOST_PORT_RANGE, BUFFER_SIZE, to_bytes, from_stream, Request, Response, Action, Client, Room
import socket


class Host:
    def __init__(self, client: Client, room_name: str, password: int):
        if not (0 < len(room_name) < BUFFER_SIZE / 32):
            raise ValueError("Room name is empty or too long")
        if not (0 < password < 2 ** (BUFFER_SIZE / 32)):
            raise ValueError("Password is out of range")

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

        self.room = client.room = Room(room_name, password, ('127.0.0.1', port))
        client.sock.connect(self.room.addr)
        conn, _ = self.sock.accept()
        conn.setblocking(False)
        client.sock.setblocking(False)
        self.connections: dict[str, dict[str, socket.socket]] = {'unverified': {}, 'verified': {client.name: conn}}

        self.actions: list[Action] = []

    def close(self):
        self.sock.close()
        for conn in self.connections['unverified'].values():
            conn.close()
        for conn in self.connections['verified'].values():
            conn.close()

    def run(self):
        """Wait for players to join, and verify players, sync, and go."""

        def wait():
            def admit():
                try:
                    conn, addr = self.sock.accept()
                except BlockingIOError:
                    pass
                else:
                    conn.setblocking(False)
                    self.connections['unverified'][addr] = conn

            def verify():
                for addr, conn in self.connections['unverified'].copy().items():
                    if len(self.connections['verified']) < 10:
                        try:
                            data = conn.recv(BUFFER_SIZE)
                        except BlockingIOError:
                            pass
                        except ConnectionResetError:
                            del self.connections['unverified'][addr]
                        else:
                            for obj in from_stream(data):
                                request = Request.from_dict(obj)
                                match request.name, request.password:
                                    case name, _ if name in self.connections['verified']:
                                        response = Response(False, "Name is already taken")
                                    case _, password if password != self.room.password:
                                        response = Response(False, "Password is incorrect")
                                    case _:
                                        response = Response(True, '')
                                try:
                                    conn.send(to_bytes(response.to_dict()))
                                except ConnectionAbortedError:
                                    del self.connections['unverified'][addr]
                                else:
                                    if response.status:
                                        self.connections['verified'][request.name] = conn
                                        del self.connections['unverified'][addr]

            admit()
            verify()

        def go():
            def action():   # 持续接收玩家行为
                for name, conn in self.connections['verified'].items():
                    try:
                        data = conn.recv(BUFFER_SIZE)
                    except BlockingIOError:
                        pass
                    except ConnectionResetError:
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

        def sync(): # 对吗？
            self.room.players[:] = list(self.connections['verified'])
            for name, conn in self.connections['verified'].copy().items():
                try:
                    conn.send(b'')
                except ConnectionError:
                    del self.connections['verified'][name]

        match self.room.status:
            case 0:
                wait()
            case 1:
                go()
            case _:
                pass
        sync()
        self.room.broadcast()