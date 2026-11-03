import socket
from typing import Any, Optional

from config import (
    HOST_PORT_RANGE,
    BUFFER_SIZE,
    ROOM_CAPACITY
)
from uno import Game, Rule

from .constants import *
from .utils import (
    to_bytes, from_stream,
    SocketClosedMessage
)
from .room import Room
from .mirror import *

__all__ = ['Host']


class Host:
    """Host of a room.

    Attributes:
        name: Name of the player.

        game: Game of the room.
        room: Room of the host.

        mirror: Game info mirror.
    """
    def __init__(self, name: str, room_name: str, password: int):
        if not 0 < len(name) < BUFFER_SIZE / 32:
            raise ValueError("Name is empty or too long")
        if not 0 < len(room_name) < BUFFER_SIZE / 32:
            raise ValueError("Room name is empty or too long")
        if not 0 <= password < 10 ** (BUFFER_SIZE / 32):
            raise ValueError("Password is out of range")

        self.name = name

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in HOST_PORT_RANGE:
            try:
                self._sock.bind(('0.0.0.0', port))
            except OSError: ...
            else:
                self._sock.listen(1)
                self._sock.setblocking(False)
                break
        else:
            raise OSError("No available port was found")
        self._connections: dict[str, dict[str, socket.socket]] = {
            'unverified': {}, 'verified': {}
        }
        self._messages: JsonMessage = {}

        self.game: Optional[Game] = None

        self.room = Room(port, room_name, password)
        self.room.players.append(self.name)

        self.mirror: Optional[Mirror] = None

    def close(self, reason: Exception = Exception()):
        self._sock.close()
        for conn in (self._connections['unverified'] | self._connections['verified']).values():
            conn.close()
        raise SocketClosedMessage(reason)

    def accept(self):
        """Accept new connections and update connections."""
        while True:
            try:
                conn, addr = self._sock.accept()
            except BlockingIOError:
                break
            else:
                conn.setsockopt(
                    socket.IPPROTO_TCP,
                    socket.TCP_NODELAY,
                    1
                )
                conn.setblocking(False)
                self._connections['unverified'][addr] = conn

    def verify(self):
        """Receive data from connections and verify them."""
        for addr, conn in self._connections['unverified'].copy().items():
            try:
                if not (data := conn.recv(BUFFER_SIZE)):
                    raise OSError
            except BlockingIOError: ...
            except OSError:
                del self._connections['unverified'][addr]
                conn.close()
            else:
                # TODO: handle invalid data
                assert (
                    request := from_stream(data)[0].get('request')
                ) # request
                del self._connections['unverified'][addr]
                if len(self.room.players) == ROOM_CAPACITY:
                    self.send(conn, msg={
                        'response': { # response
                            'status': False,
                            'message': "Room is full"
                        }
                    })
                    conn.close()
                elif request['name'] in self.room.players:
                    self.send(conn, msg={
                        'response': { # response
                            'status': False,
                            'message': "Name is already taken"
                        }
                    })
                    conn.close()
                elif request['password'] != self.room.password:
                    self.send(conn, msg={
                        'response': { # response
                            'status': False,
                            'message': "Password is incorrect"
                        }
                    })
                    conn.close()
                else:
                    self.send(conn, msg={
                        'response': { # response
                            'status': True,
                            'room': {
                                'name': self.room.name,
                                'password': self.room.password,
                                'port': self.room.port
                            }
                        }
                    })
                    self.room.players.append(request['name'])
                    self._connections['verified'][request['name']] = conn

    def send(self, conn: socket.socket, msg: JsonMessage):
        try:
            conn.sendall(to_bytes(msg))
        except BlockingIOError: ...
        except OSError:
            conn.close()

    def recv(self):
        def drop(name: str):
            connections = self._connections['verified']
            room = self.room
            connections.pop(name).close()
            if room.status == RoomStatus.WAITING:
                room.players.remove(name)

        for name, conn in self._connections['verified'].copy().items():
            try:
                peeked = conn.recv(BUFFER_SIZE, socket.MSG_PEEK)
                if not peeked:
                    drop(name)
                    continue
                messages, end = from_stream(peeked)
                if not end: continue
                conn.recv(end)
            except BlockingIOError: ...
            except OSError:
                drop(name)
            else:
                self._messages[name] = messages

    def sync(self):
        """Synchronize the host with clients."""
        if game := self.game:
            snapshot = Mirror.of(game, self.name)
            if mirror := self.mirror:
                mirror.update(snapshot)
            else:
                self.mirror = snapshot

            for name, conn in self._connections['verified'].items():
                self.send(conn, msg={
                    'game': Mirror.of(game, name).to_dict() # game
                })
        else:
            room = self.room
            info = {
                k: v for k, v in vars(room).items()
                if k not in ('port', 'name',
                    'password'
                )
            }
            for conn in self._connections['verified'].values():
                self.send(conn, msg={
                    'room': info # room
                })

    def start(self):
        self.game = Game(self.room.players)
        self.room.status = RoomStatus.ONGOING

    def action(self, type: ActionType, **kwargs: Any):
        """Perform action."""
        if type in (ActionType.DRAW, ActionType.CHALLENGE, ActionType.CATCH):
            assert not kwargs
        if type in (ActionType.PLAY):
            assert 'card' in kwargs and 'uno' in kwargs

        self._messages[self.name] = {
            'action': {
                'type': type.value,
                **kwargs
            }
        }

    def result(self):
        """Archive action."""
        if not self._messages.get(self.name): return
        if reply := self._messages[self.name].get('reply'): # reply
            if reply['status']:
                if reply.get('hand'):
                    pass

                    # TODO: 得到被质疑者手牌
            else:
                raise Exception(reply['message'])

    def handle(self):
        """Handle turn actions."""
        assert (game := self.game)

        messages, self._messages = self._messages, {}
        for name, msg in messages.items():
            if action := msg.get('action'): # action
                reply: InfoDict = {
                    'status': False
                }
                if action['type'] == ActionType.CATCH:
                    if Rule.is_able_to_catch(game):
                        reply['status'] = True
                        game.catch(name)
                    else:
                        reply['message'] = "Cannot catch"
                elif name == game.player.name:
                    match action['type']:
                        case ActionType.PLAY:
                            card = CardInfo.from_dict(action['card'])
                            if card in Rule.validplays(game):
                                reply['status'] = True
                                game.player.uno = action['uno']
                                game.play(card)
                            else:
                                reply['message'] = "Invalid play"
                        case ActionType.DRAW:
                            reply['status'] = True
                            game.draw()
                        case ActionType.CHALLENGE:
                            if Rule.is_able_to_challenge(game):
                                assert game.target_player

                                reply['status'] = True
                                reply['hand'] = [
                                    vars(card)
                                    for card in game.target_player.hand
                                ]
                                game.challenge()
                            else:
                                reply['message'] = "Cannot challenge"
                        case _:
                            continue
                else:
                    reply['message'] = "Not your turn"

                if name == self.name:
                    self._messages[self.name] = {
                        'reply': reply
                    }
                if conn := self._connections['verified'].get(name):
                    self.send(conn, msg={
                        'reply': reply # reply
                    })

    def run(self):
        """Run the host role."""
        self.recv()

        if self.room.status == RoomStatus.WAITING:
            self.room.broadcast()
            self.accept()
            self.verify()
        elif self.room.status == RoomStatus.ONGOING:
            self.handle()
            self.result()

        self.sync()
