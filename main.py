import pygame, multi, uno, utils
from typing import Callable
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者


pygame.init()

class UnoGame:  # 尝试一下改用@classmethod？self.screen什么的全放到类里面（或者数据类也可以）。这样的话也许可以在创建Button时调用cls.buttons
    # colors
    BACKGROUND = pygame.Color('#3399D9')
    TEXT_COLOR = pygame.Color('#000000')
    HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')

    # images
    images: dict[str, dict[str, pygame.Surface]] = {'info': {}, 'cards': {}, 'buttons': {}, 'columns': {}}
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
    SHAPES = ['rectangle', 'round', 'square']
    STYLES = ['flat', 'depth']
    for shape, style in zip(SHAPES, STYLES):
        images['buttons'][f'{shape}_{style}'] = pygame.image.load(f'assets/images/buttons/{shape}_{style}.png')
        # columns
    images['columns']['tag'] = pygame.image.load(f'assets/images/columns/tag.png')
    images['columns']['content'] = pygame.image.load(f'assets/images/columns/content.png')

    # fonts
    fonts: dict[str, pygame.font.Font] = {}
    fonts['tag'] = pygame.font.Font('assets/fonts/Kenney Future.ttf', 24)
    fonts['content'] = pygame.font.Font('assets/fonts/Kenney Future Narrow.ttf', 8)
    fonts['button'] = pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)

    class Button(pygame.Surface):
        def __init__(self, image: pygame.Surface, rect: pygame.Rect, action: Callable[[], None], text: str = ''):
            super().__init__(rect.size, pygame.SRCALPHA)

            self.surface = utils.scale(image, rect.width, rect.height)
            if text:
                font = UnoGame.fonts['button']
                text_surface = font.render(text, True, UnoGame.TEXT_COLOR)
                text_rect = text_surface.get_rect(center=self.get_rect().center)
                self.surface.blit(text_surface, text_rect)

            self.rect = rect
            self.action = action
            self.mask = pygame.mask.from_surface(self.surface)
            self.highlight = self.mask.to_surface(setcolor=UnoGame.HIGHLIGHT_COLOR, unsetcolor=(0, 0, 0, 0))

        @property
        def hover(self):
            mx, my = pygame.mouse.get_pos()
            x, y = self.rect.topleft
            pos = mx - x, my - y
            try:
                return self.mask.get_at(pos)
            except IndexError:
                return False

        def update(self, event: pygame.event.Event):
            self.blit(self.surface, (0, 0))
            if self.hover:
                self.blit(self.highlight, (0, 0))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.action()

    class Column(pygame.Surface):
        def __init__(self, rect: pygame.Rect, head: int, tag: str = '', content: str = ''): # 也可以还是用宽高（size）毕竟Column不需要定位
            super().__init__(rect.size, pygame.SRCALPHA)

            self.tag = utils.scale(UnoGame.images['columns']['tag'], rect.width, rect.height)
            if tag:
                font = UnoGame.fonts['tag']
                tag_surface = font.render(tag, True, UnoGame.TEXT_COLOR)
                tag_rect = tag_surface.get_rect(center=(rect.width / 2, head / 2))
                self.tag.blit(tag_surface, tag_rect)

            self.content = utils.scale(UnoGame.images['columns']['content'], rect.width, rect.height - head)
            if content:
                font = UnoGame.fonts['content']
                content_surface = font.render(content, True, UnoGame.TEXT_COLOR)
                content_rect = content_surface.get_rect(topleft=(16, 16))
                self.content.blit(content_surface, content_rect)

            self.tag.blit(self.content, (0, head))
            self.blit(self.tag, (0, 0))

            self.rect = rect

    def __init__(self):
        pygame.display.set_icon(pygame.image.load('icon.png'))
        pygame.display.set_caption('Uno Game')
        self.screen = pygame.display.set_mode((800, 600), flags=0)

        for type in UnoGame.images:
            for image in UnoGame.images[type]:
                UnoGame.images[type][image] = UnoGame.images[type][image].convert_alpha()   # 可以修改（稍微有点低级了看着哈哈

        self.buttons: list[UnoGame.Button] = []

    def menu(self):
        self.screen.fill(self.BACKGROUND)
        column = UnoGame.Column(pygame.Rect(300, 150, 200, 300), 50, 'MENU')
        self.screen.blit(column, column.rect)

        info_1 = pygame.transform.scale(UnoGame.images['info']['cards_text'], (64, 64))
        self.screen.blit(info_1, (10, 10))
        info_2 = pygame.transform.scale(UnoGame.images['info']['players_2_10'], (64, 64))
        self.screen.blit(info_2, (84, 10))

        self.buttons.clear()
        self.buttons.append(UnoGame.Button(UnoGame.images['buttons']['rectangle_flat'], pygame.Rect(325, 225, 150, 50), print, 'CREATE'))
        self.buttons.append(UnoGame.Button(UnoGame.images['buttons']['rectangle_flat'], pygame.Rect(325, 300, 150, 50), print, 'JOIN'))
        self.buttons.append(UnoGame.Button(UnoGame.images['buttons']['rectangle_flat'], pygame.Rect(325, 375, 150, 50), quit, 'QUIT'))

    def run(self):
        self.menu()

        running = True
        while running:
            for event in pygame.event.get():
                for button in self.buttons:
                    self.screen.blit(button, button.rect)
                    button.update(event)
                pass
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.update()

        pygame.quit()


# def main():
#     names = ['Alice', 'Bob']
#     players = [uno.Player(name) for name in names]
#     # 到时候尽量多把代码封装到类方法里
#     while True:
#         game = uno.Game(players)
#         game.turn += game.reverse
#         player = game.players[game.turn]   # the first player
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