# SoundCloud Discord RPC

Shows your currently playing SoundCloud track in Discord, including the track artwork, artist, and elapsed time.

![preview](assets/preview.png)

## Requirements

- Python 3.9+
- A Chromium or Firefox based browser
- Discord desktop app

## Setup

### 1. Create a Discord application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application
2. Name it `SoundCloud` (this is what shows in your Discord status)
3. Copy the **Client ID** from the General Information page — you'll need it on first run

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the browser extension

The extension reads what's playing in the SoundCloud web player and sends it to the local server.

**Chrome / Edge / Brave:**
1. Open the Extensions page:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
   - Brave: `brave://extensions`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension` folder

**Firefox:**
1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Open the `extension` folder and select `manifest.json`

> **Note:** Firefox temporary add-ons are removed when the browser closes, so you'll need to reload it after restarting Firefox.

### 4. Run the server

```bash
python server.py
```

On first run you'll be asked for your Discord Application ID and a couple of settings. After that it starts automatically with those preferences saved.

## Commands

```bash
python server.py             # start normally
python server.py --settings  # change settings
python server.py --kill      # stop a background instance
```

## How it works

1. The browser extension watches the SoundCloud player for track and playback changes
2. When something changes it sends the current track info to a local server on port `8765`
3. The server updates your Discord Rich Presence with the track title, artist, artwork, and elapsed time
4. When you pause or stop, the Discord status is cleared automatically