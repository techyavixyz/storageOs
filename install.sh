#!/bin/bash

# Configuration
GITHUB_USER="YOUR_USERNAME"
REPO="YOUR_REPO"
BINARY_URL="https://github.com/$GITHUB_USER/$REPO/releases/latest/download/StorageOS"

echo "Step 1: Update System Packages"
sudo apt update && sudo apt upgrade -y

echo "Step 2: Install Prerequisites"
# Installing system-level GUI libraries so the app can launch
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 libcanberra-gtk-module xhost

echo "Step 3: Download StorageOS Engine"
# Downloading the pre-compiled binary directly into the install path
sudo curl -L $BINARY_URL -o /usr/local/bin/storageos
sudo chmod +x /usr/local/bin/storageos

echo "Step 4: Configure Desktop Integration"
# Creating the launcher and setting up the SVG icon
sudo mkdir -p /usr/share/icons/storageos
# (Add the SVG cat command from the previous step here)

echo "Step 5: Create Desktop Launcher"
# Bridging the GUI through pkexec
sudo tee /usr/share/applications/storageos.desktop > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=StorageOS Pro
Exec=bash -c "xhost +si:localuser:root; pkexec env DISPLAY=:0 XAUTHORITY=/home/\$USER/.Xauthority /usr/local/bin/storageos; xhost -si:localuser:root"
Icon=/usr/share/icons/storageos/icon.svg
Terminal=false
Categories=System;Utility;
EOF

echo "Step 6: Refresh Package Index and Cache"
sudo update-desktop-database
sudo fc-cache -f -v

echo "Done! You can now run 'storageos' or find it in your App Menu."