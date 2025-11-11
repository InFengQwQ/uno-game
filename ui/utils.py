import pygame

def slice_scale(
    image: pygame.Surface,
    size: tuple[float, float],
    cor: int = 8
) -> pygame.Surface:
    """Scale 9-slice images

    preserve corners,
    stretch edges and center to fit target size.
    """
    w, h = image.get_size()
    trgw, trgh = size
    assert all(map(lambda x: x > 2 * cor, (w, h, trgw, trgh)))

    # Slice image into 9 parts
    slices = {
        'topleft': image.subsurface(
            pygame.Rect(0, 0, cor, cor)
        ),
        'top': image.subsurface(
            pygame.Rect(cor, 0, w - 2 * cor, cor)
        ),
        'topright': image.subsurface(
            pygame.Rect(w - cor, 0, cor, cor)
        ),
        'left': image.subsurface(
            pygame.Rect(0, cor, cor, h - 2 * cor)
        ),
        'center': image.subsurface(
            pygame.Rect(cor, cor, w - 2 * cor, h - 2 * cor)
        ),
        'right': image.subsurface(
            pygame.Rect(w - cor, cor, cor, h - 2 * cor)
        ),
        'bottomleft': image.subsurface(
            pygame.Rect(0, h - cor, cor, cor)
        ),
        'bottom': image.subsurface(
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
        pygame.transform.smoothscale(
            slices['top'], (trgw - 2 * cor, cor)
        ),
        (cor, 0)
    )
    target.blit(
        pygame.transform.smoothscale(
            slices['left'], (cor, trgh - 2 * cor)
        ),
        (0, cor)
    )
    target.blit(
        pygame.transform.smoothscale(
            slices['right'], (cor, trgh - 2 * cor)
        ),
        (trgw - cor, cor)
    )
    target.blit(
        pygame.transform.smoothscale(
            slices['bottom'], (trgw - 2 * cor, cor)
        ),
        (cor, trgh - cor)
    )

    target.blit(
        pygame.transform.smoothscale(
            slices['center'], (trgw - 2 * cor, trgh - 2 * cor)
        ),
        (cor, cor)
    )

    return target