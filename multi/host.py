from . import HOST_PORT_RANGE, BUFFER_SIZE, to_bytes, from_stream, Info, Request, Response, Client, Room
import socket


class Host:
    def __init__(self, room_name: str, name: str, password: int):
        if not (0 < len(room_name) < BUFFER_SIZE / 32):
            raise ValueError("Room name is empty or too long")
        if not (0 < len(name) < BUFFER_SIZE / 32):
            raise ValueError("Name is empty or too long")
        if not (0 < password < 2 ** (BUFFER_SIZE / 32)):
            raise ValueError("Password is out of range")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in HOST_PORT_RANGE:
            try:
                self.sock.bind(('0.0.0.0', port))
            except OSError:
                continue
            else:
                self.sock.listen(1)
                self.sock.setblocking(False)
                break
        else:
            raise Exception("Can not find a free port")

        addr = ('127.0.0.1', port)
        self.client = Client(name)
        self.client.sock.connect(addr)
        self.client.room = Room(room_name, password, addr)

        conn, _ = self.sock.accept()
        self.connections: dict[str, dict[str, socket.socket]] = {'unverified': {}, 'verified': {name: conn}}

        self.actions: list[dict[str, str | int]] = []

    def close(self):
        self.client.reset()
        self.sock.close()
        for conn in self.connections['unverified'].values():
            conn.close()
        for conn in self.connections['verified'].values():
            conn.close()

    def wait(self):
        """Operation to wait for clients to join the room."""

        def admit():
            """Accept connection for one time."""

            try:
                conn, addr = self.sock.accept()
            except BlockingIOError:
                pass
            else:
                conn.setblocking(False)
                self.connections['unverified'][addr] = conn

        def verify():
            """Verify clients' name and password."""

            for addr, conn in self.connections['unverified'].copy().items():
                try:
                    data = conn.recv(BUFFER_SIZE)
                except BlockingIOError:
                    continue
                except ConnectionResetError:
                    conn.shutdown(socket.SHUT_RDWR)
                    del self.connections['unverified'][addr]
                else:
                    for obj in from_stream(data):
                        if request := Request.from_dict(obj):
                            if len(self.connections['verified']) >= 10:
                                response = Response(False, "Room is full")
                            elif request.name in self.connections['verified']:
                                response = Response(False, "Name is already taken")
                            elif request.password != self.client.room.password:
                                response = Response(False, "Password is incorrect")
                            else:
                                response = Response(True, '')
                            try:
                                conn.send(to_bytes(response.to_dict()))
                            except ConnectionAbortedError:
                                conn.shutdown(socket.SHUT_RDWR)
                                del self.connections['unverified'][addr]
                            else:
                                if response.status:
                                    self.connections['verified'][request.name] = conn
                                    del self.connections['unverified'][addr]
                                    continue

        def sync():
            """Sync room members."""

            self.client.room.players[:] = list(self.connections['verified'])
            info = Info(self.client.room.name, self.client.room.addr, self.client.room.players)
            for name, conn in self.connections['verified'].copy().items():
                try:
                    conn.send(to_bytes(info.to_dict()))
                except ConnectionError:
                    conn.shutdown(socket.SHUT_RDWR)
                    del self.connections['verified'][name]

        admit()
        verify()
        sync()
        self.client.room.broadcast()

    def go(self):
        def action():   # 持续接收玩家行为
            for conn in self.connections['verified'].values():
                try:
                    actions = from_stream(conn.recv(BUFFER_SIZE))
                except BlockingIOError:
                    continue
                else:
                    self.actions.extend(actions)

        def sync(): # 同步广播行为，在每次动画加载前执行
            for action in self.actions:
                for conn in self.connections['verified'].values():
                    if conn != self.connections['verified'][str(action['player'])]:
                        conn.send(to_bytes(action))

        action()
        sync()