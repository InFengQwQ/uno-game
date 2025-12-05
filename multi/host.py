"""The host side of a multiplayer UNO game."""

import socket

from config import HOST_PORT_RANGE, BUFFER_SIZE, ROOM_CAPACITY
from .constants import (
    ROOM_WAITING, ROOM_ONGOING,
    InfoDict, JsonMessage
)
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage
)
from .room import Room


class Host:
    """The host side of a multiplayer UNO game."""
    def __init__(self, name: str, room_name: str, password: int):
        if not 0 < len(name) < BUFFER_SIZE / 32:
            raise ValueError("Name is empty or too long")
        if not 0 < len(room_name) < BUFFER_SIZE / 32:
            raise ValueError("Room name is empty or too long")
        if not 0 <= password < 10 ** (BUFFER_SIZE / 32):
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
            raise OSError("Can not find a free port")
        self.messages: JsonMessage = {}
        self.room = Room(room_name, password, port)
        self.room.players.append(self.name)
        self.connections: dict[str, dict[str, socket.socket]] = {
            'unverified': {}, 'verified': {}
        }               # 考虑分成两个字典，因为毕竟一个是addr: dict socket一个是name: dict socket

        self.actions: list[InfoDict] = []

    def close(self, reason: Exception = Exception()):
        """Close the Host and all connections,
        and raise a SocketClosedMessage.

        Args:
            reason: The reason for closing the connections.
        """
        self.sock.close()
        for conn in self.connections['unverified'].values():
            conn.close()
        for conn in self.connections['verified'].values():
            conn.close()
        raise SocketClosedMessage(reason)

    def send(self, conn: socket.socket, msg: JsonMessage):
        """Send a message."""
        try:
            conn.send(to_bytes(msg))
        except OSError:
            pass        # 暂时没考虑出这种情况

    def recv(self):
        """Receive data and update the messages dictionary."""
        for addr, conn in self.connections['unverified'].copy().items():
            try:
                data = conn.recv(BUFFER_SIZE)
            except ConnectionError:
                self.connections['unverified'].pop(addr)
            except BlockingIOError:
                pass
            else:
                self.messages.update(from_stream(data))

        for name, conn in self.connections['verified'].copy().items():
            try:
                if not (data := conn.recv(BUFFER_SIZE)):
                    raise ConnectionError
            except ConnectionError:
                self.connections['verified'].pop(name)
                if self.room.status is ROOM_WAITING:
                    self.room.players.remove(name)
            except BlockingIOError:
                pass
            else:
                self.messages.update(from_stream(data))

    def extract(self, key: str):
        """Extract data from the messages dictionary."""
        self.messages.setdefault(key, {})
        return self.messages.pop(key)

    def accept(self):
        """Accept new connection and update connections dictionary."""
        while True:
            try:
                conn, addr = self.sock.accept()
            except BlockingIOError:
                break
            else:
                conn.setblocking(False)
                self.connections['unverified'][addr] = conn

    def verify(self):
        """Verify the connections and update connections dictionary."""
        for addr, conn in self.connections['unverified'].copy().items():
            if request := self.extract('request'):
                self.connections['unverified'].pop(addr)
                if len(self.room.players) == ROOM_CAPACITY:
                    msg: JsonMessage = {'response': {
                        'status': False,
                        'message': "Room is full"
                    }}
                elif request['name'] in self.room.players:
                    msg: JsonMessage = {'response': {
                        'status': False,
                        'message': "Name is already taken"
                    }}
                elif request['password'] != self.room.password:
                    msg: JsonMessage = {'response': {
                        'status': False,
                        'message': "Password is incorrect"
                    }}
                else:
                    msg: JsonMessage = {'response': {
                        'status': True,
                        'room': {
                            'name': self.room.name,
                            'password': self.room.password,
                            'port': self.room.port
                        }
                    }}
                    self.room.players.append(request['name'])
                    self.connections['verified'][request['name']] = conn
                self.send(conn, msg)

    def sync(self):
        """Synchronize the host with clients,
        and remove disconnected players.
        """
        self.recv()

        msg: JsonMessage = {'room':{
            'players': self.room.players,
            'status': self.room.status
        }}
        for conn in self.connections['verified'].copy().values():
            self.send(conn, msg)

    def wait(self):
        """Handle room messages."""
        self.room.broadcast()

        self.accept()
        self.verify()

    def go(self):
        """Handle game messages."""
        # action()

    def run(self):
        """Run the host."""
        self.sync()
        if self.room.status is ROOM_WAITING:
            self.wait()
        elif self.room.status is ROOM_ONGOING:
            self.go()
