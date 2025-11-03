from ui import *
from multi import *
from uno import *
import pygame
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者

# 主机同时拥有Host和Client，独立运行


BUTTON_SHAPES = ['square', 'round']
BUTTON_STYLES = ['basic', 'line', 'color']
ARROW_DIRECTIONS = ['left', 'right', 'up', 'down']

LARGE_TEXTS = ['tag']
DEFAULT_TEXTS = ['hint', 'text']
SMALL_TEXTS = ['message']
NARROW_TEXTS = ['content']

class UnoGame:
    images: dict[str, dict[str, pygame.Surface]] = {
        'info': {
            'cards_text': pygame.image.load('assets/images/info/cards_text.svg').convert_alpha(),
            'players_2_10': pygame.image.load('assets/images/info/players_2_10.svg').convert_alpha()
        },
        'column': {
            'back': pygame.image.load('assets/images/column/back.svg').convert_alpha(),
            'front': pygame.image.load('assets/images/column/front.svg').convert_alpha(),
            'divider': pygame.image.load('assets/images/column/divider.svg').convert_alpha()
        },
        'input': {
            'inactive': pygame.image.load('assets/images/input/inactive.svg').convert_alpha(),
            'active': pygame.image.load('assets/images/input/active.svg').convert_alpha()
        },
        'button': {
            **{
                f'{shape}_{style}': pygame.image.load(f'assets/images/button/default/{shape}_{style}.svg').convert_alpha()
                for shape in BUTTON_SHAPES
                for style in BUTTON_STYLES
            },
            **{
                f'arrow_{direction}': pygame.image.load(f'assets/images/button/arrow/{direction}.svg').convert_alpha()
                for direction in ARROW_DIRECTIONS
            }
        },
        'message': {
            'box': pygame.image.load('assets/images/message/box.svg').convert_alpha()
        },
        'cards': {
            'back': pygame.image.load('assets/images/cards/back.png').convert_alpha(),
            **{
                f'{color}_empty': pygame.image.load(f'assets/images/cards/{color}_empty.png').convert_alpha()
                for color in COLORS
            },
            **{
                f'{color}_{value}': pygame.image.load(f'assets/images/cards/numbers/{color}_{value}.png').convert_alpha()
                for color in COLORS
                for value in NUMBERS
            },
            **{
                f'{color}_{action}': pygame.image.load(f'assets/images/cards/actions/{color}_{action}.png').convert_alpha()
                for color in COLORS
                for action in ACTIONS
            },
            **{
                f'{BLACK_COLOR}_{wild}': pygame.image.load(f'assets/images/cards/wilds/{BLACK_COLOR}_{wild}.png').convert_alpha()
                for wild in WILDS
            }
        }
    }
    fonts: dict[str, pygame.font.Font] = {
        **{
            large: pygame.font.Font('assets/fonts/Kenney Future.ttf', 24)
            for large in LARGE_TEXTS
        },
        **{
            default: pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)
            for default in DEFAULT_TEXTS
        },
        **{
            small: pygame.font.Font('assets/fonts/Kenney Future.ttf', 8)
            for small in SMALL_TEXTS
        },
        **{
            narrow: pygame.font.Font('assets/fonts/Kenney Future Narrow.ttf', 16)
            for narrow in NARROW_TEXTS
        }
    }
    sounds: dict[str, pygame.mixer.Sound] = {
        'click': pygame.mixer.Sound('assets/sounds/click.ogg'),
        'tap': pygame.mixer.Sound('assets/sounds/tap.ogg')
    }
    # pygame.mixer.music.load('assets/audio/music.ogg') 背景音乐加载，.play()播放
    Column.back_image = images['column']['back']
    Column.front_image = images['column']['front']
    Column.divider_image = images['column']['divider']
    Column.tag_font = fonts['tag']
    Column.content_font = fonts['content']
    Input.inactive_image = images['input']['inactive']
    Input.active_image = images['input']['active']
    Input.hint_font = fonts['hint']
    Input.tap_sound = sounds['tap']
    Button.text_font = fonts['text']
    Button.click_sound = sounds['click']
    Message.message_image = images['message']['box']
    Message.message_font = fonts['message']

    host: Host
    client: Client

    counter: int = 0

    @classmethod
    def menu(cls):
        clear()

        scene.blit(pygame.transform.scale(cls.images['info']['cards_text'], (64, 64)), (10, 10))
        scene.blit(pygame.transform.scale(cls.images['info']['players_2_10'], (64, 64)), (84, 10))

        Column.columns.extend([
            Column(pygame.Rect(W * 3/8, H * 1/4, W * 1/4, H * 1/2), tag="Menu")
        ])

        Button.buttons.extend([
            Button(cls.images['button']['square_color'], pygame.Rect(W * 13/32, H * 3/8, W * 3/16, H * 1/12), cls.enter, slice=True, text="Enter"),
            Button(cls.images['button']['square_basic'], pygame.Rect(W * 13/32, H * 1/2, W * 3/16, H * 1/12), lambda: None, slice=True, text="Options"),
            Button(cls.images['button']['square_line'], pygame.Rect(W * 13/32, H * 5/8, W * 3/16, H * 1/12), quit, slice=True, text="Quit")
        ])

    @classmethod
    def enter(cls):
        clear()

        Column.columns.extend([
            Column(pygame.Rect(W * 11/32, H * 3/8, W * 5/16, H * 1/4), tag="Join")
        ])

        Input.inputs.extend([
            name := Input(pygame.Rect(W * 3/8, H * 1/2, W * 1/8, H * 1/12), hint="Name")
        ])

        @Message.catch
        def client():
            cls.client = Client(name.text)
            cls.search()
        Button.buttons.extend([
            Button(cls.images['button']['square_color'], pygame.Rect(W * 17/32, H * 1/2, W * 3/32, H * 1/12), client, slice=True, text="OK")
        ])

    @classmethod
    def search(cls, page: int = 1):
        if Room.rooms:
            page = min(page, len(Room.rooms))
            info = sorted(Room.rooms.values())[page - 1]

            clear()

            Column.columns.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    tag=f"Search({page}/{len(Room.rooms)})",
                    contents=[
                        f"{info.name}({len(info.players)}/10)",
                        f"{info.ip}:{info.port}",
                        ''
                    ]
                )
            ])

            Input.inputs.extend([
                password := Input(pygame.Rect(W * 1/2, H * 7/16, W * 5/32, H * 1/12), hint="Password")
            ])

            @Message.catch
            def access():
                try:
                    pwd = int(password.text)
                    if pwd < 0 or pwd != float(password.text):
                        raise ValueError
                except ValueError:
                    raise ValueError("Password should be a number")
                else:
                    cls.client.join(info, pwd)
                    cls.room()
            Button.buttons.extend([
                Button(cls.images['button']['square_color'], pygame.Rect(W * 11/32, H * 7/16, W * 1/8, H * 1/12), access, slice=True, text="OK"),
                Button(cls.images['button']['square_color'], pygame.Rect(W * 11/32, H * 9/16, W * 1/8, H * 1/12), cls.create, slice=True, text="Create"),
                Button(cls.images['button']['square_line'], pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12), cls.menu, slice=True, text="Back"),
                Button(cls.images['button']['square_basic'], pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12), cls.search, slice=True, text="Refresh")
            ])
            if page < len(Room.rooms):
                def next():
                    cls.search(page + 1)
                Button.buttons.extend([
                    Button(cls.images['button']['arrow_right'], pygame.Rect(W * 19/32, H * 29/48 - 16, 32, 32), next)
                ])
            if page > 1:
                def prev():
                    cls.search(page - 1)
                Button.buttons.extend([
                    Button(cls.images['button']['arrow_left'], pygame.Rect(W * 9/16 - 32, H * 29/48 - 16, 32, 32), prev)
                ])
        else:
            clear()

            Column.columns.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    tag="Search",
                    contents=[
                        "Empty"
                    ]
                )
            ])

            Button.buttons.extend([
                Button(cls.images['button']['square_color'], pygame.Rect(W * 11/32, H * 9/16, W * 1/8, H * 1/12), cls.create, slice=True, text="Create"),
                Button(cls.images['button']['square_line'], pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12), cls.menu, slice=True, text="Back"),
                Button(cls.images['button']['square_basic'], pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12), cls.search, slice=True, text="Refresh")
            ])

    @classmethod
    def create(cls):
        clear()

        Column.columns.extend([
            Column(pygame.Rect(W * 5/16, H * 1/4, W * 3/8, H * 1/2),
                tag="Create",
                contents = [
                    "Create a room with name",
                    "and your player name.",
                    ''
                ]
            )
        ])

        Input.inputs.extend([
            name := Input(pygame.Rect(W * 17/32, H * 1/2, H * 1/6, H * 1/12), hint="Name"),
            password := Input(pygame.Rect(W * 11/32, H * 5/8, W * 5/32, H * 1/12), hint="Password")
        ])

        @Message.catch
        def host():
            try:
                pwd = int(password.text)
                if pwd < 0 or pwd != float(password.text):
                    raise ValueError
            except ValueError:
                raise ValueError("Password should be a number")    # TODO: 在ui中添加提示（实为错误，Exception的子类)
            else:
                cls.host = Host(cls.client, name.text, pwd)
                cls.room()
        Button.buttons.extend([
            Button(cls.images['button']['square_line'], pygame.Rect(W * 11/32, H * 1/2, W * 5/32, H * 1/12), cls.search, slice=True, text="Back"),
            Button(cls.images['button']['square_color'], pygame.Rect(W * 17/32, H * 5/8, H * 1/6, H * 1/12), host, slice=True, text="OK")
        ])

    @classmethod
    def room(cls):
        if hasattr(cls, 'host'):
            clear()

            Column.columns.extend([
                Column(pygame.Rect(W * 5/16, H * 1/8, W * 3/8, H * 3/4), tag=cls.client.room.name, contents=cls.client.room.players)
            ])

            def back():
                cls.host.close()
                del cls.host
                cls.client.reset()
                cls.search()
            Button.buttons.extend([
                Button(cls.images['button']['square_line'], pygame.Rect(W * 11/32, H * 3/4, W * 1/8, H * 1/12), back, slice=True, text="Back"),
                Button(cls.images['button']['square_color'], pygame.Rect(W * 17/32, H * 3/4, W * 1/8, H * 1/12), cls.game, slice=True, text="Start")
            ])
        else:
            clear()

            Column.columns.extend([
                Column(pygame.Rect(W * 5/16, H * 1/8, W * 3/8, H * 3/4), tag=cls.client.room.name, contents=cls.client.room.players)
            ])

            def back():
                cls.client.reset()
                cls.search()
            Button.buttons.extend([
                Button(cls.images['button']['square_line'], pygame.Rect(W * 7/16, H * 3/4, W * 1/8, H * 1/12), back, slice=True, text="Back")
            ])

    @classmethod
    def game(cls):
        pass

    @classmethod
    def run(cls):
        cls.menu()

        @Message.catch
        def network():
            if hasattr(cls, 'client'):
                cls.client.run()
            if hasattr(cls, 'host'):
                cls.host.run()

        while update():
            if cls.counter > FPS * RUN_INTERVAL:
                network()
                cls.counter = 0
            else:
                cls.counter += 1
        
        quit()


# def main():
#     names = ['Alice', 'Bob']
#     players = [Player(name) for name in names]
#     # 到时候尽量多把代码封装到类方法里
#     while True:
#         game = Game(players)
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
#                 # card: Optional[Card]
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
#                 if Rules.is_winner(player):
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