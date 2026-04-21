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
# Song-Erkennung (nur Audio-Datei)
# --------------------------------------------------
def recognize_song(uploaded_file):
    if not uploaded_file:
        return None

    try:
        r = requests.post(
            AUDD_API_URL,
            files={"file": uploaded_file},
            timeout=20
        )
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
# Last.fm Helper
# --------------------------------------------------
def lastfm_request(params: dict) -> dict:
    params["api_key"] = LASTFM_API_KEY
    params["format"] = "json"

    r = requests.get(LASTFM_BASE_URL, params=params, timeout=10)
    return r.json()

# --------------------------------------------------
# Genre (Track → Artist Fallback)
# --------------------------------------------------
def get_genres_from_lastfm(title: str, artist: str) -> list[str]:
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

    data = lastfm_request({
        "method": "artist.getTopTags",
        "artist": artist,
        "autocorrect": 1
    })

    tags = data.get("toptags", {}).get("tag", [])
    return [t["name"] for t in tags[:5]]

# --------------------------------------------------
# Cover (Album → Artist Fallback)
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

    data = lastfm_request({
        "method": "artist.getInfo",
        "artist": artist,
        "autocorrect": 1
    })

    images = data.get("artist", {}).get("image", [])
    if images:
        return images[-1].get("#text")

    return None
