import pygame


def scale(image: pygame.Surface, width: int, height: int, corner: int = 16) -> pygame.Surface:
    if width < 2 * corner or height < 2 * corner:
        raise ValueError('size out of range')
    if image.get_width() < 2 * corner or image.get_height() < 2 * corner:
        raise ValueError('corner too large')

    w, h = image.get_size()
    slices = {
        'topleft': image.subsurface((0, 0, corner, corner)),
        'top': image.subsurface((corner, 0, w - 2 * corner, corner)),
        'topright': image.subsurface((w - corner, 0, corner, corner)),
        'left': image.subsurface((0, corner, corner, h - 2 * corner)),
        'center': image.subsurface((corner, corner, w - 2 * corner, h - 2 * corner)),
        'right': image.subsurface((w - corner, corner, corner, h - 2 * corner)),
        'bottomleft': image.subsurface((0, h - corner, corner, corner)),
        'bottom': image.subsurface((corner, h - corner, w - 2 * corner, corner)),
        'bottomright': image.subsurface((w - corner, h - corner, corner, corner))
    }

    target = pygame.Surface((width, height), flags=pygame.SRCALPHA)    # flags=pygame.SCHALPHA?
    target.blit(slices['topleft'], (0, 0))
    target.blit(pygame.transform.scale(slices['top'], (width - 2 * corner, corner)), (corner, 0))
    target.blit(slices['topright'], (width - corner, 0))
    target.blit(pygame.transform.scale(slices['left'], (corner, height - 2 * corner)), (0, corner))
    target.blit(pygame.transform.scale(slices['center'], (width - 2 * corner, height - 2 * corner)), (corner, corner))
    target.blit(pygame.transform.scale(slices['right'], (corner, height - 2 * corner)), (width - corner, corner))
    target.blit(slices['bottomleft'], (0, height - corner))
    target.blit(pygame.transform.scale(slices['bottom'], (width - 2 * corner, corner)), (corner, height - corner))
    target.blit(slices['bottomright'], (width - corner, height - corner))
    return target