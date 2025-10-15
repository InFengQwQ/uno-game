import pygame, multi, uno, utils
from typing import Any, Callable
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者

# 主机同时拥有Host和Client，独立运行

pygame.init()

class UnoGame:
    # colors
    BACKGROUND = pygame.Color('#3399D9')
    TEXT_COLOR = pygame.Color('#000000')
    HINT_COLOR = pygame.Color('#DDDDDD')
    HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')

    # images
    images: dict[str, dict[str, pygame.Surface]] = {
        'info': {
            'cards_text': pygame.image.load('assets/images/info/cards_text.svg'),
            'players_2_10': pygame.image.load('assets/images/info/players_2_10.svg')
        },
        'cards': {
            'back': pygame.image.load('assets/images/cards/back.png'),
            **{
                f'{color}_empty': pygame.image.load(f'assets/images/cards/{color}_empty.png')
                for color in uno.deck.COLORS
            },
            **{
                f'{color}_{value}': pygame.image.load(f'assets/images/cards/numbers/{color}_{value}.png')
                for color in uno.deck.COLORS
                for value in range(10)
            },
            **{
                f'{color}_{action}': pygame.image.load(f'assets/images/cards/actions/{color}_{action}.png')
                for color in uno.deck.COLORS
                for action in uno.deck.ACTIONS
            },
            **{
                wild: pygame.image.load(f'assets/images/cards/wilds/{wild}.png')
                for wild in uno.deck.WILDS
            }
        },
        'buttons': {
            **{
                f'{shape}_{style}': pygame.image.load(f'assets/images/buttons/defaults/{shape}_{style}.png')
                for shape in ['square', 'rectangle', 'round']
                for style in ['basic', 'line', 'color']
            },
            'square_checkmark': pygame.image.load('assets/images/buttons/square_checkmark.png'),
            'square_cross': pygame.image.load('assets/images/buttons/square_cross.png'),
            'arrow_right': pygame.image.load('assets/images/buttons/arrow_right.png'),
            'arrow_left': pygame.image.load('assets/images/buttons/arrow_left.png')
        },
        'inputs': {
            'inactive': pygame.image.load('assets/images/inputs/inactive.svg'),
            'active': pygame.image.load('assets/images/inputs/active.svg')
        },
        'columns': {
            'tag': pygame.image.load('assets/images/columns/tag.png'),
            'content': pygame.image.load('assets/images/columns/content.png'),
            'refresh': pygame.image.load('assets/images/columns/refresh.png')
        }
    }

    # fonts
    fonts: dict[str, pygame.font.Font] = {
        'tag': pygame.font.Font('assets/fonts/Kenney Future.ttf', 24),
        'content': pygame.font.Font('assets/fonts/Kenney Future Narrow.ttf', 16),
        'button': pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)
    }

    pygame.display.set_icon(pygame.image.load('icon.png'))
    pygame.display.set_caption('Uno Game')
    screen = pygame.display.set_mode((800, 600), flags=0)

    images = {
        category: {
            name: img.convert_alpha()
            for name, img in subdict.items()
        }
        for category, subdict in images.items()
    }

    class Input(pygame.Surface):    # TODO: 输入事件类型？
        def __init__(self, rect: pygame.Rect, hint: str = ''):
            super().__init__(rect.size, pygame.SRCALPHA)

            self.inactive = utils.scale(UnoGame.images['inputs']['inactive'], rect.size)
            self.active = utils.scale(UnoGame.images['inputs']['active'], rect.size)
            self.area = self.subsurface((8, 8), (rect.w - 16, rect.h - 16))

            self.rect = rect
            self.mask = pygame.mask.from_surface(self.inactive)
            self.hint = hint
            self.activated = False
            self.text = ''

            self.update()
            UnoGame.inputs.append(self)

        @property
        def hover(self):
            mx, my = pygame.mouse.get_pos()
            x, y = self.rect.topleft
            pos = mx - x, my - y
            try:
                return self.mask.get_at(pos)
            except IndexError:
                return False

        def update(self, event: pygame.event.Event = pygame.event.Event(pygame.USEREVENT)):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.activated = self.hover

            if self.activated:
                if event.type == pygame.TEXTINPUT:
                    self.text += event.text
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and self.text:
                    self.text = self.text[:-1]
                self.blit(self.active, (0, 0))
            else:
                self.blit(self.inactive, (0, 0))

            if self.text:
                font = pygame.font.SysFont(None, self.area.get_rect().h)
                text_surface = font.render(self.text, True, UnoGame.TEXT_COLOR)
                text_rect = text_surface.get_rect(midright=self.area.get_rect().midright)
                self.area.blit(text_surface, text_rect)
            else:
                if self.hint:
                    font = UnoGame.fonts['button']
                    hint_surface = font.render(self.hint, True, UnoGame.HINT_COLOR)
                    hint_rect = hint_surface.get_rect(center=self.area.get_rect().center)
                    self.area.blit(hint_surface, hint_rect)

    class Button(pygame.Surface):
        def __init__(self, image: pygame.Surface, rect: pygame.Rect, action: Callable[[], None], slice: bool = False, text: str = ''):
            super().__init__(rect.size, pygame.SRCALPHA)

            if slice:
                self.surface = utils.scale(image, rect.size)
            else:
                self.surface = pygame.transform.smoothscale(image, rect.size)
            if text:
                font = UnoGame.fonts['button']
                text_surface = font.render(text, True, UnoGame.TEXT_COLOR)
                text_rect = text_surface.get_rect(center=self.get_rect().center)
                self.surface.blit(text_surface, text_rect)

            self.rect = rect
            self.action = action
            self.mask = pygame.mask.from_surface(self.surface)
            self.highlight = self.mask.to_surface(setcolor=UnoGame.HIGHLIGHT_COLOR, unsetcolor=(0, 0, 0, 0))

            self.update()
            UnoGame.buttons.append(self)

        @property
        def hover(self):
            mx, my = pygame.mouse.get_pos()
            x, y = self.rect.topleft
            pos = mx - x, my - y
            try:
                return self.mask.get_at(pos)
            except IndexError:
                return False

        def update(self, event: pygame.event.Event = pygame.event.Event(pygame.USEREVENT)):
            self.blit(self.surface, (0, 0))
            if self.hover:
                self.blit(self.highlight, (0, 0))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.action()

    class Column(pygame.Surface):
        def __init__(self, rect: pygame.Rect, head: int, tag: str = '', contents: list[str] = [], refresh: bool = False): # 也可以还是用宽高（size）毕竟Column不需要定位
            super().__init__(rect.size, pygame.SRCALPHA)

            self.back = utils.scale(UnoGame.images['columns']['tag'], rect.size)
            self.front = utils.scale(UnoGame.images['columns']['content'], (rect.width, rect.height - head))
            self.rect = rect
            self.tag = tag
            self.contents = contents

            self.update()
            if refresh:
                UnoGame.Button(UnoGame.images['columns']['refresh'], pygame.Rect(rect.right - 50, rect.top + 10, 41, 36), self.update)

        def update(self):
            head = self.back.get_height() - self.front.get_height()

            if self.tag:
                font = UnoGame.fonts['tag']
                tag_surface = font.render(self.tag, True, UnoGame.TEXT_COLOR)
                tag_rect = tag_surface.get_rect(center=self.get_rect(top=head / 2).midtop)
                self.back.blit(tag_surface, tag_rect)
            self.blit(self.back, (0, 0))

            if self.contents:
                for line, content in enumerate(self.contents):
                    font = UnoGame.fonts['content']
                    content_surface = font.render(content, True, UnoGame.TEXT_COLOR)
                    content_rect = content_surface.get_rect(topleft=(16, 16 + 32 * line))
                    self.front.blit(content_surface, content_rect)
            self.blit(self.front, (0, head))

            UnoGame.columns.append(self)

    class Message(pygame.Surface):  # 弹出在屏幕上方的错误或提示
        pass

    inputs: list[Input] = []
    buttons: list[Button] = []
    columns: list[Column] = []
    messages: list[Message] = []

    host: multi.Host
    client: multi.Client

    @classmethod
    def menu(cls):
        cls.inputs.clear()
        cls.buttons.clear()
        cls.screen.fill(cls.BACKGROUND)
        info_1 = pygame.transform.scale(cls.images['info']['cards_text'], (64, 64))
        cls.screen.blit(info_1, (10, 10))
        info_2 = pygame.transform.scale(cls.images['info']['players_2_10'], (64, 64))
        cls.screen.blit(info_2, (84, 10))

        cls.Button(cls.images['buttons']['rectangle_color'], pygame.Rect(325, 225, 150, 50), cls.create, slice=True, text='CREATE')
        cls.Button(cls.images['buttons']['rectangle_basic'], pygame.Rect(325, 300, 150, 50), cls.join, slice=True, text='JOIN')
        cls.Button(cls.images['buttons']['rectangle_line'], pygame.Rect(325, 375, 150, 50), quit, slice=True, text='QUIT')

        cls.Column(pygame.Rect(300, 150, 200, 300), 50, 'MENU')

    @classmethod
    def create(cls):
        cls.inputs.clear()
        cls.buttons.clear()
        cls.screen.fill(cls.BACKGROUND)

        room_name = cls.Input(pygame.Rect(275, 300, 125, 50), 'ROOM')
        name = cls.Input(pygame.Rect(425, 300, 100, 50), 'NAME')
        password = cls.Input(pygame.Rect(275, 375, 125, 50), 'PASSWORD')

        def host():
            try:
                cls.host = multi.Host(name.text, room_name.text, int(password.text))
                cls.client = cls.host.client
                cls.room()
            except ValueError:
                pass    # TODO

        cls.Button(cls.images['buttons']['rectangle_color'], pygame.Rect(425, 375, 100, 50), host, slice=True, text='OK')

        cls.Column(pygame.Rect(250, 150, 300, 300), 50,
            tag='CREATE',
            contents=['CREATE A ROOM WITH NAME', 'AND YOUR PLAYER NAME.']
        )

    @classmethod
    def join(cls):  # 刷新按钮，点一下重新加载该页面（其他页面比如create也可以刷新，room可以做成动态的也可以刷新）
        cls.inputs.clear()
        cls.buttons.clear()
        cls.screen.fill(cls.BACKGROUND)

        name = cls.Input(pygame.Rect(325, 300, 100, 50), 'NAME')

        def client():
            cls.client = multi.Client(name.text)
            cls.search(sorted(cls.client.receive(), key=lambda info: info['name']))

        cls.Button(cls.images['buttons']['square_checkmark'], pygame.Rect(443, 309, 32, 32), client)

        cls.Column(pygame.Rect(300, 225, 200, 150), 50, 'JOIN')

    @classmethod
    def search(cls, rooms: list[dict[str, Any]], page: int = 1):
        cls.inputs.clear()
        cls.buttons.clear()
        cls.screen.fill(cls.BACKGROUND)

        if rooms:
            info = rooms[page - 1]
            ip, port = info['addr']
            contents = [
                f'{info['name']}({len(info['players'])}/10)',
                f'{ip}:{port}'
            ] # 房间名（人数），主机（ip）

            password = cls.Input(pygame.Rect(400, 300, 125, 50), 'PASSWORD')

            def next():
                cls.search(rooms, page + 1)

            def prev():
                cls.search(rooms, page - 1)

            def access():
                if cls.client.join(info, int(password.text)):
                    cls.room()
                else:
                    cls.search(sorted(cls.client.receive(), key=lambda info: info['name']))    # TODO: Error

            cls.Button(cls.images['buttons']['rectangle_basic'], pygame.Rect(275, 300, 100, 50), cls.join, slice=True, text='REJOIN')
            cls.Button(cls.images['buttons']['rectangle_color'], pygame.Rect(350, 375, 100, 50), access, slice=True, text='OK')
            if page < len(rooms):
                cls.Button(cls.images['buttons']['arrow_right'], pygame.Rect(475, 384, 32, 32), next)
            if page > 1:
                cls.Button(cls.images['buttons']['arrow_left'], pygame.Rect(293, 384, 32, 32), prev)
        else:
            contents = ['EMPTY']

            cls.Button(cls.images['buttons']['rectangle_basic'], pygame.Rect(350, 350, 100, 50), cls.join, slice=True, text='REJOIN')

        cls.Column(pygame.Rect(250, 150, 300, 300), 50, 'SEARCH', contents, True)

    @classmethod
    def room(cls):
        cls.inputs.clear()
        cls.buttons.clear()
        cls.screen.fill(cls.BACKGROUND)

        players: Any = cls.client.room.info['players']

        cls.Column(pygame.Rect(250, 100, 300, 400), 50, cls.client.room.name, players, True)

    @classmethod
    def game(cls):
        pass

    @classmethod
    def run(cls):
        cls.menu()

        running = True
        while running:
            while cls.columns:
                # cls.screen.fill(cls.BACKGROUND)
                column = cls.columns.pop()
                cls.screen.blit(column, column.rect)
            for button in cls.buttons:
                cls.screen.blit(button, button.rect)
            for input in cls.inputs:
                cls.screen.blit(input, input.rect)
            for event in pygame.event.get():
                for input in cls.inputs:
                    input.update(event)
                for button in cls.buttons:
                    button.update(event)
                pass
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.update()

            if any(input.hover for input in cls.inputs):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
    UnoGame.run()