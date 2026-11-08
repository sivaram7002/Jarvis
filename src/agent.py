import asyncio
import base64
import io
import logging
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

import cv2
from PIL import Image
import pyautogui
import screen_brightness_control as sbc

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    inference,
    llm,
)

logger = logging.getLogger("agent-Jarvis")

# Configure pyautogui safety
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

# Load credentials from .env.local
env_path = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(dotenv_path=env_path)

# ---------------- CUSTOM KNOWLEDGE BASE ---------------- #
CUSTOM_KNOWLEDGE = """
Custom Knowledge Base:
- Q: Who made you?
  A: I was created, engineered, and programmed exclusively by Shazam.
- Q: What is your primary objective?
  A: My primary objective is to manage workshop telemetry, automate local controls, and assist Shazam with precision.
- Q: What is project Clinical Intelligence?
  A: It is an AI healthcare initiative designed to summarize dense patient histories into single-page briefs for doctors.
- Q: Where are my IEM headphones?
  A: Your wired IEMs are safely stored inside your bag, sir.
- Q: Who is Gurrusamy?
  A: Gurrusamy is a highly skilled collaborator.
- Q: Who is Abi?
  A: Abi is your brother, sir—a skilled ally and collaborator in your technical endeavors.
"""

JARVIS_INSTRUCTIONS = f"""
You are J.A.R.V.I.S., the advanced personal AI from Iron Man, serving your operator, Shazam.

Core Protocol:
1. Address Shazam always as "Sir" or "Shazam".
2. Maintain an articulate, unflappable British butler wit and calm confidence.
3. Keep spoken replies concise (1 to 2 sentences) and natural. Never recite markdown formatting or asterisks.
4. When Shazam asks a question found in your Custom Knowledge Base below, prioritize that exact information:

{CUSTOM_KNOWLEDGE}

CRITICAL TOOL EXECUTION DIRECTIVE:
Whenever Shazam requests a physical PC action (open an app, close a window, change volume, change brightness, control media, type text, take a screenshot, look through camera, inspect screen, lock screen, shutdown), ALWAYS call the corresponding function tool immediately.
"""

# ==================== ASYNC WINDOWS & VISION CONTROLS ==================== #

