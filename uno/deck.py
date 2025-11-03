from . import COLORS, BLACK_COLOR, NUMBER, NUMBERS, NONZERO_NUMBERS, ACTIONS, WILDS, Card
import random


class Deck:
    def __init__(self):
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []
        for color in COLORS:
            for numbers in NUMBERS, NONZERO_NUMBERS:
                for value in numbers:
                    self.draw_pile.append(Card(color, NUMBER, value))
                for action in ACTIONS:
                    self.draw_pile.append(Card(color, action, 20))  # 分数值也可以放到constants.py中
            for wild in WILDS:
                self.draw_pile.append(Card(BLACK_COLOR, wild, 50))
        random.shuffle(self.draw_pile)

    def _reshuffle(self):
        for card in self.discard_pile[:-1]:
            if card.type in WILDS:
                card.color = BLACK_COLOR
        self.draw_pile, self.discard_pile = self.discard_pile[:-1], self.discard_pile[-1:]
        random.shuffle(self.draw_pile)

    def draw(self, num: int = 1):    # draw_pile to player.hand
        cards: list[Card] = []
        for _ in range(num):
            try:
                if not self.draw_pile:
                    self._reshuffle()
            except IndexError:
                return cards
            else:
                cards.append(self.draw_pile.pop())
        return cards

    def discard(self, card: Card):  # player.hand to discard_pile
        self.discard_pile.append(card)