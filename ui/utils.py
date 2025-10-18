import pygame

def scale(image: pygame.Surface, size: tuple[float, float], corner: float = 8) -> pygame.Surface:
    width, height = size
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

    target = pygame.Surface((width, height), flags=pygame.SRCALPHA)
    target.blit(slices['topleft'], (0, 0))
    target.blit(pygame.transform.smoothscale(slices['top'], (width - 2 * corner, corner)), (corner, 0))
    target.blit(slices['topright'], (width - corner, 0))
    target.blit(pygame.transform.smoothscale(slices['left'], (corner, height - 2 * corner)), (0, corner))
    target.blit(pygame.transform.smoothscale(slices['center'], (width - 2 * corner, height - 2 * corner)), (corner, corner))
    target.blit(pygame.transform.smoothscale(slices['right'], (corner, height - 2 * corner)), (width - corner, corner))
    target.blit(slices['bottomleft'], (0, height - corner))
    target.blit(pygame.transform.smoothscale(slices['bottom'], (width - 2 * corner, corner)), (corner, height - corner))
    target.blit(slices['bottomright'], (width - corner, height - corner))
    return target