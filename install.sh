#!/bin/bash

# --- CONFIGURATION ---
GITHUB_USER="techyavixyz"
REPO_NAME="storageOs"
BINARY_NAME="StorageOS"
INSTALL_PATH="/usr/local/bin/storageos"
ICON_PATH="/usr/share/icons/storageos/icon.svg"
DESKTOP_ENTRY="/usr/share/applications/storageos.desktop"

echo "--------------------------------------------------"
echo "🚀 Installing StorageOS Pro from techyavixyz/storageOs"
echo "--------------------------------------------------"

# 1. Repair and Update System Packages
echo "🛠️ Step 1: Repairing package manager and installing dependencies..."
sudo dpkg --configure -a
sudo apt update
# Added libcanberra-gtk3-module and x11-xserver-utils for better GUI stability
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 \
libcanberra-gtk-module libcanberra-gtk3-module x11-xserver-utils xhost curl -y

# 2. Download Binary from GitHub Releases
echo "📥 Step 2: Downloading latest binary..."
BINARY_URL="https://github.com/$GITHUB_USER/$REPO_NAME/releases/latest/download/$BINARY_NAME"
sudo curl -L "$BINARY_URL" -o "$INSTALL_PATH"
sudo chmod +x "$INSTALL_PATH"

# 3. Create SVG Icon
echo "🎨 Step 3: Creating application icon..."
sudo mkdir -p /usr/share/icons/storageos
cat <<EOF | sudo tee "$ICON_PATH" > /dev/null
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" rx="120" fill="#0f172a"/>
  <path d="M120 160C120 137.909 137.909 120 160 120H352C374.091 120 392 137.909 392 160V352C392 374.091 374.091 392 352 392H160C137.909 392 120 374.091 120 352V160Z" fill="#3b82f6"/>
  <path d="M160 220H352V260H160V220ZM160 300H352V340H160V300Z" fill="#ffffff" fill-opacity="0.2"/>
  <circle cx="330" cy="180" r="15" fill="#60a5fa"/>
</svg>
EOF

# 4. Create Desktop Launcher (The "Bypass" Version)
echo "🖥️ Step 4: Creating desktop launcher..."
# FONTCONFIG_FILE=/dev/null fixes the "out of memory" font error
# XAUTHORITY path is dynamically detected to support different user home setups
cat <<EOF | sudo tee "$DESKTOP_ENTRY" > /dev/null
[Desktop Entry]
Version=1.0
Type=Application
Name=StorageOS Pro
Comment=Monitor and Clean Disk Space
Exec=bash -c "xhost +si:localuser:root; pkexec env DISPLAY=:0 XAUTHORITY=\${XAUTHORITY:-\$HOME/.Xauthority} FONTCONFIG_FILE=/etc/fonts/fonts.conf $INSTALL_PATH; xhost -si:localuser:root"
Icon=$ICON_PATH
Terminal=false
Categories=System;Utility;
Keywords=disk;storage;clean;monitor;
EOF

# 5. Clean Caches
echo "🔄 Step 5: Refreshing font and desktop caches..."
sudo update-desktop-database
sudo rm -rf /var/cache/fontconfig/*
sudo fc-cache -f -v > /dev/null

echo "--------------------------------------------------"
echo "✅ Installation Complete!"
echo "✨ Search for 'StorageOS Pro' in your app menu to start."
echo "--------------------------------------------------"