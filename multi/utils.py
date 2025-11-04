from . import InfoDict, RequestDict, ResponseDict, ActionDict, JsonSerializable
import json


def to_bytes(obj: JsonSerializable):
    try:
        return json.dumps(obj).encode()
    except json.JSONDecodeError:
        return b''

def from_packet(packet: bytes):
    result = None
    try:
        result = json.loads(packet.decode())
    except json.JSONDecodeError:
        pass
    return result

def from_stream(stream: bytes):
    data = ''
    result: list[JsonSerializable] = []
    for c in stream.decode():
        data += c
        try:
            result.append(json.loads(data))
        except json.JSONDecodeError:
            pass
        else:
            data = ''
    return result

class Info():
    def __init__(self, name: str, addr: tuple[str, int], players: list[str], status: int):
        self.name = name
        self.addr = self.ip, self.port = addr
        self.players = players
        self.status = status

    # def __eq__(self, other: object):
    #     if isinstance(other, Info):
    #         return self.addr == other.addr
    #     else:
    #         return NotImplemented

    def __lt__(self, other: object):
        if isinstance(other, Info):
            return self.name < other.name
        else:
            return NotImplemented

    def to_dict(self) -> InfoDict:
        return {
            'name': self.name,
            'port': self.port,
            'players': self.players,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, obj: JsonSerializable, ip: str):
        if (
            isinstance(name := obj['name'], str) and
            isinstance(port := obj['port'], int) and
            isinstance(players := obj['players'], list) and
            isinstance(status := obj['status'], int)
        ):
            return cls(name, (ip, port), players, status)
        else:
            raise TypeError

class Request():
    def __init__(self, name: str, password: int):
        self.name = name
        self.password = password

    def to_dict(self) -> RequestDict:
        return self.__dict__

    @classmethod
    def from_dict(cls, obj: JsonSerializable):
        if (
            isinstance(name := obj['name'], str) and
            isinstance(password := obj['password'], int)
        ):
            return cls(name, password)
        else:
            raise TypeError

class Response():
    def __init__(self, status: bool, message: str):
        self.status = status
        self.message = message

    def to_dict(self) -> ResponseDict:
        return self.__dict__

    @classmethod
    def from_dict(cls, obj: JsonSerializable):
        if (
            isinstance(status := obj['status'], bool) and
            isinstance(message := obj['message'], str)
        ):
            return cls(status, message)
        else:
            raise TypeError

class Action():
    def __init__(self, name: str, action: str, value: int):
        self.name = name
        self.action = action
        self.value = value

    def to_dict(self) -> ActionDict:
        return self.__dict__

    @classmethod
    def from_dict(cls, obj: JsonSerializable):
        if (
            isinstance(name := obj['name'], str) and
            isinstance(action := obj['action'], str) and
            isinstance(value := obj['value'], int)
        ):
            return cls(name, action, value)
        else:
            raise TypeError

class ClosedError(Exception):
    pass