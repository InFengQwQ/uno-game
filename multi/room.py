class Room:
    def __init__(self, name: str, password: int, addr: tuple[str, int]):
        self.password = password

        self.name = name
        self.addr = addr
        self.players: list[str] = []
        self.status = 0 # 0 is waiting and 1 is ongoing

    @property
    def info(self) -> dict[str, str | tuple[str, int] | list[str] | int]:
        return {
            'name': self.name,
            'addr': self.addr,
            'players': self.players,
            'status': self.status
        }