uv run --with pyinstaller python -m PyInstaller "main.py" ^
  --onefile ^
  --windowed ^
  --add-data "assets;assets" ^
  --icon "icon.ico" ^
  --noconfirm
