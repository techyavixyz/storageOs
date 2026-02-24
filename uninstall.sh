#!/bin/bash

# --- CONFIGURATION ---
GITHUB_USER="techyavixyz"
REPO_NAME="storageOs"
BINARY_NAME="StorageOS"
# We store the actual binary in a hidden spot and use a wrapper for the command
REAL_BINARY="/usr/local/bin/.storageos-engine"
COMMAND_PATH="/usr/local/bin/storageos"
ICON_PATH="/usr/share/icons/storageos/icon.svg"
DESKTOP_ENTRY="/usr/share/applications/storageos.desktop"

echo "🚀 Installing StorageOS Pro (GUI + CLI Fix)..."

# 1. Install System Dependencies
sudo apt update
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 \
libcanberra-gtk-module libcanberra-gtk3-module x11-xserver-utils xhost curl -y

# 2. Download and Hide the Engine
echo "📥 Downloading engine..."
BINARY_URL="https://github.com/$GITHUB_USER/$REPO_NAME/releases/latest/download/$BINARY_NAME"
sudo curl -L "$BINARY_URL" -o "$REAL_BINARY"
sudo chmod +x "$REAL_BINARY"

# 3. Create the Permanent CLI Wrapper
# This ensures typing 'storageos' in terminal works without font errors
echo "💻 Configuring CLI command..."
cat <<EOF | sudo tee "$COMMAND_PATH" > /dev/null
#!/bin/bash
xhost +si:localuser:root > /dev/null 2>&1
pkexec env DISPLAY=\$DISPLAY XAUTHORITY=\${XAUTHORITY:-\$HOME/.Xauthority} FONTCONFIG_FILE=/etc/fonts/fonts.conf $REAL_BINARY "\$@"
EOF
sudo chmod +x "$COMMAND_PATH"

# 4. Create SVG Icon
sudo mkdir -p /usr/share/icons/storageos
cat <<EOF | sudo tee "$ICON_PATH" > /dev/null
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" rx="120" fill="#0f172a"/>
  <path d="M120 160C120 137.909 137.909 120 160 120H352C374.091 120 392 137.909 392 160V352C392 374.091 374.091 392 352 392H160C137.909 392 120 374.091 120 352V160Z" fill="#3b82f6"/>
  <path d="M160 220H352V260H160V220ZM160 300H352V340H160V300Z" fill="#ffffff" fill-opacity="0.2"/>
  <circle cx="330" cy="180" r="15" fill="#60a5fa"/>
</svg>
EOF

# 5. Create Desktop Launcher (Points to our new wrapper)
echo "🖥️ Configuring GUI launcher..."
cat <<EOF | sudo tee "$DESKTOP_ENTRY" > /dev/null
[Desktop Entry]
Version=1.0
Type=Application
Name=StorageOS Pro
Comment=Monitor and Clean Disk Space
Exec=$COMMAND_PATH
Icon=$ICON_PATH
Terminal=false
Categories=System;Utility;
EOF

# 6. Final System Cleanup
sudo update-desktop-database
sudo rm -rf /var/cache/fontconfig/*
sudo fc-cache -f -v > /dev/null

echo "✅ DONE! Use the command 'storageos' or the App Menu."