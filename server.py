from flask import Flask, request
from flask_cors import CORS
from pypresence import Presence
from pypresence.types import ActivityType
import time
import sys

DISCORD_CLIENT_ID = "your_discord_client_id_here"  # Replace with your actual Discord Client ID
SOUNDCLOUD_LOGO = "https://a-v2.sndcdn.com/assets/images/sc-icons/favicon-2cadd14bdb.ico"

rpc = Presence(DISCORD_CLIENT_ID)

try:
    rpc.connect()
    print("Connected to Discord RPC")
except Exception as e:
    print(f"Failed to connect to Discord RPC: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

last_track = None
last_start = None

def print_status(artist, title, elapsed):
    sys.stdout.write(f"\r\033[2K{artist} - {title} ({elapsed}s)")
    sys.stdout.flush()

@app.route("/")
def home():
    return "SoundCloud RPC running"

@app.route("/update", methods=["POST"])
def update():
    global last_track, last_start

    data = request.json or {}
    title   = data.get("title")
    artist  = data.get("artist", "Unknown Artist")
    elapsed = float(data.get("elapsed") or 0)
    artwork = data.get("artwork") or SOUNDCLOUD_LOGO

    if not title:
        return {"ok": False}

    track_key = f"{artist}-{title}"

    if track_key != last_track:
        last_track = track_key
        last_start = int(time.time() - elapsed)

        print(f"\nNow playing: {artist} - {title}")

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
            print(f"\nRPC update failed: {e}")

    print_status(artist, title, int(elapsed))
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

    print("\nCleared")
    return {"ok": True}

app.run(port=8765)