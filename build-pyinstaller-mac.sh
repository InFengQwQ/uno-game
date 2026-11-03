#!/bin/sh
set -e
cd "$(dirname "$0")"

uv run --with pyinstaller --with pillow python -m PyInstaller main.py \
  --onedir \
  --windowed \
  --add-data "assets:assets" \
  --icon "icon.ico" \
  --noconfirm
