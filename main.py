import pygame, multi, ui, uno
from typing import Any, Callable
# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者

# 主机同时拥有Host和Client，独立运行

# W和H在column里也有，应该改，考虑一下它们的归属问题（问一下ai结构问题吧） （已改）
class UnoGame:
    images: dict[str, dict[str, pygame.Surface]] = {
        'info': {
            'cards_text': pygame.image.load('assets/images/info/cards_text.svg').convert_alpha(),
            'players_2_10': pygame.image.load('assets/images/info/players_2_10.svg').convert_alpha()
        },
        'button': {
            **{
                f'{shape}_{style}': pygame.image.load(f'assets/images/button/default/{shape}_{style}.svg').convert_alpha()
                for shape in ['square', 'round']
                for style in ['basic', 'line', 'color']
            },
            **{
                f'arrow_{direction}': pygame.image.load(f'assets/images/button/arrow/{direction}.svg').convert_alpha()
                for direction in ['left', 'right', 'up', 'down']
            }
        },
        'input': {
            'inactive': pygame.image.load('assets/images/input/inactive.svg').convert_alpha(),
            'active': pygame.image.load('assets/images/input/active.svg').convert_alpha()
        },
        'column': {
            'back': pygame.image.load('assets/images/column/back.svg').convert_alpha(),
            'front': pygame.image.load('assets/images/column/front.svg').convert_alpha(),
            'divider': pygame.image.load('assets/images/column/divider.svg').convert_alpha()
        },
        'cards': {
            'back': pygame.image.load('assets/images/cards/back.png').convert_alpha(),
            **{
                f'{color}_empty': pygame.image.load(f'assets/images/cards/{color}_empty.png').convert_alpha()
                for color in uno.COLORS
            },
            **{
                f'{color}_{value}': pygame.image.load(f'assets/images/cards/numbers/{color}_{value}.png').convert_alpha()
                for color in uno.COLORS
                for value in range(10)
            },
            **{
                f'{color}_{action}': pygame.image.load(f'assets/images/cards/actions/{color}_{action}.png').convert_alpha()
                for color in uno.COLORS
                for action in uno.ACTIONS
            },
            **{
                wild: pygame.image.load(f'assets/images/cards/wilds/{wild}.png').convert_alpha()
                for wild in uno.WILDS
            }
        }
    }
    fonts: dict[str, pygame.font.Font] = {
        **{
            default: pygame.font.Font('assets/fonts/Kenney Future.ttf', 24)
            for default in ['tag']
        },
        **{
            small: pygame.font.Font('assets/fonts/Kenney Future.ttf', 16)
            for small in ['hint', 'text']
        },
        **{
            narrow: pygame.font.Font('assets/fonts/Kenney Future Narrow.ttf', 16)
            for narrow in ['content']
        }
    }
    sounds: dict[str, pygame.mixer.Sound] = {
        'click': pygame.mixer.Sound('assets/audio/sounds/click.ogg'),
        'tap': pygame.mixer.Sound('assets/audio/sounds/tap.ogg')
    }
    # pygame.mixer.music.load('assets/audio/music.ogg') 背景音乐加载，.play()播放
    ui.Column.back_image = images['column']['back']
    ui.Column.front_image = images['column']['front']
    ui.Column.divider_image = images['column']['divider']
    ui.Column.tag_font = fonts['tag']
    ui.Column.content_font = fonts['content']
    ui.Input.inactive_image = images['input']['inactive']
    ui.Input.active_image = images['input']['active']
    ui.Input.hint_font = fonts['hint']
    ui.Input.tap_sound = sounds['tap']
    ui.Button.text_font = fonts['text']
    ui.Button.click_sound = sounds['click']

    host: multi.Host
    client: multi.Client

    actions: list[Callable[[], None]] = []

    @classmethod
    def menu(cls):
        ui.clear()

        ui.scene.blit(pygame.transform.scale(cls.images['info']['cards_text'], (64, 64)), (10, 10))
        ui.scene.blit(pygame.transform.scale(cls.images['info']['players_2_10'], (64, 64)), (84, 10))

        ui.columns.extend([
            ui.Column(pygame.Rect(ui.W * 3/8, ui.H * 1/4, ui.W * 1/4, ui.H * 1/2), tag='MENU')
        ])

        ui.buttons.extend([
            ui.Button(cls.images['button']['square_color'], pygame.Rect(ui.W * 13/32, ui.H * 3/8, ui.W * 3/16, ui.H * 1/12), cls.create, slice=True, text='CREATE'),
            ui.Button(cls.images['button']['square_basic'], pygame.Rect(ui.W * 13/32, ui.H * 1/2, ui.W * 3/16, ui.H * 1/12), cls.join, slice=True, text='JOIN'),
            ui.Button(cls.images['button']['square_line'], pygame.Rect(ui.W * 13/32, ui.H * 5/8, ui.W * 3/16, ui.H * 1/12), quit, slice=True, text='QUIT')
        ])

    @classmethod
    def create(cls):
        ui.clear()

        contents = [
            'CREATE A ROOM WITH NAME',
            'AND YOUR PLAYER NAME.',
            ''
        ]
        ui.columns.extend([
            ui.Column(pygame.Rect(ui.W * 5/16, ui.H * 1/4, ui.W * 3/8, ui.H * 1/2), tag='CREATE', contents=contents)
        ])

        ui.inputs.extend([
            room_name := ui.Input(pygame.Rect(ui.W * 11/32, ui.H * 1/2, ui.W * 5/32, ui.H * 1/12), hint='ROOM'),
            name := ui.Input(pygame.Rect(ui.W * 17/32, ui.H * 1/2, ui.H * 1/6, ui.H * 1/12), hint='NAME'),
            password := ui.Input(pygame.Rect(ui.W * 11/32, ui.H * 5/8, ui.W * 5/32, ui.H * 1/12), hint='PASSWORD')
        ])

        def host():
            try:
                cls.host = multi.Host(name.text, room_name.text, int(password.text))
                cls.client = cls.host.client
                cls.room()  # 在room中实现action...?
                cls.actions.append(cls.host.wait)
            except ValueError:
                pass    # TODO
        ui.buttons.extend([
            ui.Button(cls.images['button']['square_color'], pygame.Rect(ui.W * 17/32, ui.H * 5/8, ui.H * 1/6, ui.H * 1/12), host, slice=True, text='OK')
        ])

    @classmethod
    def join(cls):  # 刷新按钮，点一下重新加载该页面（其他页面比如create也可以刷新，room可以做成动态的也可以刷新）
        ui.clear()

        ui.columns.extend([
            ui.Column(pygame.Rect(ui.W * 11/32, ui.H * 3/8, ui.W * 5/16, ui.H * 1/4), tag='JOIN')
        ])

        ui.inputs.extend([
            name := ui.Input(pygame.Rect(ui.W * 3/8, ui.H * 1/2, ui.W * 1/8, ui.H * 1/12), hint='NAME')
        ])

        def client():
            cls.client = multi.Client(name.text)
            multi.Room.receive()
            cls.search()
        ui.buttons.extend([
            ui.Button(cls.images['button']['square_color'], pygame.Rect(ui.W * 17/32, ui.H * 1/2, ui.W * 3/32, ui.H * 1/12), client, slice=True, text='OK')
        ])

    @classmethod
    def search(cls, rooms: list[dict[str, Any]] = multi.Room.rooms, page: int = 1):
        if rooms:
            ui.clear()

            info = rooms[page - 1]
            ip, port = info['addr']
            ui.columns.extend([
                ui.Column(
                    pygame.Rect(ui.W * 5/16, ui.H * 1/4, ui.W * 3/8, ui.H * 1/2),
                    tag='SEARCH',
                    contents=[
                        f'{info['name']}({len(info['players'])}/10)',
                        f'{ip}:{port}',
                        ''
                    ] # 房间名（人数），主机（ip）
                )
            ])

            ui.inputs.extend([
                password := ui.Input(pygame.Rect(ui.W * 1/2, ui.H * 1/2, ui.W * 5/32, ui.H * 1/12), hint='PASSWORD')
            ])

            def access():
                cls.client.join(info, int(password.text))
                cls.room()
            ui.buttons.extend([
                ui.Button(cls.images['button']['square_line'], pygame.Rect(ui.W * 11/32, ui.H * 1/2, ui.W * 1/8, ui.H * 1/12), cls.menu, slice=True, text='BACK'), # TODO: 变成刷新键（那么就要固定到一个合适的位置了，如左下角，OK和箭头放在一边
                ui.Button(cls.images['button']['square_color'], pygame.Rect(ui.W * 7/16, ui.H * 5/8, ui.W * 1/8, ui.H * 1/12), access, slice=True, text='OK')
            ])
            if page < len(rooms):
                def next():
                    cls.search(rooms, page + 1)
                ui.buttons.extend([
                    ui.Button(cls.images['button']['arrow_right'], pygame.Rect(ui.W * 19/32, ui.H * 2/3 - 16, 32, 32), next)
                ])
            if page > 1:
                def prev():
                    cls.search(rooms, page - 1)
                ui.buttons.extend([
                    ui.Button(cls.images['button']['arrow_left'], pygame.Rect(ui.W * 13/32 - 32, ui.H * 2/3 - 16, 32, 32), prev)
                ])
        else:
            ui.clear()

            ui.columns.extend([
                ui.Column(
                    pygame.Rect(ui.W * 5/16, ui.H * 1/4, ui.W * 3/8, ui.H * 1/2),
                    tag='SEARCH',
                    contents=[
                        'EMPTY'
                    ]
                )
            ])

            ui.buttons.extend([
                ui.Button(cls.images['button']['square_line'], pygame.Rect(ui.W * 7/16, ui.H * 5/8, ui.W * 1/8, ui.H * 1/12), cls.menu, slice=True, text='BACK')
            ])

    @classmethod
    def room(cls):
        ui.clear()

        ui.columns.extend([
            ui.Column(pygame.Rect(ui.W * 5/16, ui.H * 1/6, ui.W * 3/8, ui.H * 2/3), tag=cls.client.room.name, contents=cls.client.room.players)
        ])

    @classmethod
    def game(cls):
        pass

    @classmethod
    def run(cls):
        cls.menu()

        while ui.update():
            for action in cls.actions:
                action()

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