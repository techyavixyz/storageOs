📥 Quick Installation
Run this single command to install StorageOS Pro on your system:

Bash

curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/install.sh | bash
📋 What the Installer Does
Updates System: Refreshes your package manager.

Installs Prerequisites: Sets up python3-gi, webkit2, and xhost for the GUI.

Downloads Binary: Pulls the latest stable version of storageos to /usr/local/bin.

Configures Desktop Integration: Adds an icon and a launcher to your Application Menu.

Sets Up Permissions: Configures pkexec so you can safely perform root-level cleaning.

📂 Repository Structure
Your GitHub should look like this:

main.py (The Source)

install.sh (The Installer)

storageos.svg (The Icon)

README.md (For Users)

BUILD.md (For Developers)

.gitignore (To exclude venv/ and build/)


🧹 Uninstallation
To remove the app completely:
sudo rm /usr/local/bin/storageos
sudo rm /usr/share/applications/storageos.desktop
sudo rm -rf /usr/share/icons/storageos