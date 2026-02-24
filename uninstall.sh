#!/bin/bash

# --- CONFIGURATION ---
INSTALL_PATH="/usr/local/bin/storageos"
ICON_DIR="/usr/share/icons/storageos"
DESKTOP_ENTRY="/usr/share/applications/storageos.desktop"

echo "🗑️ Uninstalling StorageOS Pro..."

# 1. Remove the binary
if [ -f "$INSTALL_PATH" ]; then
    sudo rm "$INSTALL_PATH"
    echo "✅ Removed binary"
fi

# 2. Remove the Desktop entry
if [ -f "$DESKTOP_ENTRY" ]; then
    sudo rm "$DESKTOP_ENTRY"
    echo "✅ Removed desktop launcher"
fi

# 3. Remove icons
if [ -d "$ICON_DIR" ]; then
    sudo rm -rf "$ICON_DIR"
    echo "✅ Removed icons"
fi

# 4. Refresh desktop database
sudo update-desktop-database

echo "✨ StorageOS Pro has been removed from your system."