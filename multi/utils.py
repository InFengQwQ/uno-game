import json


def to_stream(d: dict) -> bytes:
    try:
        return json.dumps(d).encode()
    except json.JSONDecodeError:
        return b''

def from_stream(stream: bytes) -> list[dict]:   # TODO: 单个值时返回单列表
    try:
        data = stream.decode()
        result = []
        i = j = 0
        for a, b in zip(data[:-1], data[1:]):
            if a in ['}', ']'] and b in ['[', '{']:
                i, j = j, data.index(b)
                result.append(data[i:j])
        result.append(data[j:])
        return [d for d in map(json.loads, result)]
    except json.JSONDecodeError:
        return []