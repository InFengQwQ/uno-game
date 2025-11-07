python -m nuitka ^
  --windows-console-mode="attach" ^
  --standalone ^
  --onefile ^
  --remove-output ^
  --main="main.py" ^
  --include-data-dir="assets"="assets" ^
  --windows-icon-from-ico="icon.ico" ^
  --follow-imports