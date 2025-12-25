"""The client side of a multiplayer UNO game."""

import socket
from typing import Optional

from config import BUFFER_SIZE, SOCKET_TIMEOUT
from .constants import (
    ROOM_ONGOING, ROOM_WAITING,
    JsonMessage, Action
)
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage, GameStartedMessage, GameEndedMessage,
    create_action_message
)
from .room import Room


class Client:
    """The client side of a multiplayer UNO game."""
    
    def __init__(self, name: str):
        """Initialize the client.
        
        Args:
            name: Player name
            
        Raises:
            ValueError: If name is invalid
        """
        if not 0 < len(name) < BUFFER_SIZE / 32:
            raise ValueError(
                "Name is empty or too long"
            )

        self.name = name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages: JsonMessage = {}
        self.room: Optional[Room] = None

    def close(self, reason: Exception = Exception()) -> None:
        """Close the client connection,
        and raise a SocketClosedMessage.

        Args:
            reason: The reason for closing the connection.
        """
        self.sock.close()
        self.room = None
        raise SocketClosedMessage(reason)

    def send(self, msg: JsonMessage) -> None:
        """Send a message to the host.
        
        Args:
            msg: The message to send
        """
        try:
            self.sock.send(to_bytes(msg))
        except OSError as e:
            self.close(reason=e)

    def send_action(self, action: Action, data: Optional[dict] = None) -> None:
        """Send a game action to the host.
        
        Args:
            action: The action type
            data: Optional action data
        """
        msg = create_action_message(action, data)
        self.send(msg)

    def recv(self) -> None:
        """Receive data and update the messages dictionary."""
        try:
            if not (data := self.sock.recv(BUFFER_SIZE)):
                raise ConnectionError(
                    "Host has closed the connection"
                )
        except (TimeoutError, ConnectionError) as e:
            self.close(reason=e)
        except BlockingIOError:
            pass
        else:
            self.messages.update(from_stream(data))

    def extract(self, key: str) -> dict:
        """Extract data from the messages dictionary.
        
        Args:
            key: The message key to extract
            
        Returns:
            The extracted message data
        """
        self.messages.setdefault(key, {})
        return self.messages.pop(key)

    def join(self, addr: tuple[str, int], password: int) -> None:
        """Join a room.
        
        Args:
            addr: Tuple of (host IP, port)
            password: Room password
            
        Raises:
            TimeoutError: If connection times out
            ConnectionRefusedError: If connection is refused
        """
        self.sock.settimeout(SOCKET_TIMEOUT)
        try:
            self.sock.connect(addr)
        except TimeoutError as e:
            raise TimeoutError(
                "Timeout or game is ongoing"
            ) from e
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                "Host is busy or room does not exist"
            ) from e
        else:
            msg: JsonMessage = {'request': {
                'name': self.name,
                'password': password
            }}
            self.send(msg)
            self.sync()

    def sync(self) -> None:
        """Synchronize the client with the host."""
        self.recv()

        if response := self.extract('response'):
            if response['status']:
                self.sock.setblocking(False)
                self.room = Room(**response['room'])
            else:
                self.close(response['message'])

        assert self.room

        if room := self.extract('room'):
            self.room.players[:] = room['players']
            if (
                room['status'] is ROOM_ONGOING and
                self.room.status is ROOM_WAITING
            ):
                self.room.status = ROOM_ONGOING
                raise GameStartedMessage
            elif (
                room['status'] is ROOM_WAITING and
                self.room.status is ROOM_ONGOING
            ):
                self.room.status = ROOM_WAITING
                raise GameEndedMessage

    def go(self) -> None:
        """Handle game messages."""
        assert self.room
        
        # Process game state updates
        if state := self.extract('state'):
            # Handle game state synchronization
            pass

    def run(self) -> None:
        """Run the client."""
        assert self.room

        self.sync()
        if self.room.status is ROOM_ONGOING:
            self.go()
