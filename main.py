"""Main module for the UNO game application."""

from typing import Optional

import pygame

from config import (
    W, H, FPS,
    RUN_INTERVAL, ROOM_UPDATE_INTERVAL, ROOM_RECEIVE_INTERVAL,
    ROOM_CAPACITY,
)
from resources import ResourceManager
import ui
from ui import *
import multi
from multi import *
import uno
from uno import *

# 所有游戏内核在主机完成，所以大多数实例对象仅存在于主机
# 对于客户端的玩家的数据，主机仍留有备份，客户端拥有手牌的卡牌类（主机发送json标明卡牌属性），仅此而已
# 当然，客户端需要知道弃牌堆顶的牌，并通过rule判断自己可以打出什么，主机也应该脱离内核实现同样的架构
# 而且对于摸牌和质疑等操作还需要单独发送数据到交互对象而非全局
# 而对于其他操作应该不发送给操作者

# Initialize resource manager
resources = ResourceManager()

# Initialize UI components
Column.init(
    back_image=resources.images['column']['back'],
    front_image=resources.images['column']['front'],
    divider_image=resources.images['column']['divider'],
    tag_font=resources.fonts['tag'],
    content_font=resources.fonts['content']
)
Input.init(
    inactive_image=resources.images['input']['inactive'],
    active_image=resources.images['input']['active'],
    hint_font=resources.fonts['hint'],
    tap_sound=resources.sounds['tap']
)
Button.init(
    text_font=resources.fonts['text'],
    click_sound=resources.sounds['click']
)
Message.init(
    message_image=resources.images['message']['box'],
    message_font=resources.fonts['message']
)


