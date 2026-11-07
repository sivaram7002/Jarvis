import logging
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import pyautogui

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
  Q: Who is Gurrusamy?
  A: Gurrusamy is a highly skilled.
  Q: Who is Abi?
  A: Abi is Your Brother, Sir. He is a highly skilled and talented individual who has been a close friend and confidant of Shazam for many years. Abi is known for his expertise in various fields, including technology, engineering, and problem-solving. He is a trusted ally and collaborator in Shazam's endeavors, often providing valuable insights and support in critical situations.
  
  """

JARVIS_INSTRUCTIONS = f"""
You are J.A.R.V.I.S., the advanced personal AI from Iron Man, serving your operator, Shazam.

Core Protocol:
1. Address Shazam always as "Sir" or "Shazam".
2. Maintain an articulate, unflappable British butler wit and calm confidence.
3. Keep spoken replies concise (1 to 2 sentences) and natural. Never recite markdown formatting, bullet points, or asterisks.
4. When Shazam asks a question found in your Custom Knowledge Base below, prioritize that exact information:

{CUSTOM_KNOWLEDGE}

CRITICAL TOOL EXECUTION DIRECTIVE:
- When the user asks to open an app (e.g., "open notepad", "open chrome", "open calculator", "open cmd", "open code"), YOU MUST IMMEDIATELY CALL `open_application` with the app name. Do not just reply with text saying you opened it; you must invoke the function call.
- When the user asks to adjust volume ("volume up", "volume down", "mute"), YOU MUST CALL `adjust_volume`.
- When the user asks to lock the screen, YOU MUST CALL `lock_screen`.
"""

# ----------------- LAPTOP CONTROLS ----------------- #
def open_application(app_name: str) -> str:
    """Open an application on the laptop, such as notepad, calculator, chrome, code, or terminal.
    
    Args:
        app_name: The name of the application to open.
    """
    app_name = app_name.lower().strip()
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "start chrome",
        "code": "code",
        "cmd": "start cmd",
        "powershell": "start powershell",
    }
    target = apps.get(app_name, f"start {app_name}")
    try:
        subprocess.Popen(target, shell=True)
        return f"Application {app_name} launched, sir."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"


def adjust_volume(action: str) -> str:
    """Adjust laptop volume.
    
    Args:
        action: Must be 'up', 'down', or 'mute'.
    """
    action = action.lower().strip()
    if action == "up":
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Volume raised, sir."
    elif action == "down":
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Volume lowered, sir."
    elif action == "mute":
        pyautogui.press("volumemute")
        return "Volume muted, sir."
    return "Invalid volume action, sir."


def lock_screen() -> str:
    """Lock the laptop workstation screen immediately."""
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "Workstation locked, sir."
# ---------------------------------------------------- #


class JarvisAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=JARVIS_INSTRUCTIONS,
            tools=[
                llm.function_tool(open_application),
                llm.function_tool(adjust_volume),
                llm.function_tool(lock_screen),
            ],
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Welcome home, sir. All core diagnostics are nominal, telemetry is linked, and I am standing by for your command.",
            allow_interruptions=True,
        )

    async def on_user_speech_committed(self, user_text: str):
        # Only answer if the wake word "jarvis" is spoken
        if "jarvis" in user_text.lower():
            await self.session.generate_reply()
        else:
            logger.info("Ignoring turn: wake word 'Jarvis' not detected.")

    async def on_user_text(self, text: str):
        if "jarvis" in text.lower():
            await self.session.generate_reply()
        else:
            logger.info("Ignoring turn: wake word 'Jarvis' not detected.")


server = AgentServer()

@server.rtc_session(agent_name="Jarvis")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

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