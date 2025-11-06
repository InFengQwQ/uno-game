from . import TEXT_COLOR, HINT_COLOR, scale
import pygame


class Input(pygame.Surface):    # TODO: 输入事件类型？

    inputs: list['Input'] = []

    inactive_image: pygame.Surface
    active_image: pygame.Surface
    hint_font: pygame.font.Font
    tap_sound: pygame.mixer.Sound

    def __init__(self, rect: pygame.Rect, hint: str = ''):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.inactive_surface = scale(Input.inactive_image, rect.size)
        self.active_surface = scale(Input.active_image, rect.size)
        self.text_area = self.subsurface((8, 8), (rect.w - 16, rect.h - 16))
        self.mask = pygame.mask.from_surface(self.inactive_surface)

        self.rect = rect
        self.hint = hint

        self.is_activated = False
        self.text = ''

    @property
    def is_hovered(self):
        mx, my = pygame.mouse.get_pos()
        x, y = self.rect.topleft
        pos = mx - x, my - y
        return self.rect.collidepoint(mx, my) and self.mask.get_at(pos)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.is_activated = True
                Input.tap_sound.play()
            else:
                self.is_activated = False

        if self.is_activated:
            if event.type == pygame.TEXTINPUT:
                self.text += event.text
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1] if self.text else ''
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.is_activated = False
            self.blit(self.active_surface, (0, 0))
        else:
            self.blit(self.inactive_surface, (0, 0))

        if self.text:
            font = pygame.font.SysFont(None, self.text_area.get_rect().h)
            text_surface = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(midright=self.text_area.get_rect().midright)
            self.text_area.blit(text_surface, text_rect)
        else:
            if self.hint:
                hint_surface = Input.hint_font.render(self.hint, True, HINT_COLOR)
                hint_rect = hint_surface.get_rect(center=self.text_area.get_rect().center)
                self.text_area.blit(hint_surface, hint_rect)

    @classmethod
    def update_all(cls, event: pygame.event.Event):
        for input in cls.inputs.copy():
            input.update(event)