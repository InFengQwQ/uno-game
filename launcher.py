import sys
import os

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)  # type: ignore

from main import UnoGame

if __name__ == '__main__':
    UnoGame.run()