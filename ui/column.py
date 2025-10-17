from . import H, TEXT_COLOR, scale
import pygame


class Column(pygame.Surface):
    back_image: pygame.Surface
    front_image: pygame.Surface
    divider_image: pygame.Surface
    tag_font: pygame.font.Font
    content_font: pygame.font.Font
    def __init__(self, rect: pygame.Rect, head: float = 48, tag: str = '', contents: list[str] = []):
        super().__init__(rect.size, pygame.SRCALPHA)

        self.back = scale(Column.back_image, rect.size)
        self.front = scale(Column.front_image, (rect.w, rect.h - head))
        self.rect = rect
        self.tag = tag
        self.contents = contents

        self.update()

    def update(self):
        head = self.back.get_height() - self.front.get_height()

        if self.tag:
            tag_surface = Column.tag_font.render(self.tag, True, TEXT_COLOR)
            tag_rect = tag_surface.get_rect(center=self.get_rect(top=head / 2).midtop)
            self.back.blit(tag_surface, tag_rect)
        self.blit(self.back, (0, 0))

        if self.contents:
            for line, content in enumerate(self.contents):
                if content:
                    content_surface = Column.content_font.render(content, True, TEXT_COLOR)
                    content_rect = content_surface.get_rect(topleft=(16, 16 + H * 1/20 * line))
                    self.front.blit(content_surface, content_rect)
                else:
                    divider_surface = pygame.transform.scale(Column.divider_image, (self.rect.w - 32, 4))
                    divider_rect = divider_surface.get_rect(center=(self.rect.w * 1/2, 20 + H * 1/20 * line))
                    self.front.blit(divider_surface, divider_rect)
        self.blit(self.front, (0, head))