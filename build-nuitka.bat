uv run --with "nuitka[onefile]" python -m nuitka ^
  --onefile ^
  --remove-output ^
  --windows-console-mode="disable" ^
  --main="main.py" ^
  --include-data-dir="assets"="assets" ^
  --windows-icon-from-ico="icon.ico"
