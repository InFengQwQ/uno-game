from . import BLACK_COLOR, Card, Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Game


class Rules:
    @staticmethod
    def is_valid_play(card: Card, game: 'Game'):
        top = game.deck.discard_pile[-1]
        if card.color == BLACK_COLOR:
            return True
        elif card.color == top.color or (card.type == top.type and card.value == top.value):
            return True
        else:
            return False

    @staticmethod
    def is_able_to_play(player: Player, game: 'Game'):
        return any(Rules.is_valid_play(card, game) for card in player.hand)

    @staticmethod
    def apply_special_effects(card: Card, game: 'Game'):
        if card.type == 'skip':
            game.turn += 1 if game.reverse else -1
        elif card.type == 'reverse':
            if len(game.players) == 2:
                game.turn -= 1
            else:
                game.reverse = not game.reverse
        elif card.type == 'draw_two':
            game.draw += 2
        elif card.type == 'draw_four':
            game.draw += 4

    @staticmethod
    def is_winner(player: Player):
        return not player.hand

    @staticmethod
    def score(game: 'Game'):
        return sum(sum(card.value for card in player.hand) for player in game.players)