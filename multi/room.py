class Room:
    def __init__(self, name: str, password: int):
        self.name = name
        self.password = password
        # self.players = {}
        self.status = 0 # 0 is waiting and 1 is ongoing