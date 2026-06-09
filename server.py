from flask import Flask, request
from flask_cors import CORS
from pypresence import Presence
from pypresence.types import ActivityType
import time
import logging
import sys
import os
import json
import subprocess
import psutil
import tempfile 

SOUNDCLOUD_LOGO = "https://a-v2.sndcdn.com/assets/images/sc-icons/favicon-2cadd14bdb.ico"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

PID_FILE = os.path.join(tempfile.gettempdir(), "soundcloud-rpc.pid")

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def enable_autostart():
    script = os.path.abspath(__file__)

    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SoundCloudRPC", 0, winreg.REG_SZ, f'"{sys.executable}" "{script}" --background')
        winreg.CloseKey(key)

    elif sys.platform == "darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.soundcloud-rpc.plist")
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.soundcloud-rpc</string>
    <key>ProgramArguments</key>
    <array><string>{sys.executable}</string><string>{script}</string><string>--background</string></array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>"""
        with open(plist_path, "w") as f:
            f.write(plist)
        os.system(f"launchctl load {plist_path}")

    else:
        service_dir = os.path.expanduser("~/.config/systemd/user")
        os.makedirs(service_dir, exist_ok=True)
        service_path = os.path.join(service_dir, "soundcloud-rpc.service")
        service = f"""[Unit]
Description=SoundCloud Discord RPC

[Service]
ExecStart={sys.executable} {script} --background
Restart=on-failure

[Install]
WantedBy=default.target
"""
        with open(service_path, "w") as f:
            f.write(service)
        os.system("systemctl --user daemon-reload")
        os.system("systemctl --user enable soundcloud-rpc")


def disable_autostart():
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "SoundCloudRPC")
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass

    elif sys.platform == "darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.soundcloud-rpc.plist")
        if os.path.exists(plist_path):
            os.system(f"launchctl unload {plist_path}")
            os.remove(plist_path)

    else:
        os.system("systemctl --user disable soundcloud-rpc")
        service_path = os.path.expanduser("~/.config/systemd/user/soundcloud-rpc.service")
        if os.path.exists(service_path):
            os.remove(service_path)


def run_in_background():
    script = os.path.abspath(__file__)

    if sys.platform == "win32":
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        p = subprocess.Popen(
            [pythonw, script, "--background"],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        )
    else:
        p = subprocess.Popen(
            [sys.executable, script, "--background"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

    with open(PID_FILE, "w") as f:
        f.write(str(p.pid))


def kill_process():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            proc.terminate()
            os.remove(PID_FILE)
            print("Stopped.")
            return
        except (psutil.NoSuchProcess, ValueError, ProcessLookupError):
            pass

    script = os.path.basename(__file__)
    found = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"] or []
            if any(script in arg for arg in cmdline) and "--background" in cmdline and proc.pid != os.getpid():
                proc.terminate()
                found = True
                print("Stopped.")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found:
        print("No running instance found.")

def print_settings(config):
    client_id = config.get("client_id", "not set")
    print(f"\n  [1] Autostart: {'on' if config['autostart'] else 'off'}")
    print(f"  [2] Run in background: {'on' if config['background'] else 'off'}")
    print(f"  [3] Discord Application ID: {client_id}")
    print(f"  [q] Exit\n")

def settings_menu():
    config = load_config() or {"autostart": False, "background": False, "client_id": ""}
    print("Settings")
    print_settings(config)

    while True:
        choice = input("> ").strip().lower()
        if choice == "1":
            config["autostart"] = not config["autostart"]
            if config["autostart"]:
                try:
                    enable_autostart()
                except Exception as e:
                    print(f"Failed to enable autostart: {e}")
                    config["autostart"] = False
            else:
                disable_autostart()
            save_config(config)
        elif choice == "2":
            config["background"] = not config["background"]
            save_config(config)
        elif choice == "3":
            new_id = input("Enter new Discord Application ID: ").strip()
            if new_id:
                config["client_id"] = new_id
                save_config(config)
                print("Application ID updated. Restart the server for it to take effect.")
        elif choice == "q":
            break
        print_settings(config)

def first_time_setup():
    print("First time setup\n")
    autostart = input("Enable autostart? (y/n): ").strip().lower() == "y"
    background = input("Always run in background? (y/n): ").strip().lower() == "y"
    client_id = input("Enter Discord Application ID: ").strip()

    config = {"autostart": autostart, "background": background, "client_id": client_id}
    save_config(config)

    if autostart:
        try:
            enable_autostart()
            print("Autostart enabled.")
        except Exception as e:
            print(f"Failed to enable autostart: {e}")
    print("")
    return config


if "--settings" in sys.argv:
    settings_menu()
    sys.exit(0)

if "--kill" in sys.argv:
    kill_process()
    sys.exit(0)

config = load_config()
if config is None:
    config = first_time_setup()

if config.get("background") and "--background" not in sys.argv:
    run_in_background()
    sys.exit(0)

if "--background" in sys.argv:
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

rpc = Presence(config["client_id"])
try:
    rpc.connect()
    if "--background" not in sys.argv:
        print("Connected to Discord RPC")
except Exception as e:
    if "--background" not in sys.argv:
        print(f"Failed to connect to Discord RPC: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

last_track = None
last_start = None

@app.route("/")
def home():
    return "SoundCloud RPC running"

@app.route("/update", methods=["POST"])
def update():
    global last_track, last_start
    data = request.json or {}
    title = data.get("title")
    artist = data.get("artist", "Unknown Artist")
    elapsed = float(data.get("elapsed") or 0)
    artwork = data.get("artwork") or SOUNDCLOUD_LOGO

    if not title:
        return {"ok": False}

    track_key = f"{artist}-{title}"

    if track_key != last_track:
        last_track = track_key
        last_start = int(time.time() - elapsed)

        if "--background" not in sys.argv:
            print(f"{artist} - {title}")

        try:
            rpc.update(
                activity_type=ActivityType.LISTENING,
                details=title,
                state=f"by {artist}",
                start=last_start,
                large_image=artwork,
                large_text=title,
            )
        except Exception as e:
            if "--background" not in sys.argv:
                print(f"RPC update failed: {e}")

    return {"ok": True}

@app.route("/clear", methods=["POST"])
def clear():
    global last_track, last_start
    last_track = None
    last_start = None
    try:
        rpc.clear()
    except Exception:
        pass
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)