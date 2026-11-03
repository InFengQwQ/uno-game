from functools import wraps
from typing import Optional, Callable

import pygame

from config import (
    W, H,
    FPS,
    RUN_INTERVAL, ROOM_RECV_INTERVAL,
    ROOM_CAPACITY
)
from resources import ResourceManager
from ui import (
    Column, Input, Button, Message,
    Stage,
    scene,
    clear, update
)
from multi import (
    ActionType,
    SocketClosedMessage, GameBeginMessage, GameEndedMessage,
    Room, Client, Host
)


# Initialize resource manager
resources = ResourceManager()

# Initialize
Column.init(
    tag_font=resources.fonts['tag'],
    content_font=resources.fonts['content'],
    back_image=resources.images['column']['back'],
    face_image=resources.images['column']['face'],
    divider_image=resources.images['column']['divider']
)
Input.init(
    hint_font=resources.fonts['hint'],
    active_image=resources.images['input']['active'],
    normal_image=resources.images['input']['normal'],
    tap_sound=resources.sounds['tap']
)
Button.init(
    text_font=resources.fonts['text'],
    click_sound=resources.sounds['click']
)
Message.init(
    message_font=resources.fonts['message'],
    box_image=resources.images['message']['box']
)
Stage.init(
    name_font=resources.fonts['name'],
    size_font=resources.fonts['size'],
    card_images=resources.images['cards']
)


