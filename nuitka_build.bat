python -m nuitka ^
  --standalone ^
  --onefile ^
  --windows-console-mode=disable ^
  --follow-imports ^
  --show-progress ^
  --output-dir=build ^
  --remove-output ^
  --windows-icon-from-ico=icon.ico ^
  --include-data-dir=./assets=assets ^
  main.py