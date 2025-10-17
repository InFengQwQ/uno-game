import pygame, uno, multi, utils
from typing import Any, Callable
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者

# 主机同时拥有Host和Client，独立运行

pygame.init()

class UnoGame:
    # screen 只会更大，不能再小了
    SCREEN_WIDTH = W = 800
    SCREEN_HEIGHT = H = 600
    # FPS
    FPS = 165
    # colors
    BACKGROUND_COLOR = pygame.Color('#3399D9')
    TEXT_COLOR = pygame.Color('#000000')
    HINT_COLOR = pygame.Color('#DDDDDD')
    HIGHLIGHT_COLOR = pygame.Color('#FFFFFF80')

    images: dict[str, dict[str, pygame.Surface]] = {
        'info': {
            'cards_text': pygame.image.load('assets/images/info/cards_text.svg'),
            'players_2_10': pygame.image.load('assets/images/info/players_2_10.svg')
        },
        'button': {
            **{
                f'{shape}_{style}': pygame.image.load(f'assets/images/button/default/{shape}_{style}.svg')
                for shape in ['square', 'round']
                for style in ['basic', 'line', 'color']
            },
            **{
                f'arrow_{direction}': pygame.image.load(f'assets/images/button/arrow/{direction}.svg')
                for direction in ['left', 'right', 'up', 'down']
            }
        },
        'input': {
            'inactive': pygame.image.load('assets/images/input/inactive.svg'),
            'active': pygame.image.load('assets/images/input/active.svg')
        },
        'column': {
            'tag': pygame.image.load('assets/images/column/tag.svg'),
            'content': pygame.image.load('assets/images/column/content.svg'),
            'divider': pygame.image.load('assets/images/column/divider.svg')
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
        }
    }

    fonts: dict[str, pygame.font.Font] = {
        'tag': pygame.font.Font('assets/fonts/Kenney Future.ttf', 24),
        'content': pygame.font.Font('assets/fonts/Kenney Future Narrow.ttf', 16),
        'button': pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)
    }

    sounds: dict[str, pygame.mixer.Sound] = {
        'click': pygame.mixer.Sound('assets/audio/sounds/click.ogg'),
        'tap': pygame.mixer.Sound('assets/audio/sounds/tap.ogg')
    }

    # pygame.mixer.music.load('assets/audio/music.ogg') 背景音乐加载，.play()播放

    pygame.display.set_icon(pygame.image.load('icon.png'))  # 也许可在加载资源之前执行？
    pygame.display.set_caption('Uno Game')
    screen = pygame.display.set_mode((W, H), flags=0)

    clock = pygame.time.Clock()

    images = {
        category: {
            name: img.convert_alpha()
            for name, img in subdict.items()
        }
        for category, subdict in images.items()
    }

    class Column(pygame.Surface):
        def __init__(self, rect: pygame.Rect, head: float = 48, tag: str = '', contents: list[str] = []): # 也可以还是用宽高（size）毕竟Column不需要定位
            super().__init__(rect.size, pygame.SRCALPHA)

            self.back = utils.scale(UnoGame.images['column']['tag'], rect.size)
            self.front = utils.scale(UnoGame.images['column']['content'], (rect.w, rect.h - head))
            self.rect = rect
            self.tag = tag
            self.contents = contents

            self.update()
            UnoGame.column.append(self)

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
                    if content:
                        font = UnoGame.fonts['content']
                        content_surface = font.render(content, True, UnoGame.TEXT_COLOR)
                        content_rect = content_surface.get_rect(topleft=(16, 16 + UnoGame.H * 1/20 * line))
                        self.front.blit(content_surface, content_rect)
                    else:
                        divider_surface = pygame.transform.scale(UnoGame.images['column']['divider'], (self.rect.w - 32, 4))
                        divider_rect = divider_surface.get_rect(center=(self.rect.w * 1/2, 20 + UnoGame.H * 1/20 * line))
                        self.front.blit(divider_surface, divider_rect)
            self.blit(self.front, (0, head))

    class Input(pygame.Surface):    # TODO: 输入事件类型？
        def __init__(self, rect: pygame.Rect, hint: str = ''):
            super().__init__(rect.size, pygame.SRCALPHA)

            self.inactive = utils.scale(UnoGame.images['input']['inactive'], rect.size)
            self.active = utils.scale(UnoGame.images['input']['active'], rect.size)
            self.area = self.subsurface((8, 8), (rect.w - 16, rect.h - 16))

            self.rect = rect
            self.mask = pygame.mask.from_surface(self.inactive)
            self.hint = hint
            self.activated = False
            self.text = ''

            self.update()
            UnoGame.input.append(self)

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
                if self.hover:
                    UnoGame.sounds['tap'].play()
                    self.activated = True
                else:
                    self.activated = False

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
            UnoGame.button.append(self)

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
                    UnoGame.sounds['click'].play()
                    try:
                        self.action()
                    except Exception as e:
                        print(e)
                        UnoGame.Message(e)

    class Message(pygame.Surface):  # 弹出在屏幕上方的错误或提示
        def __init__(self, content: Any):
            self.content = content

    background = pygame.Surface((W, H))
    column: list[Column] = []
    input: list[Input] = []
    button: list[Button] = []
    messages: list[Message] = []

    actions: list[Callable[[], None]] = []

    host: multi.Host
    client: multi.Client

    @classmethod
    def menu(cls):
        cls.background.fill(cls.BACKGROUND_COLOR)
        info_1 = pygame.transform.scale(cls.images['info']['cards_text'], (64, 64))
        cls.background.blit(info_1, (10, 10))
        info_2 = pygame.transform.scale(cls.images['info']['players_2_10'], (64, 64))
        cls.background.blit(info_2, (84, 10))
        cls.column.clear()
        cls.input.clear()
        cls.button.clear()

        cls.Column(pygame.Rect(cls.W * 3/8, cls.H * 1/4, cls.W * 1/4, cls.H * 1/2), tag='MENU')

        cls.Button(cls.images['button']['square_color'], pygame.Rect(cls.W * 13/32, cls.H * 3/8, cls.W * 3/16, cls.H * 1/12), cls.create, slice=True, text='CREATE')
        cls.Button(cls.images['button']['square_basic'], pygame.Rect(cls.W * 13/32, cls.H * 1/2, cls.W * 3/16, cls.H * 1/12), cls.join, slice=True, text='JOIN')
        cls.Button(cls.images['button']['square_line'], pygame.Rect(cls.W * 13/32, cls.H * 5/8, cls.W * 3/16, cls.H * 1/12), quit, slice=True, text='QUIT')

    @classmethod
    def create(cls):
        cls.background.fill(cls.BACKGROUND_COLOR)
        cls.column.clear()
        cls.input.clear()
        cls.button.clear()

        contents = [
            'CREATE A ROOM WITH NAME',
            'AND YOUR PLAYER NAME.',
            ''
        ]
        cls.Column(pygame.Rect(cls.W * 5/16, cls.H * 1/4, cls.W * 3/8, cls.H * 1/2), tag='CREATE', contents=contents)

        room_name = cls.Input(pygame.Rect(cls.W * 11/32, cls.H * 1/2, cls.W * 5/32, cls.H * 1/12), hint='ROOM')
        name = cls.Input(pygame.Rect(cls.W * 17/32, cls.H * 1/2, cls.H * 1/6, cls.H * 1/12), hint='NAME')
        password = cls.Input(pygame.Rect(cls.W * 11/32, cls.H * 5/8, cls.W * 5/32, cls.H * 1/12), hint='PASSWORD')

        def host():
            try:
                cls.host = multi.Host(name.text, room_name.text, int(password.text))
                cls.client = cls.host.client
                cls.room()  # 在room中实现action...?
                cls.actions.append(cls.host.wait)
            except ValueError:
                pass    # TODO
        cls.Button(cls.images['button']['square_color'], pygame.Rect(cls.W * 17/32, cls.H * 5/8, cls.H * 1/6, cls.H * 1/12), host, slice=True, text='OK')

    @classmethod
    def join(cls):  # 刷新按钮，点一下重新加载该页面（其他页面比如create也可以刷新，room可以做成动态的也可以刷新）
        cls.background.fill(cls.BACKGROUND_COLOR)
        cls.column.clear()
        cls.input.clear()
        cls.button.clear()

        cls.Column(pygame.Rect(cls.W * 11/32, cls.H * 3/8, cls.W * 5/16, cls.H * 1/4), tag='JOIN')

        name = cls.Input(pygame.Rect(cls.W * 3/8, cls.H * 1/2, cls.W * 1/8, cls.H * 1/12), hint='NAME')

        def client():
            cls.client = multi.Client(name.text)
            multi.Room.receive()
            cls.search()
        cls.Button(cls.images['button']['square_color'], pygame.Rect(cls.W * 17/32, cls.H * 1/2, cls.W * 3/32, cls.H * 1/12), client, slice=True, text='OK')

    @classmethod
    def search(cls, rooms: list[dict[str, Any]] = multi.Room.rooms, page: int = 1):
        cls.background.fill(cls.BACKGROUND_COLOR)
        cls.column.clear()
        cls.input.clear()
        cls.button.clear()

        if rooms:
            info = rooms[page - 1]
            ip, port = info['addr']
            contents = [
                f'{info['name']}({len(info['players'])}/10)',
                f'{ip}:{port}',
                ''
            ] # 房间名（人数），主机（ip）

            password = cls.Input(pygame.Rect(cls.W * 1/2, cls.H * 1/2, cls.W * 5/32, cls.H * 1/12), hint='PASSWORD')

            cls.Button(cls.images['button']['square_line'], pygame.Rect(cls.W * 11/32, cls.H * 1/2, cls.W * 1/8, cls.H * 1/12), cls.menu, slice=True, text='BACK')  # TODO: 变成刷新键（那么就要固定到一个合适的位置了，如左下角，OK和箭头放在一边
            def access():
                cls.client.join(info, int(password.text))
                cls.room()
            cls.Button(cls.images['button']['square_color'], pygame.Rect(cls.W * 7/16, cls.H * 5/8, cls.W * 1/8, cls.H * 1/12), access, slice=True, text='OK')
            if page < len(rooms):
                def next():
                    cls.search(rooms, page + 1)
                cls.Button(cls.images['button']['arrow_right'], pygame.Rect(cls.W * 19/32, cls.H * 2/3 - 16, 32, 32), next)
            if page > 1:
                def prev():
                    cls.search(rooms, page - 1)
                cls.Button(cls.images['button']['arrow_left'], pygame.Rect(cls.W * 13/32 - 32, cls.H * 2/3 - 16, 32, 32), prev)
        else:
            contents = ['EMPTY']

            cls.Button(cls.images['button']['square_line'], pygame.Rect(cls.W * 7/16, cls.H * 5/8, cls.W * 1/8, cls.H * 1/12), cls.menu, slice=True, text='BACK')

        cls.Column(pygame.Rect(cls.W * 5/16, cls.H * 1/4, cls.W * 3/8, cls.H * 1/2), tag='SEARCH', contents=contents)   # 可以改为不同大小分别放到两个情况里

    @classmethod
    def room(cls):
        cls.background.fill(cls.BACKGROUND_COLOR)
        cls.column.clear()
        cls.input.clear()
        cls.button.clear()

        cls.Column(pygame.Rect(cls.W * 5/16, cls.H * 1/6, cls.W * 3/8, cls.H * 2/3), tag=cls.client.room.name, contents=cls.client.room.players)

    @classmethod
    def game(cls):
        pass

    @classmethod
    def run(cls):
        cls.menu()

        running = True
        while running:
            cls.screen.blit(cls.background, (0, 0))
            for column in cls.column:
                cls.screen.blit(column, column.rect)
                column.update()
            for button in cls.button:
                cls.screen.blit(button, button.rect)
            for input in cls.input:
                cls.screen.blit(input, input.rect)
            for event in pygame.event.get():
                for input in cls.input.copy():
                    input.update(event)
                for button in cls.button.copy():
                    button.update(event)
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()

            cls.clock.tick(cls.FPS)

            for action in cls.actions:
                action()

            if any(input.hover for input in cls.input):
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