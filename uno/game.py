from . import Card, Deck, Player, Rules
import random


class Game:
    def __init__(self, players: list[Player]):
        self.deck = Deck()
        self.players = players   # player number no more than 10
        self.turn = -1   # counterclockwise is positively increasing, and default clockwise
        self.reverse = False
        self.draw = 0
        for player in self.players:
            player.draw(self.deck, 7)
        while (top := self.deck.draw_pile.pop()).type == 'wild draw four':
            self.deck.draw_pile.insert(random.choice(range(len(self.deck.draw_pile))), top)
        Rules.apply_special_effects(top, self)
        self.deck.discard_pile.append(top)

    def play_card(self, player: Player, card: Card):
        if is_valid := Rules.is_valid_play(card, self):
            Rules.apply_special_effects(card, self)
            player.discard(self.deck, card)
        return is_valid