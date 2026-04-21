import streamlit as st
import requests

AUDD_API_URL = "https://api.audd.io/"
LASTFM_API_KEY = st.secrets.get("LASTFM_API_KEY")

if not LASTFM_API_KEY:
    raise RuntimeError(
        "Last.fm API-Key fehlt! Bitte in .streamlit/secrets.toml setzen."
    )

LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
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
def lastfm_request(params: dict) -> dict:
    params["api_key"] = LASTFM_API_KEY
    params["format"] = "json"

    r = requests.get(LASTFM_BASE_URL, params=params, timeout=10)
    return r.json()#
    
# --------------------------------------------------
# Genre-Erkennung (Last.fm Tags)
# --------------------------------------------------
def get_genres_from_lastfm(title: str, artist: str) -> list[str]:
    # 1️⃣ Track-Tags
    data = lastfm_request({
        "method": "track.getInfo",
        "track": title,
        "artist": artist,
        "autocorrect": 1
    })

    tags = (
        data.get("track", {})
            .get("toptags", {})
            .get("tag", [])
    )

    if tags:
        return [t["name"] for t in tags[:5]]

    # 2️⃣ Artist-Tags (Fallback)
    data = lastfm_request({
        "method": "artist.getTopTags",
        "artist": artist,
        "autocorrect": 1
    })

    tags = data.get("toptags", {}).get("tag", [])
    return [t["name"] for t in tags[:5]]

# --------------------------------------------------
# Cover (Last.fm)
# --------------------------------------------------
def get_cover_from_lastfm(title: str, artist: str) -> str | None:
    data = lastfm_request({
        "method": "track.getInfo",
        "track": title,
        "artist": artist,
        "autocorrect": 1
    })

    album = data.get("track", {}).get("album", {})
    images = album.get("image", [])

    if images:
        url = images[-1].get("#text")
        if url:
            return url

    # Fallback: Artist Image
    data = lastfm_request({
        "method": "artist.getInfo",
        "artist": artist,
        "autocorrect": 1
    })

    images = data.get("artist", {}).get("image", [])
    if images:
        return images[-1].get("#text")

    return None
