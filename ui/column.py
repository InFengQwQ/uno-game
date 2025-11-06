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

        self.back_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.front_surface = pygame.Surface((rect.w, rect.h - head), pygame.SRCALPHA)

        self.rect = rect
        self.head = head
        self.tag = tag
        self.contents = contents

    def update(self):
        self.back_surface.blit(scale(Column.back_image, self.back_surface.get_size()), (0, 0))
        if self.tag:
            tag_surface = Column.tag_font.render(self.tag, True, TEXT_COLOR)
            tag_rect = tag_surface.get_rect(center=self.get_rect(top=self.head // 2).midtop)
            self.back_surface.blit(tag_surface, tag_rect)
        self.blit(self.back_surface, (0, 0))

        self.front_surface.blit(scale(Column.front_image, self.front_surface.get_size()), (0, 0))
        if self.contents:
            for line, content in enumerate(self.contents):
                if content:
                    content_surface = Column.content_font.render(content, True, TEXT_COLOR)
                    content_rect = content_surface.get_rect(topleft=(16, 16 + line * H // 20))
                    self.front_surface.blit(content_surface, content_rect)
                else:
                    divider_surface = pygame.transform.scale(Column.divider_image, (self.rect.w - 32, 4))
                    divider_rect = divider_surface.get_rect(topleft=(16, 18 + line * H // 20))
                    self.front_surface.blit(divider_surface, divider_rect)
        self.blit(self.front_surface, (0, self.head))

    @classmethod
    def update_all(cls):
        for column in cls.columns.copy():
            column.update()