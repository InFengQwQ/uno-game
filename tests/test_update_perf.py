import os
import time

# Run pygame headless for CI / test environments
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

pygame.init()
pygame.font.init()

# Ensure project root is on sys.path so `import ui` works when running tests directly
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


class DummySound:
    def play(self):
        return None


from ui.button import Button
from ui.input import Input
from ui.column import Column
from ui.message import Message


# Minimal initialization for UI classes
font = pygame.font.SysFont(None, 12)
# slice_scale expects images bigger than 2*cor (cor==8) so make a larger surface
surf = pygame.Surface((64, 64))
dummy_sound = DummySound()

Button.init(font, dummy_sound)
Input.init(surf, surf, font, dummy_sound)
Column.init(surf, surf, surf, font, font)
Message.init(surf, font)


def make_scene(N=200):
    Button.elements.clear()
    Input.elements.clear()
    Column.elements.clear()
    Message.elements.clear()

    # Use larger rect so slice_scale (9-slice) constraints are satisfied
    rect = pygame.Rect(0, 0, 128, 128)
    for i in range(N):
        Button.elements.append(Button(surf, rect, lambda: None))
        Input.elements.append(Input(rect, hint=''))
        Column.elements.append(Column(rect))
        Message.elements.append(Message(None))


def bench(N=200, M=10, iterations=20):
    make_scene(N)

    events = [pygame.event.Event(pygame.MOUSEMOTION) for _ in range(M)]

    t0 = time.perf_counter()
    for _ in range(iterations):
        # call each class update_all (this matches screen update order)
        Column.update_all(events)
        Input.update_all(events)
        Button.update_all(events)
        Message.update_all(events)
    t1 = time.perf_counter()
    return t1 - t0


def test_benchmark_print():
    # Small, medium and larger scenes
    for N in (50, 200, 800):
        elapsed = bench(N=N, M=20, iterations=10)
        print(f'Benchmark N={N:4d} elements, M=20 events, 10 iters -> {elapsed:.6f}s')

    # Always pass the test; this file is for measurement output only
    assert True


if __name__ == '__main__':
    test_benchmark_print()
