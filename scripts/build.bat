cd ..

pip install -r requirements.txt

pyinstaller launcher.py ^
  --name Uno ^
  --icon icon.ico ^
  --onefile ^
  --windowed ^
  --add-data "assets;assets" ^
  --clean

pause