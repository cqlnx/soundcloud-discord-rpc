let lastTrack = "";
let lastElapsed = 0;

function getElapsedSeconds() {
    const el = document.querySelector('.playbackTimeline__timePassed span[aria-hidden="true"]');
    if (!el) return 0;

    const parts = el.textContent.trim().split(":").map(Number);

    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];

    return 0;
}

function getArtworkUrl() {
    const el = document.querySelector(".playbackSoundBadge__avatar span[style]");
    if (!el) return null;

    const match = el.getAttribute("style").match(/url\("(.+?)"\)/);
    return match ? match[1].replace("-t50x50", "-t200x200") : null;
}

function getTrackData() {
    const titleEl = document.querySelector(".playbackSoundBadge__titleLink span");
    const artistEl = document.querySelector(".playbackSoundBadge__lightLink");

    const title = titleEl?.textContent?.trim().replace(/^Current track:\s*/i, "");
    let artist = artistEl?.textContent?.trim();

    const ignored = ["Current track", "SoundCloud Go+", "Playlist", ""];
    if (!artist || ignored.includes(artist)) artist = "Unknown Artist";

    if (!title) return null;

    return { title, artist, artwork: getArtworkUrl() };
}

function send(payload) {
    fetch("http://127.0.0.1:8765/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    }).catch(() => {});
}

function checkTrackChange() {
    const data = getTrackData();
    if (!data) return;

    const key = `${data.artist}-${data.title}`;
    if (key === lastTrack) return;

    lastTrack = key;
    lastElapsed = 0;

    send({ title: data.title, artist: data.artist, artwork: data.artwork, elapsed: 0 });
}

function updateTime() {
    const data = getTrackData();
    if (!data) return;

    const elapsed = getElapsedSeconds();
    if (Math.abs(elapsed - lastElapsed) < 1) return;

    lastElapsed = elapsed;

    send({ title: data.title, artist: data.artist, artwork: data.artwork, elapsed });
}

const observer = new MutationObserver(checkTrackChange);
observer.observe(document.body, { childList: true, subtree: true });

setInterval(updateTime, 1000);
setInterval(checkTrackChange, 3000);