class UnoGame:
    """Main game class."""
    role: Optional[Host | Client] = None

    @classmethod
    def display_menu(cls):
        """Display the main menu screen."""
        clear()

        scene.blit(pygame.transform.scale(
            resources.images['info']['cards_text'],
            (64, 64)), (10, 10)
        )
        scene.blit(pygame.transform.scale(
            resources.images['info']['players_2_10'],
            (64, 64)), (84, 10)
        )

        Column.elements.extend([
            Column(
                pygame.Rect(W * 3/8, H * 1/4, W * 1/4, H * 1/2),
                "Menu"
            )
        ])

        Button.elements.extend([
            Button(
                pygame.Rect(W * 13/32, H * 3/8, W * 3/16, H * 1/12),
                resources.images['button']['square_color'],
                cls.display_create, slice=True, text=lambda: "Create"
            ),
            Button(
                pygame.Rect(W * 13/32, H * 1/2, W * 3/16, H * 1/12),
                resources.images['button']['square_basic'],
                cls.display_join, slice=True, text=lambda: "Join"
            ),
            Button(
                pygame.Rect(W * 13/32, H * 5/8, W * 3/16, H * 1/12),
                resources.images['button']['square_basic'],
                lambda: None, slice=True, text=lambda: "Options"
            )
        ])

    @classmethod
    def display_join(cls, page: int = 1):
        """Display the room join screen.

        Args:
            page: Page number for room listing.
        """
        if rooms := Room.rooms:
            page = min(page, len(rooms))
            ip, port = addr = sorted(rooms)[page-1]
            info = rooms[addr]

            clear()

            Column.elements.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    f"Search({page}/{len(rooms)})",
                    contents=[
                        f"{info.name}({len(info.players)}/{ROOM_CAPACITY})",
                        f"{ip}:{port}",
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
            def join():
                if not password.text.isdigit():
                    Message.elements.append(Message(
                        ValueError("Password should be a number")
                        # TODO
                    ))
                    return
                client = Client(name.text)
                client.join(addr, int(password.text))
                cls.role = client
                cls.display_room()
            Button.elements.extend([
                Button(
                    pygame.Rect(W * 11/32, H * 9/16, W * 1/8, H * 1/12),
                    resources.images['button']['square_color'],
                    join, slice=True, text=lambda: "OK"
                ),
                Button(
                    pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12),
                    resources.images['button']['square_line'],
                    cls.display_menu, slice=True, text=lambda: "Back"
                ),
                Button(
                    pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12),
                    resources.images['button']['square_basic'],
                    cls.display_join, slice=True, text=lambda: "Refresh"
                )
            ])
            if page < len(rooms):
                def next_page():
                    cls.display_join(page + 1)
                Button.elements.append(Button(
                    pygame.Rect(W * 19/32, H * 29/48 - 16, 32, 32),
                    resources.images['button']['arrow_right'],
                    next_page
                ))
            if page > 1:
                def prev_page():
                    cls.display_join(page - 1)
                Button.elements.append(Button(
                    pygame.Rect(W * 9/16 - 32, H * 29/48 - 16, 32, 32),
                    resources.images['button']['arrow_left'],
                    prev_page
                ))
        else:
            clear()

            Column.elements.extend([
                Column(
                    pygame.Rect(W * 5/16, H * 3/16, W * 3/8, H * 5/8),
                    "Search",
                    contents=[
                        "Empty"
                    ]
                )
            ])

            Button.elements.extend([
                Button(
                    pygame.Rect(W * 11/32, H * 11/16, W * 1/8, H * 1/12),
                    resources.images['button']['square_line'],
                    cls.display_menu, slice=True, text=lambda: "Back"
                ),
                Button(
                    pygame.Rect(W * 1/2, H * 11/16, W * 5/32, H * 1/12),
                    resources.images['button']['square_basic'],
                    cls.display_join, slice=True, text=lambda: "Refresh"
                )
            ])

    @classmethod
    def display_create(cls):
        """Display the room creation screen."""
        clear()

        Column.elements.extend([
            Column(
                pygame.Rect(W * 5/16, H * 1/4, W * 3/8, H * 1/2),
                "Create",
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
        def create():
            if not password.text.isdigit():
                Message.elements.append(Message(
                    ValueError("Password should be a number")
                    # TODO
                ))
                return
            cls.role = Host(name.text, room_name.text, int(password.text))
            cls.display_room()
        Button.elements.extend([
            Button(
                pygame.Rect(W * 11/32, H * 1/2, W * 3/32, H * 1/12),
                resources.images['button']['square_line'],
                cls.display_menu, slice=True, text=lambda: 'Back'
            ),
            Button(
                pygame.Rect(W * 17/32, H * 5/8, W * 1/8, H * 1/12),
                resources.images['button']['square_color'],
                create, slice=True, text=lambda: "OK"
            )
        ])

    @classmethod
    def display_room(cls):
        """Display the room waiting screen."""
        assert (role := cls.role)
        assert (room := cls.role.room)

        clear()

        Column.elements.extend([
            Column(
                pygame.Rect(W * 5/16, H * 1/8, W * 3/8, H * 3/4),
                f'"{room.name}"',
                contents=room.players
            )
        ])

        def back():
            try:
                role.close(Exception("Go to menu"))
            except SocketClosedMessage:
                cls.role = None
                cls.display_menu()
        Button.elements.extend([
            Button(
                pygame.Rect(W * 11/32, H * 3/4, W * 1/8, H * 1/12),
                resources.images['button']['square_line'],
                back, slice=True, text=lambda: "Back"
            )
        ])

        if isinstance(role, Host):
            def start():
                role.start()
                role.sync()
                cls.display_game()
            Button.elements.extend([
                Button(
                    pygame.Rect(W * 17/32, H * 3/4, W * 1/8, H * 1/12),
                    resources.images['button']['square_color'],
                    start, slice=True, text=lambda: "Start"
                )
            ])

    @classmethod
    def display_game(cls, pick: int = 1):
        """Display the game screen."""
        assert (role := cls.role)
        # assert (room := cls.role.room)

        assert (mirror := role.mirror)

        clear()

        def clamped_exec(func: Callable[..., None]) -> Callable[..., None]:
            @wraps(func)
            def wrapper():
                nonlocal pick
                pick = max(min(pick, len(mirror.hand)), 1)
                return func()

            return wrapper

        Stage.elements.append(Stage(
            mirror.players,
            mirror.player,
            mirror.hand,
            mirror.top,
            pick-1,
        ))

        @Message.catch
        @clamped_exec
        def draw():
            role.action(ActionType.DRAW)
        @Message.catch
        @clamped_exec
        def play():
            card = mirror.hand[pick-1]
            @Message.catch
            def send_action(color: Optional[str] = None):
                card_info = card.to_dict()|(
                    {
                        'color': color
                    } if color else {}
                )
                role.action(ActionType.PLAY,
                    card=card_info,
                    uno=False   # TODO
                )

                cls.display_game(pick)
            if card.is_pending:
                cls.display_game(pick)

                Stage.Selector(
                    pygame.Rect(W * 2/9, H * 3/8, W * 5/9, H * 1/4),
                    send_action,
                )
            else:
                send_action()
        Button.elements.extend([
            Button(
                pygame.Rect(W * 21/64, H * 7/8, W * 5/32, H * 1/12),
                resources.images['button']['square_basic'],
                draw, slice=True, text=(
                    lambda: "Pass" if mirror.to_draw < 0 else "Draw"
                )
            ),
            Button(
                pygame.Rect(W * 33/64, H * 7/8, W * 5/32, H * 1/12),
                resources.images['button']['square_color'],
                play, slice=True, text=lambda: "Play"
            )
        ])

        @clamped_exec
        def next_card():
            cls.display_game(pick + 1)
        Button.elements.append(Button(
            pygame.Rect(W * 23/32, H * 11/12 - 16, 32, 32),
            resources.images['button']['arrow_right'],
            next_card
        ))
        @clamped_exec
        def prev_card():
            cls.display_game(pick - 1)
        Button.elements.append(Button(
            pygame.Rect(W * 9/32 - 32, H * 11/12 - 16, 32, 32),
            resources.images['button']['arrow_left'],
            prev_card
        ))

    @classmethod
    def run(cls):
        """Run the main loop."""
        cls.display_menu()

        def check_interval(i: float) -> bool:
            return not int(counter % (FPS * i))

        @Message.catch
        def network():
            assert (role := cls.role)

            try:
                role.run()
            except SocketClosedMessage as e:
                cls.role = None

                Message.elements.append(Message(e))
                cls.display_menu()
            except GameBeginMessage:
                cls.display_game()
            except GameEndedMessage:
                cls.display_room()

        counter = 0
        while counter := update(counter):
            if check_interval(RUN_INTERVAL) and cls.role:
                network()
            if check_interval(ROOM_RECV_INTERVAL):
                Room.recv()


if __name__ == '__main__':
    UnoGame.run()