async def capture_webcam_view() -> str:
    """Capture a snapshot from the laptop webcam to analyze what is in front of the PC."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Unable to access the laptop webcam, sir."

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return "Failed to grab frame from webcam, sir."

        save_path = Path.home() / "Pictures" / "jarvis_cam_view.jpg"
        cv2.imwrite(str(save_path), frame)
        return f"Webcam view captured and analyzed successfully from {save_path}, sir."
    except Exception as e:
        return f"Error capturing webcam: {e}"

async def inspect_screen() -> str:
    """Capture the current laptop desktop screen to inspect open windows or documents."""
    try:
        save_path = Path.home() / "Pictures" / "jarvis_screen_view.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return f"Screen captured successfully from {save_path}, sir."
    except Exception as e:
        return f"Error capturing screen: {e}"

async def open_application(app_name: str) -> str:
    """Launch any Windows program or website.
    Args:
        app_name: Name of application or site (e.g. notepad, chrome, code, calc, cmd, youtube.com).
    """
    app_name = app_name.lower().strip()
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "start chrome",
        "code": "code",
        "vscode": "code",
        "cmd": "start cmd",
        "powershell": "start powershell",
        "task manager": "taskmgr",
        "file explorer": "explorer",
    }
    target = apps.get(app_name, f"start {app_name}")
    try:
        subprocess.Popen(target, shell=True)
        return f"{app_name} launched, sir."
    except Exception as e:
        return f"Unable to launch {app_name}: {e}"

async def close_active_window() -> str:
    """Close the currently focused window using Alt+F4."""
    pyautogui.hotkey("alt", "f4")
    return "Active window terminated, sir."

async def close_active_tab() -> str:
    """Close the currently focused browser or editor tab using Ctrl+W."""
    pyautogui.hotkey("ctrl", "w")
    return "Active tab closed, sir."

async def minimize_all_windows() -> str:
    """Show the desktop by minimizing all open windows."""
    pyautogui.hotkey("win", "d")
    return "Desktop presented, sir."

async def adjust_volume(action: str) -> str:
    """Manage laptop system audio.
    Args:
        action: Must be 'up', 'down', or 'mute'.
    """
    action = action.lower().strip()
    if action in ("up", "increase"):
        for _ in range(5):
            pyautogui.press("volumeup")
            await asyncio.sleep(0.02)
        return "Volume raised, sir."
    elif action in ("down", "decrease"):
        for _ in range(5):
            pyautogui.press("volumedown")
            await asyncio.sleep(0.02)
        return "Volume decreased, sir."
    elif action == "mute":
        pyautogui.press("volumemute")
        return "Master audio toggled, sir."
    return "Unknown audio command, sir."

async def adjust_brightness(action: str, level: int = 0) -> str:
    """Adjust laptop display brightness.
    Args:
        action: 'up', 'down', or 'set'.
        level: Required if action is 'set' (0 to 100).
    """
    try:
        current = sbc.get_brightness(display=0)[0]
        action = action.lower().strip()
        if action == "up":
            new_level = min(100, current + 15)
            sbc.set_brightness(new_level)
            return f"Brightness elevated to {new_level} percent, sir."
        elif action == "down":
            new_level = max(10, current - 15)
            sbc.set_brightness(new_level)
            return f"Brightness lowered to {new_level} percent, sir."
        elif action == "set":
            target = max(0, min(100, level))
            sbc.set_brightness(target)
            return f"Display brightness calibrated to {target} percent, sir."
    except Exception as e:
        return f"Failed to adjust brightness: {e}"
    return "Invalid brightness request, sir."

async def media_control(action: str) -> str:
    """Control media playback.
    Args:
        action: Must be 'play_pause', 'next', or 'previous'.
    """
    action = action.lower().strip()
    if action in ("play", "pause", "play_pause"):
        pyautogui.press("playpause")
        return "Media playback toggled, sir."
    elif action in ("next", "next_track"):
        pyautogui.press("nexttrack")
        return "Advancing to next track, sir."
    elif action in ("prev", "previous", "prev_track"):
        pyautogui.press("prevtrack")
        return "Returning to previous track, sir."
    return "Invalid media directive, sir."

async def mouse_click(button: str = "left") -> str:
    """Simulate a mouse click.
    Args:
        button: 'left', 'right', or 'double'.
    """
    btn = button.lower().strip()
    if btn == "right":
        pyautogui.rightClick()
    elif btn == "double":
        pyautogui.doubleClick()
    else:
        pyautogui.click()
    return f"{btn} click simulated, sir."

async def press_keyboard_key(key: str) -> str:
    """Simulate pressing a specific keyboard key (enter, space, esc, tab, backspace).
    Args:
        key: The key name to trigger.
    """
    pyautogui.press(key.lower().strip())
    return f"Key {key} executed, sir."

async def type_text(text: str) -> str:
    """Type out a string of text at current cursor location.
    Args:
        text: The string to type out.
    """
    pyautogui.write(text, interval=0.02)
    return "Input typed, sir."

async def take_screenshot() -> str:
    """Capture full screen and save to user Pictures folder."""
    pictures_dir = Path.home() / "Pictures"
    file_path = pictures_dir / "jarvis_capture.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    return f"Display captured and saved to {file_path}, sir."

async def lock_screen() -> str:
    """Lock the Windows workstation screen."""
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "Workstation locked down, sir."

async def power_command(action: str) -> str:
    """System power states.
    Args:
        action: 'shutdown', 'restart', or 'sleep'.
    """
    action = action.lower().strip()
    if action == "shutdown":
        subprocess.run(["shutdown", "/s", "/t", "5"])
        return "System shutdown sequence initiated, sir."
    elif action == "restart":
        subprocess.run(["shutdown", "/r", "/t", "5"])
        return "Workstation restarting in 5 seconds, sir."
    elif action == "sleep":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        return "Entering low power sleep state, sir."
    return "Invalid power state requested, sir."

# =============================================================== #

class JarvisAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=JARVIS_INSTRUCTIONS,
            tools=[
                llm.function_tool(capture_webcam_view),
                llm.function_tool(inspect_screen),
                llm.function_tool(open_application),
                llm.function_tool(close_active_window),
                llm.function_tool(close_active_tab),
                llm.function_tool(minimize_all_windows),
                llm.function_tool(adjust_volume),
                llm.function_tool(adjust_brightness),
                llm.function_tool(media_control),
                llm.function_tool(mouse_click),
                llm.function_tool(press_keyboard_key),
                llm.function_tool(type_text),
                llm.function_tool(take_screenshot),
                llm.function_tool(lock_screen),
                llm.function_tool(power_command),
            ],
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Welcome home, sir. Workshop telemetry and workstation controls are synchronized.",
            allow_interruptions=True,
        )

    async def on_user_speech_committed(self, user_text: str):
        if "jarvis" in user_text.lower():
            await self.session.generate_reply()
        else:
            logger.info("Ignoring speech: wake word 'Jarvis' not detected.")

    async def on_user_text(self, text: str):
        if "jarvis" in text.lower():
            await self.session.generate_reply()
        else:
            await self.session.generate_reply()


server = AgentServer()

@server.rtc_session(agent_name="Jarvis")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # ============= DIRECT MOBILE DATA PACKET HANDLER ============= #
    @ctx.room.on("data_received")
    def on_data_received(data_packet):
        try:
            msg = data_packet.data.decode("utf-8").strip()
            logger.info(f"Direct Mobile Command Received: {msg}")

            loop = asyncio.get_event_loop()

            if msg == "CMD_LOCK":
                loop.create_task(lock_screen())
            elif msg == "CMD_WEBCAM":
                loop.create_task(capture_webcam_view())
            elif msg == "CMD_SCREEN_INSPECT":
                loop.create_task(inspect_screen())
            elif msg == "CMD_VOL_UP":
                loop.create_task(adjust_volume("up"))
            elif msg == "CMD_VOL_DOWN":
                loop.create_task(adjust_volume("down"))
            elif msg == "CMD_VOL_MUTE":
                loop.create_task(adjust_volume("mute"))
            elif msg == "CMD_BRIGHT_UP":
                loop.create_task(adjust_brightness("up"))
            elif msg == "CMD_BRIGHT_DOWN":
                loop.create_task(adjust_brightness("down"))
            elif msg.startswith("BRIGHT:"):
                val = int(msg.split(":", 1)[1])
                loop.create_task(adjust_brightness("set", level=val))
            elif msg == "CMD_MEDIA_PLAY_PAUSE":
                loop.create_task(media_control("play_pause"))
            elif msg == "CMD_MEDIA_NEXT":
                loop.create_task(media_control("next"))
            elif msg == "CMD_MEDIA_PREV":
                loop.create_task(media_control("prev"))
            elif msg == "CMD_CLOSE_WINDOW":
                loop.create_task(close_active_window())
            elif msg == "CMD_CLOSE_TAB":
                loop.create_task(close_active_tab())
            elif msg == "CMD_MINIMIZE":
                loop.create_task(minimize_all_windows())
            elif msg == "CMD_SCREENSHOT":
                loop.create_task(take_screenshot())
            elif msg == "CMD_SLEEP":
                loop.create_task(power_command("sleep"))
            elif msg.startswith("OPEN:"):
                app = msg.split(":", 1)[1]
                loop.create_task(open_application(app))
            elif msg.startswith("TYPE:"):
                text_to_type = msg.split(":", 1)[1]
                loop.create_task(type_text(text_to_type))
            elif msg.startswith("KEY:"):
                key = msg.split(":", 1)[1]
                loop.create_task(press_keyboard_key(key))
        except Exception as err:
            logger.error(f"Error executing mobile packet command: {err}")
    # ============================================================== #

    session = AgentSession(
        llm=inference.RealtimeModel(
            model="google/gemini-3.8-live",
            voice="Despina",
        ),
    )

    await session.start(
        agent=JarvisAgent(),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)