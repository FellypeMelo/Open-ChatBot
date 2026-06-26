#!/bin/bash
# install.sh
# Script to install the plantuml-generator skill in Antigravity/Gemini (Global or Local)

set -e

SKILL_NAME="plantuml-generator"
GLOBAL_PATH="$HOME/.gemini/config/skills/$SKILL_NAME"
LOCAL_PATH=".agents/skills/$SKILL_NAME"

echo "Where would you like to install the '$SKILL_NAME' skill?"
echo "1) Globally (available to all projects at: $GLOBAL_PATH)"
echo "2) Locally (available only to this project at: $LOCAL_PATH)"
read -p "Select Option [1 or 2, default: 1]: " choice

if [ "$choice" = "2" ]; then
    TARGET="$LOCAL_PATH"
else
    TARGET="$GLOBAL_PATH"
fi

# Ensure parent directory exists
TARGET_DIR=$(eval echo "$TARGET")
mkdir -p "$(dirname "$TARGET_DIR")"

# Remove existing installation
if [ -d "$TARGET_DIR" ]; then
    echo "Target directory already exists. Overwriting old installation..."
    rm -rf "$TARGET_DIR"
fi

mkdir -p "$TARGET_DIR"

# Copy files excluding git assets and install scripts
if command -v rsync >/dev/null 2>&1; then
    rsync -av --exclude='.git' --exclude='.github' --exclude='install.ps1' --exclude='install.sh' ./ "$TARGET_DIR/"
else
    cp -r ./ "$TARGET_DIR/"
    rm -rf "$TARGET_DIR/.git" "$TARGET_DIR/.github" "$TARGET_DIR/install.ps1" "$TARGET_DIR/install.sh"
fi

echo -e "\n✓ '$SKILL_NAME' skill installed successfully to $TARGET_DIR!"
