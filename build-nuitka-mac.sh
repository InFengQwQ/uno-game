#!/bin/sh
set -e
cd "$(dirname "$0")"

uv run --with "nuitka[onefile]" python -m nuitka \
  --onefile \
  --remove-output \
  --output-dir=dist \
  --main="main.py" \
  --include-data-dir="assets"="assets"

APP="dist/main.app"
mkdir -p "$APP/Contents/MacOS"
mv "dist/main.bin" "$APP/Contents/MacOS/main"
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>main</string>
<key>CFBundleIdentifier</key><string>com.example.uno</string>
<key>CFBundleName</key><string>UNO</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
EOF
