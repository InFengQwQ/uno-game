import pygame, multi, uno
from typing import Any, Callable
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者


pygame.init()

class UnoGame:
    # colors
    BACKGROUND = pygame.Color('#3399D9')
    TEXT_COLOR = pygame.Color('#000000')
    HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')

    class Button:
        def __init__(self, image: pygame.Surface, action: Callable[[], None], text: str = '', font: Any = None):
            self.surface = image
            if text:
                _font: pygame.font.Font = font
                text_surface = _font.render(text, True, UnoGame.TEXT_COLOR)
                text_rect = text_surface.get_rect(center=self.surface.get_rect().center)
                self.surface.blit(text_surface, text_rect)

            self.action = action

        @property
        def surface(self):
            return self._surface

        @surface.setter
        def surface(self, value: pygame.Surface):
            self._surface = value
            self._rect = None
            self._mask = None
            self._highlight = None

        @property
        def rect(self):
            if not self._rect:
                self._rect = self.surface.get_rect()
            return self._rect

        @property
        def mask(self):
            if not self._mask:
                self._mask = pygame.mask.from_surface(self.surface)
            return self._mask

        @property
        def highlight(self):
            if not self._highlight:
                self._highlight = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                self._highlight.fill(UnoGame.HIGHLIGHT_COLOR)
            return self._highlight

        @property
        def hover(self):
            mx, my = pygame.mouse.get_pos()
            x, y = self.rect.topleft
            pos = mx - x, my - y
            try:
                return self.mask.get_at(pos)
            except IndexError:
                return False

        def update(self, event: pygame.event.Event):    # handle_event
            self.display = self.surface.copy()
            if self.hover:
                self.display.blit(self.highlight, (0, 0), special_flags=pygame.BLEND_ADD)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.action()

    def __init__(self):
        self.images = self._images
        self.fonts = self._fonts

        pygame.display.set_icon(pygame.image.load('icon.png'))
        pygame.display.set_caption('Uno Game')
        self.screen = pygame.display.set_mode((800, 600), flags=0)

        self.buttons: list[UnoGame.Button] = []

    @property
    def _images(self):
        images: dict[str, dict[str, pygame.Surface]] = {'info': {}, 'cards': {}, 'buttons':{}}
        # info
        images['info']['cards_text'] = pygame.image.load('assets/images/info/cards_text.svg')
        images['info']['players_2_10'] = pygame.image.load('assets/images/info/players_2_10.svg')
        # cards
        images['cards']['back'] = pygame.image.load('assets/images/cards/back.png')
        for color in uno.deck.COLORS:
            images['cards'][f'{color}_empty'] = pygame.image.load(f'assets/images/cards/{color}_empty.png')
            for value in range(10):
                images['cards'][f'{color}_{value}'] = pygame.image.load(f'assets/images/cards/numbers/{color}_{value}.png')
            for action in uno.deck.ACTIONS:
                images['cards'][f'{color}_{action}'] = pygame.image.load(f'assets/images/cards/actions/{color}_{action}.png')
        for wild in uno.deck.WILDS:
            images['cards'][wild] = pygame.image.load(f'assets/images/cards/wilds/{wild}.png')
        # buttons
        images['buttons']['']
        return images

    @property
    def _fonts(self):
        fonts: dict[str, pygame.font.Font] = {}
        fonts['title'] = pygame.font.Font('assets/fonts/Kenney Future.ttf', 24)
        return fonts

    def menu(self):
        self.screen.fill(self.BACKGROUND)
        column1 = uno.utils.scale('x', 100, 100, self.images['buttons'][''])
        button1 = self.Button()

    def run(self):
        pass


# def main():
#     names = ['Alice', 'Bob']
#     players = [uno.Player(name) for name in names]
#     # 到时候尽量多把代码封装到类方法里
#     while True:
#         game = uno.Game(players)
#         game.turn += game.reverse
#         player = game.players[game.turn]   # the fi rst player
#         while True:
#             try:
#                 if game.deck.discard_pile[-1].type == 'Wild Draw Four' and game.draw:
#                     # +4 challenge
#                     pass
#                     if True:
#                         if True:
#                             game.players[game.turn - 1 if game.reverse else -1].draw(game.deck, game.draw)
#                             game.draw = 0
#                             continue
#                         else:
#                             game.draw += 2
#                 if game.draw:
#                     player.draw(game.deck, game.draw)
#                     game.draw = 0
#                     continue
#                 # while? or None to continue?
#                 # card: Optional[uno.Card]
#                 if card:
#                     if game.play_card(player, card):
#                         # play card
#                         pass
#                 elif (game.deck.draw_pile + game.deck.discard_pile):   # draw one and select whether to discard or reserve(or yes -> invalid -> reserve) 
#                     player.draw(game.deck)
#                     # draw
#                     pass
#                     if True:
#                         card = player.hand[-1]
#                         if game.play_card(player, card):
#                             # play card
#                             pass
#                         else:
#                             # reserve
#                             pass
#             finally:
#                 if uno.Rules.is_winner(player):
#                     break
#                 else:
#                     game.turn += 1 if game.reverse else -1
#                     game.turn %= len(game.players)
#                     player = game.players[game.turn]    # the next player
#         # win
#         pass
#         game.players[game.turn + 1 if game.reverse else game.turn - 1].draw(game.deck, game.draw)
#         player.score
#         players = [player for player in game.players[game.turn:] + game.players[:game.turn]]


if __name__ == '__main__':
    UnoGame().run()