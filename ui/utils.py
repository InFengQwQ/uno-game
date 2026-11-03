import pygame

__all__ = ['slice_scale']


def slice_scale(image: pygame.Surface,
    size: tuple[float, float],
    cor: int = 8
) -> pygame.Surface:
    """Scale 9-slice images.

    Preserve corners,
    stretch edges and center to fit target size.
    """
    w, h = image.get_size()
    trgw, trgh = size
    assert all(map(lambda x: x > 2 * cor, (w, h, trgw, trgh)))

    slices = {
        'topleft': image.subsurface(
            pygame.Rect(0, 0, cor, cor)
        ),
        'midtop': image.subsurface(
            pygame.Rect(cor, 0, w - 2 * cor, cor)
        ),
        'topright': image.subsurface(
            pygame.Rect(w - cor, 0, cor, cor)
        ),
        'midleft': image.subsurface(
            pygame.Rect(0, cor, cor, h - 2 * cor)
        ),
        'center': image.subsurface(
            pygame.Rect(cor, cor, w - 2 * cor, h - 2 * cor)
        ),
        'midright': image.subsurface(
            pygame.Rect(w - cor, cor, cor, h - 2 * cor)
        ),
        'bottomleft': image.subsurface(
            pygame.Rect(0, h - cor, cor, cor)
        ),
        'midbottom': image.subsurface(
            pygame.Rect(cor, h - cor, w - 2 * cor, cor)
        ),
        'bottomright': image.subsurface(
            pygame.Rect(w - cor, h - cor, cor, cor)
        )
    }

    # Create target surface by corners, edges and center
    target = pygame.Surface(size, flags=pygame.SRCALPHA)

    target.blit(slices['topleft'], (0, 0))
    target.blit(slices['topright'], (trgw - cor, 0))
    target.blit(slices['bottomleft'], (0, trgh - cor))
    target.blit(slices['bottomright'], (trgw - cor, trgh - cor))

    target.blit(
        pygame.transform.scale(
            slices['midtop'], (trgw - 2 * cor, cor)
        ),
        (cor, 0)
    )
    target.blit(
        pygame.transform.scale(
            slices['midleft'], (cor, trgh - 2 * cor)
        ),
        (0, cor)
    )
    target.blit(
        pygame.transform.scale(
            slices['midright'], (cor, trgh - 2 * cor)
        ),
        (trgw - cor, cor)
    )
    target.blit(
        pygame.transform.scale(
            slices['midbottom'], (trgw - 2 * cor, cor)
        ),
        (cor, trgh - cor)
    )

    target.blit(
        pygame.transform.scale(
            slices['center'], (trgw - 2 * cor, trgh - 2 * cor)
        ),
        (cor, cor)
    )

    return target
