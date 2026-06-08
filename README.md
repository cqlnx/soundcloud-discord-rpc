# SoundCloud Discord RPC

Shows your currently playing SoundCloud track in Discord, including the track artwork, artist, and elapsed time.

![preview](assets/preview.png)

## Requirements

* Python 3.9+
* A Chromium-based browser (Chrome, Edge, Brave, etc.) or Firefox
* Discord desktop app

## Setup

### 1. Create a Discord application

1. Open the Discord Developer Portal.
2. Create a new application.
3. Name it **SoundCloud** (this is the name that appears in your Discord status).
4. Copy the **Client ID** from the **General Information** page.
5. Open `server.py` and replace the `DISCORD_CLIENT_ID` value with your Client ID.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the browser extension

The extension is what reads information from the SoundCloud web player and sends it to the local RPC server.

#### Chrome / Edge / Brave
#### Chrome / Edge / Brave

1. Open the Extensions page:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
   - Brave: `brave://extensions`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the project's `extension` folder
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the project's `extension` folder

The extension should now appear in your list of installed extensions.

#### Firefox

1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Open the `extension` folder
4. Select the `manifest.json` file

**Note:** Firefox temporary add-ons are removed when the browser is closed, so you'll need to load it again after restarting Firefox.

### 4. Start the RPC server

Run:

```bash
python server.py
```

You should see a message indicating that the server is listening on port `8765`.

### 5. Use it

1. Make sure Discord is running.
2. Make sure the RPC server is running.
3. Open SoundCloud in the browser where the extension is installed.
4. Play any track.

Your Discord Rich Presence should update automatically with the track title, artist, artwork, and playback progress.

## How it works

1. The browser extension watches the SoundCloud web player for track and playback changes.
2. When something changes, the extension sends the current track information to a local server running on `localhost:8765`.
3. The server updates your Discord Rich Presence using Discord's RPC connection.
4. Discord displays the current track, artwork, artist, and elapsed playback time in your profile.
