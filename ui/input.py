from . import TEXT_COLOR, HINT_COLOR, scale
import pygame


class Input(pygame.Surface):    # TODO: 输入事件类型？
    inactive_image: pygame.Surface
    active_image: pygame.Surface
    hint_font: pygame.font.Font
    tap_sound: pygame.mixer.Sound

    def __init__(self, rect: pygame.Rect, hint: str = ''):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.inactive = scale(Input.inactive_image, rect.size)
        self.active = scale(Input.active_image, rect.size)
        self.area = self.subsurface((8, 8), (rect.w - 16, rect.h - 16))

        self.rect = rect
        self.mask = pygame.mask.from_surface(self.inactive)
        self.hint = hint
        self.activated = False
        self.text = ''

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                Input.tap_sound.play()
                self.activated = True
            else:
                self.activated = False

        if self.activated:
            if event.type == pygame.TEXTINPUT:
                self.text += event.text
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and self.text:  # TODO
                self.text = self.text[:-1]
            self.blit(self.active, (0, 0))
        else:
            self.blit(self.inactive, (0, 0))

        if self.text:
            font = pygame.font.SysFont(None, self.area.get_rect().h)
            text_surface = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(midright=self.area.get_rect().midright)
            self.area.blit(text_surface, text_rect)
        else:
            if self.hint:
                hint_surface = Input.hint_font.render(self.hint, True, HINT_COLOR)
                hint_rect = hint_surface.get_rect(center=self.area.get_rect().center)
                self.area.blit(hint_surface, hint_rect)


inputs: list[Input] = []