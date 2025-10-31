from . import HOST_PORT_RANGE, BUFFER_SIZE, to_stream, from_stream, Client, Room
import socket


class Host:
    def __init__(self, name: str, room_name: str, password: int):
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
                    request = from_stream(conn.recv(BUFFER_SIZE))[-1]
                except BlockingIOError:
                    continue
                except OSError:
                    pass
                else:
                    reply: dict[str, bool | str]
                    if len(self.connections['verified']) == 10:
                        reply = {
                            'status': False, 'message': "Room is full"
                        }
                    elif request['name'] in self.connections['verified']:
                        reply = {
                            'status': False, 'message': "Name exists"
                        }
                    elif request['password'] != self.client.room.password:
                        reply = {
                            'status': False, 'message': "Password is incorrect"
                        }
                    else:
                        reply = {
                            'status': True
                        }
                    try:
                        conn.send(to_stream(reply))
                    except OSError:
                        pass
                    else:
                        if reply['status']:
                            self.connections['verified'][request['name']] = conn
                            del self.connections['unverified'][addr]
                            continue
                conn.shutdown(socket.SHUT_RDWR)
                del self.connections['unverified'][addr]

        def sync():
            """Sync room members."""

            self.client.room.players[:] = list(self.connections['verified'])
            for name, conn in self.connections['verified'].copy().items():
                try:
                    conn.send(to_stream(self.client.room.info))
                except ConnectionError:
                    conn.close()
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
                        conn.send(to_stream(action))

        action()
        sync()