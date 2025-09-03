from . import Card, Deck


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: list[Card] = []
        self.score = 0  # Other players' hand cards when losing can be added here with a certain weight.

    def draw(self, deck: Deck, num: int = 1):  # deck.draw_pile to hand
        self.hand.extend(deck.draw(num))

    def discard(self, deck: Deck, card: Card):  # hand(chosen that is valid) to discard_pile
        self.hand.remove(card)
        deck.discard(card)