#!/usr/bin/env bash
# video-clip-cut skill 一键安装 (macOS / Linux)
# 用法: bash install.sh
set -e

DEST="$HOME/.workbuddy/skills/video-clip-cut"
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "Installing video-clip-cut skill ..."
echo "  From: $SRC"
echo "  To  : $DEST"

mkdir -p "$DEST"
cp -R "$SRC"/. "$DEST"/

echo "[OK] Installed to $DEST"
echo "Restart WorkBuddy session to load the skill."
