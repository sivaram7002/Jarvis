# JARVIS Installation & Deployment Guide — Shazam Edition

Complete deployment walkthrough to clone, configure, run, compile, and link the JARVIS Voice Assistant & Remote Windows Automation Engine on any fresh Windows machine with VS Code.

---

## 1. System Prerequisites

Install the following software on the target laptop before proceeding:

1. **Python 3.10 to 3.12**
   - Download from [python.org](https://www.python.org/downloads/).
   - **Crucial:** Ensure the **"Add python.exe to PATH"** checkbox is checked during installation.
2. **Git for Windows**
   - Download from [git-scm.com](https://git-scm.com/).
3. **VS Code**
   - Install the official **Python** extension (by Microsoft) via the VS Code Extensions tab.
4. **LiveKit CLI (`lk`)**
   - Open PowerShell as Administrator and run:
     ```powershell
     winget install livekit.cli
     ```
   - Restart the terminal once installed to reload your PATH.

---

## 2. Project Setup & Virtual Environment

1. Open VS Code, launch an integrated terminal (`Ctrl + ~`), and clone your repository:
   ```powershell
   git clone <YOUR_GITHUB_REPO_URL>
   cd Jarvis



   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
python -m venv .venv
.\.venv\Scripts\Activate.ps1


python -m pip install --upgrade pip
pip install livekit-agents livekit-plugins-google livekit-api sounddevice pyautogui screen-brightness-control python-dotenv pystray pillow pyinstaller




New-Item -ItemType File -Name ".env.local"

LIVEKIT_URL="wss://jarvis-shazam-udrwa6i9.livekit.cloud"
LIVEKIT_API_KEY="APIUKc3RmbZ7x7C"
LIVEKIT_API_SECRET="SHNep382bhAJMW4y1Kk6efg1nBWZ7MgjG3ia7h2EHlqB"
GOOGLE_API_KEY="your_google_api_key_here"

.venv/
.env.local
dist/
build/
*.spec

run

python src/agent.py dev


python src/agent.py connect --room test-room


6. Remote Mobile Control (Android Client)
Open android-voice-assistant in Android Studio.

Allow Gradle sync to complete.

In app/src/main/res/values/strings.xml, update the connection URL:

XML
<resources>
    <string name="app_name">JARVIS</string>
    <string name="livekit_url">wss://jarvis-shazam-udrwa6i9.livekit.cloud</string>
</resources>




Generate a 1-year participant access token from your PC terminal:
lk token create --api-key APIUKc3RmbZ7x7C --api-secret SHNep382bhAJMW4y1Kk6efg1nBWZ7MgjG3ia7h2EHlqB --join --room test-room --identity Shazam --valid-for 8760h

Ensure tray_runner.py is present in the project root.
pyinstaller --noconsole --onefile --name "JARVIS" --add-data ".env.local;." tray_runner.py

Locate the built binary at dist/JARVIS.exe.



# Publish screen sharing to test-room
lk room join --room test-room --identity PC_Screen --publish-screen

# OR publish laptop webcam to test-room
lk room join --room test-room --identity PC_Cam --publish-camera
 lk dispatch create --room test-room --agent-name Jarvis