class UnoGame:
    """Main game class managing the UNO game flow."""

    role: Optional[Host | Client] = None
    uno_game: Optional[Game] = None

    @classmethod
    def menu(cls):
        """Display the main menu screen."""

        ui.clear()

        ui.scene.blit(pygame.transform.scale(
            resources.images['info']['cards_text'], (64, 64)), (10, 10)
        )
        ui.scene.blit(pygame.transform.scale(
            resources.images['info']['players_2_10'], (64, 64)), (84, 10)
        )

        Column.elements.extend([
            Column(
                pygame.Rect(W * 3/8, H * 1/4, W * 1/4, H * 1/2),
                tag="Menu"
            )
        ])

        Button.elements.extend([
            Button(
                resources.images['button']['square_color'],
                pygame.Rect(W * 13/32, H * 3/8, W * 3/16, H * 1/12),
                cls.create, slice=True, text="Create"
            ),
            Button(
                resources.images['button']['square_basic'],
                pygame.Rect(W * 13/32, H * 1/2, W * 3/16, H * 1/12),
                cls.join, slice=True, text="Join"
            ),
            Button(
                resources.images['button']['square_basic'],
                pygame.Rect(W * 13/32, H * 5/8, W * 3/16, H * 1/12),
                lambda: None, slice=True, text="Options"
            )
        ])

    @classmethod
    def join(cls, page: int = 1):
        """
        Display the room join screen.

        Args:
            page: Page number for room listing (default: 1)
        """

        if Room.rooms:
            page = min(page, len(Room.rooms))
            info = sorted(Room.rooms.values())[page - 1]

            ui.clear()

            Column.elements.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    tag=f"Search({page}/{len(Room.rooms)})",
                    contents=[
                        f"{info.name}({len(info.players)}/{ROOM_CAPACITY})",
                        f"{info.ip}:{info.port}",
                        ''
                    ]
                )
            ])

            Input.elements.extend([
                name := Input(
                    pygame.Rect(W * 11/32, H * 7/16, W * 1/8, H * 1/12),
                    hint="Name"
                ),
                password := Input(
                    pygame.Rect(W * 1/2, H * 7/16, W * 5/32, H * 1/12),
                    hint="Password"
                )
            ])

            @Message.catch
            def access():
                if not password.text.isdigit():
                    raise ValueError("Password should be a number")
                client = Client(name.text)
                client.join(info, int(password.text))
                cls.role = client
                cls.room()
            Button.elements.extend([
                Button(
                    resources.images['button']['square_color'],
                    pygame.Rect(W * 11/32, H * 9/16, W * 1/8, H * 1/12),
                    access, slice=True, text="OK"
                ),
                Button(
                    resources.images['button']['square_line'],
                    pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12),
                    cls.menu, slice=True, text="Back"
                ),
                Button(
                    resources.images['button']['square_basic'],
                    pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12),
                    cls.join, slice=True, text="Refresh"
                )
            ])
            if page < len(Room.rooms):
                def next():
                    cls.join(page + 1)
                Button.elements.extend([
                    Button(
                        resources.images['button']['arrow_right'],
                        pygame.Rect(W * 19/32, H * 29/48 - 16, 32, 32),
                        next
                    )
                ])
            if page > 1:
                def prev():
                    cls.join(page - 1)
                Button.elements.extend([
                    Button(
                        resources.images['button']['arrow_left'],
                        pygame.Rect(W * 9/16 - 32, H * 29/48 - 16, 32, 32),
                        prev
                    )
                ])
        else:
            ui.clear()

            Column.elements.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    tag="Search",
                    contents=[
                        "Empty"
                    ]
                )
            ])

            Button.elements.extend([
                Button(
                    resources.images['button']['square_line'],
                    pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12),
                    cls.menu, slice=True, text="Back"
                ),
                Button(
                    resources.images['button']['square_basic'],
                    pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12),
                    cls.join, slice=True, text="Refresh"
                )
            ])

    @classmethod
    def create(cls):
        """Display the room creation screen."""

        ui.clear()

        Column.elements.extend([
            Column(
                pygame.Rect(W * 5/16, H * 1/4, W * 3/8, H * 1/2),
                tag="Create",
                contents=[
                    "Create a room with name",
                    "and your player name.",
                    ''
                ]
            )
        ])

        Input.elements.extend([
            name := Input(
                pygame.Rect(W * 29/64, H * 1/2, W * 3/32, H * 1/12),
                hint="Name"
            ),
            room_name := Input(
                pygame.Rect(W * 9/16, H * 1/2, W * 3/32, H * 1/12),
                hint="Room"
            ),
            password := Input(
                pygame.Rect(W * 11/32, H * 5/8, W * 5/32, H * 1/12),
                hint="Password"
            )
        ])

        @Message.catch
        def host():
            if not password.text.isdigit():
                raise ValueError("Password should be a number")
            cls.role = Host(name.text, room_name.text, int(password.text))
            cls.room()
        Button.elements.extend([
            Button(
                resources.images['button']['square_line'],
                pygame.Rect(W * 11/32, H * 1/2, W * 3/32, H * 1/12),
                cls.menu, slice=True, text='Back'
            ),
            Button(
                resources.images['button']['square_color'],
                pygame.Rect(W * 17/32, H * 5/8, W * 1/8, H * 1/12),
                host, slice=True, text="OK"
            )
        ])

    @classmethod
    def room(cls):
        """Display the room waiting screen."""

        assert cls.role and cls.role.room

        ui.clear()

        Column.elements.extend([
            Column(
                pygame.Rect(W * 5/16, H * 1/8, W * 3/8, H * 3/4),
                tag=cls.role.room.name,
                contents=cls.role.room.players
            )
        ])

        def back():
            assert cls.role

            try:
                cls.role.close()
            except SocketClosedMessage:
                cls.role = None
                cls.menu()
        Button.elements.extend([
            Button(
                resources.images['button']['square_line'],
                pygame.Rect(W * 11/32, H * 3/4, W * 1/8, H * 1/12),
                back, slice=True, text="Back"
            )
        ])

        if isinstance(cls.role, Host):
            def start():
                assert cls.role and cls.role.room

                cls.role.room.status = ROOM_ONGOING
                cls.game()
            Button.elements.extend([
                Button(
                    resources.images['button']['square_color'],
                    pygame.Rect(W * 17/32, H * 3/4, W * 1/8, H * 1/12),
                    start, slice=True, text="Start"
                )
            ])

    @classmethod
    def game(cls):
        """
        Initialize and display the game screen.

        TODO: Initialize game logic here
        """

        assert cls.role and cls.role.room

        cls.uno_game = Game([Player(name) for name in cls.role.room.players])
        # 看一下下面的实现，搞清楚每一回合该如何处理交互

        ui.clear()

    @classmethod
    def run(cls):
        """Run the game main loop."""

        cls.menu()
        counter = ui.update()

        def check_interval(i: float) -> bool:
            return not int(counter % (FPS * i))

        @Message.catch
        def network():
            assert cls.role

            try:
                cls.role.run()
            except SocketClosedMessage as e:
                cls.role = None
                cls.menu()
                Message.elements.append(Message(e))
            except GameStartedMessage:
                cls.game()
            except GameEndedMessage:
                cls.room()

        while counter := ui.update(counter):
            if check_interval(RUN_INTERVAL):
                if cls.role:
                    network()
            if check_interval(ROOM_UPDATE_INTERVAL):
                Room.update()
            if check_interval(ROOM_RECEIVE_INTERVAL):
                Room.receive()


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
