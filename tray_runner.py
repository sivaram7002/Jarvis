import sys
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Import LiveKit server and cli from src/agent.py
from src.agent import server, cli

def create_tray_icon():
    image = Image.new("RGB", (64, 64), color=(20, 20, 20))
    draw = ImageDraw.Draw(image)
    # Draw an arc / circle for JARVIS
    draw.ellipse((8, 8, 56, 56), outline=(0, 210, 255), width=4)
    draw.ellipse((20, 20, 44, 44), fill=(0, 168, 255))
    return image

def start_agent():
    # Pass 'dev' or 'connect' mode arguments automatically
    sys.argv = ["agent.py", "dev"]
    cli.run_app(server)

def on_quit(icon, item):
    icon.stop()
    sys.exit(0)

def main():
    # Run the LiveKit agent worker in the background
    agent_thread = threading.Thread(target=start_agent, daemon=True)
    agent_thread.start()

    # System Tray Menu
    menu = pystray.Menu(
        item("JARVIS: Online (Shazam)", lambda icon, item: None, enabled=False),
        item("Quit JARVIS", on_quit)
    )

    icon = pystray.Icon("JARVIS", create_tray_icon(), "JARVIS Voice Assistant", menu)
    icon.run()

if __name__ == "__main__":
    main()