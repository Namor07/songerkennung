import os
import requests

AUDD_API_URL = "https://api.audd.io/"
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# --------------------------------------------------
# Song-Erkennung (AudD)
# --------------------------------------------------
def recognize_song(uploaded_file, audio_url):
    data = {}
    files = None

    if uploaded_file:
        files = {"file": uploaded_file}
    elif audio_url:
        data["url"] = audio_url
    else:
        return None

    try:
        r = requests.post(AUDD_API_URL, data=data, files=files, timeout=20)
        result = r.json().get("result")
    except Exception:
        return None

    if not result:
        return None

    title = result.get("title")
    artist = result.get("artist")
    album = result.get("album")

    genres = get_genres_from_lastfm(title, artist)
    cover = get_cover_from_lastfm(title, artist)

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "genre": genres,
        "cover": cover
    }

# --------------------------------------------------
# Last.fm: Request-Helfer
# --------------------------------------------------
def _lastfm_request(params: dict) -> dict:
    params["api_key"] = LASTFM_API_KEY
    params["format"] = "json"

    try:
        r = requests.get(LASTFM_BASE_URL, params=params, timeout=10)
        return r.json()
    except Exception:
        return {}

# --------------------------------------------------
# Genre-Erkennung (Last.fm Tags)
# --------------------------------------------------
def get_genres_from_lastfm(title: str, artist: str) -> list[str]:
    if not LASTFM_API_KEY or not title or not artist:
        return []

    data = _lastfm_request({
        "method": "track.getInfo",
        "track": title,
        "artist": artist
    })

    tags = (
        data.get("track", {})
            .get("toptags", {})
            .get("tag", [])
    )

    # Mehrere Genres sind normal!
    return [t["name"] for t in tags[:5] if "name" in t]

# --------------------------------------------------
# Cover (Last.fm)
# --------------------------------------------------
def get_cover_from_lastfm(title: str, artist: str) -> str | None:
    if not LASTFM_API_KEY:
        return None

    data = _lastfm_request({
        "method": "track.getInfo",
        "track": title,
        "artist": artist
    })

    album = data.get("track", {}).get("album", {})
    images = album.get("image", [])

    if images:
        return images[-1].get("#text")  # größtes Bild

    return None
