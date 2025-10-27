from . import HOST_PORT_RANGE, BUFFER_SIZE, Client, Room
import json, socket


class Host:
    def __init__(self, name: str, room_name: str, password: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in HOST_PORT_RANGE:
            try:
                self.sock.bind(('0.0.0.0', port))
            except OSError:
                continue
            else:
                self.sock.listen(10)
                break
        else:
            raise Exception('CAN NOT FIND A FREE PORT')
        addr = ('127.0.0.1', port)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(addr)
        sock, _ = self.sock.accept()
        self.sock.setblocking(False)
        self.connections: dict[str, dict[str, socket.socket]] = {'unverified': {}, 'verified': {name: sock}}
        self.client = Client(name, client_sock)
        self.client.room = Room(room_name, password, addr)

        self.actions: list[dict[str, str | int]] = []

    def wait(self):
        """Operation to wait for clients to join the room."""
        def admit():
            """Accept connections for one time."""
            while len(self.connections['verified']) + len(self.connections['unverified']) < 10:
                try:
                    conn, addr = self.sock.accept()
                except BlockingIOError:
                    break
                else:
                    conn.setblocking(False)
                    self.connections['unverified'][addr] = conn

        def sync():
            """Sync room members."""
            for addr, conn in self.connections['unverified'].copy().items():
                try:
                    request = json.loads(conn.recv(BUFFER_SIZE).decode())
                except BlockingIOError:
                    continue
                except Exception:
                    conn.close()
                    del self.connections['unverified'][addr]
                else:
                    if (name := request['name']) in self.connections['verified']: # 重名
                        conn.send(json.dumps({'status': False, 'message': 'NAME EXISTS'}).encode())
                        conn.close()
                    elif request['password'] != self.client.room.password:
                        conn.send(json.dumps({'status': False, 'message': 'PASSWORD INCORRECT'}).encode())
                        conn.close()
                    else:
                        conn.send(json.dumps({'status': True}).encode())
                        self.connections['verified'][name] = conn
                    del self.connections['unverified'][addr]

            self.client.room.players[:] = list(self.connections['verified'])
            for name, conn in self.connections['verified'].copy().items():
                try:
                    conn.send(json.dumps(self.client.room.info).encode())
                except Exception as e:
                    print(e)
                    conn.close()
                    del self.connections['verified'][name]   # 是否要直接删除？不过确实socket失效之后已经没必要存储了

        admit()
        sync()
        self.client.room.broadcast()

    def go(self):
        def action():   # 持续接收玩家行为
            for conn in self.connections['verified'].values():
                try:
                    action = json.loads(conn.recv(BUFFER_SIZE).decode())
                except BlockingIOError:
                    continue
                else:
                    self.actions.append(action)

        def sync(): # 同步广播行为，在每次动画加载前执行
            for action in self.actions:
                for conn in self.connections['verified'].values():
                    if conn != self.connections['verified'][str(action['player'])]:
                        conn.send(json.dumps(action).encode())

        action()
        sync()