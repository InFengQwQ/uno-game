from . import H, TEXT_COLOR, scale
import pygame


class Column(pygame.Surface):
    columns: list['Column'] = []

    back_image: pygame.Surface
    front_image: pygame.Surface
    divider_image: pygame.Surface
    tag_font: pygame.font.Font
    content_font: pygame.font.Font

    def __init__(self, rect: pygame.Rect, head: int = 48, tag: str = '', contents: list[str] = []):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.back = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.front = pygame.Surface((rect.w, rect.h - head), pygame.SRCALPHA)
        self.rect = rect
        self.tag = tag
        self.contents = contents

    def update(self):
        head = self.back.get_height() - self.front.get_height()

        self.back.blit(scale(Column.back_image, self.back.get_size()), (0, 0))
        if self.tag:
            tag_surface = Column.tag_font.render(self.tag, True, TEXT_COLOR)
            tag_rect = tag_surface.get_rect(center=self.get_rect(top=head // 2).midtop)
            self.back.blit(tag_surface, tag_rect)
        self.blit(self.back, (0, 0))

        self.front.blit(scale(Column.front_image, self.front.get_size()), (0, 0))
        if self.contents:
            for line, content in enumerate(self.contents):
                if content:
                    content_surface = Column.content_font.render(content, True, TEXT_COLOR)
                    content_rect = content_surface.get_rect(topleft=(16, 16 + line * H // 20))
                    self.front.blit(content_surface, content_rect)
                else:
                    divider_surface = pygame.transform.scale(Column.divider_image, (self.rect.w - 32, 4))
                    divider_rect = divider_surface.get_rect(center=(self.rect.w // 2, 20 + line * H // 20))
                    self.front.blit(divider_surface, divider_rect)
        self.blit(self.front, (0, head))

    @classmethod
    def update_all(cls):
        for column in cls.columns.copy():
            column.update()