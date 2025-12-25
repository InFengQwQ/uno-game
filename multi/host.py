"""The host side of a multiplayer UNO game."""

import socket
from typing import Optional

from config import HOST_PORT_RANGE, BUFFER_SIZE, ROOM_CAPACITY
from .constants import (
    ROOM_WAITING, ROOM_ONGOING,
    InfoDict, JsonMessage, Action
)
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage,
    create_action_message, create_error_message
)
from .room import Room


class Host:
    """The host side of a multiplayer UNO game."""
    
    def __init__(self, name: str, room_name: str, password: int):
        """Initialize the host.
        
        Args:
            name: Host player name
            room_name: Name of the room
            password: Room password
            
        Raises:
            ValueError: If parameters are invalid
            OSError: If no free port is available
        """
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
        }

        self.actions: list[InfoDict] = []

    def close(self, reason: Exception = Exception()) -> None:
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

    def send(self, conn: socket.socket, msg: JsonMessage) -> None:
        """Send a message to a connection.
        
        Args:
            conn: The socket connection
            msg: The message to send
        """
        try:
            conn.send(to_bytes(msg))
        except OSError:
            pass

    def broadcast(self, msg: JsonMessage, exclude: Optional[str] = None) -> None:
        """Broadcast a message to all verified connections.
        
        Args:
            msg: The message to broadcast
            exclude: Optional player name to exclude from broadcast
        """
        for name, conn in self.connections['verified'].items():
            if name != exclude:
                self.send(conn, msg)

    def recv(self) -> None:
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

    def extract(self, key: str) -> InfoDict:
        """Extract data from the messages dictionary.
        
        Args:
            key: The message key to extract
            
        Returns:
            The extracted message data
        """
        self.messages.setdefault(key, {})
        return self.messages.pop(key)

    def accept(self) -> None:
        """Accept new connection and update connections dictionary."""
        while True:
            try:
                conn, addr = self.sock.accept()
            except BlockingIOError:
                break
            else:
                conn.setblocking(False)
                self.connections['unverified'][addr] = conn

    def verify(self) -> None:
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

    def sync(self) -> None:
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

    def wait(self) -> None:
        """Handle room messages."""
        self.room.broadcast()

        self.accept()
        self.verify()

    def process_action(self, action: InfoDict) -> None:
        """Process a game action from a client.
        
        Args:
            action: The action data to process
        """
        self.actions.append(action)

    def go(self) -> None:
        """Handle game messages."""
        # Process actions from clients
        if action_data := self.extract('action'):
            self.process_action(action_data)

    def run(self) -> None:
        """Run the host."""
        self.sync()
        if self.room.status is ROOM_WAITING:
            self.wait()
        elif self.room.status is ROOM_ONGOING:
            self.go()
