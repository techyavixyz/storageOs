🏗️ Build Instructions
Initialize Environment:
Create a virtual environment that allows access to system-level GTK libraries:

Bash

python3 -m venv --system-site-packages venv
source venv/bin/activate
Install Dependencies:

Bash

pip install pywebview fastapi uvicorn psutil pyinstaller
Generate Executable:
Use PyInstaller to bundle the app. This command includes the necessary "hidden" hooks for the GUI to function:

Bash

pyinstaller --noconsole --onefile \
--hidden-import=gi \
--hidden-import=gi.repository.Gtk \
--hidden-import=gi.repository.WebKit2 \
--collect-all webview \
--name "StorageOS" main.py
The resulting binary will be located in the dist/ folder.

🚫 GitHub Exclusions
To keep the repository clean, the following must be ignored in your .gitignore:

venv/: Specific to your machine's architecture.

build/: Temporary files created during the PyInstaller process.

dist/: The final binary (should be uploaded to GitHub Releases instead).

__pycache__/: Compiled Python bytecode.