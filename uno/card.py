class Card:
    def __init__(self, color: str, type: str, value: int):
        self.color = color  # "Red" "Green" "Blue" "Yellow" or "Black"
        self.type = type    # wilds, actions or "Number"
        self.value = value  # value of score

    def __repr__(self): 
        if self.value < 10:
            return f'Card({self.color}, {self.type}, {self.value})'
        else:
            return f'Card({self.color}, {self.type})'