import requests
import streamlit as st

AUDD_API_URL = "https://api.audd.io/"
LASTFM_API_KEY = st.secrets.get("LASTFM_API_KEY")

LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# --------------------------------------------------
# Last.fm Helper
# --------------------------------------------------
def lastfm_request(params: dict) -> dict:
    params["api_key"] = LASTFM_API_KEY
    params["format"] = "json"
    r = requests.get(LASTFM_BASE_URL, params=params, timeout=10)
    return r.json()

# --------------------------------------------------
# Song erkennen
# --------------------------------------------------
def recognize_song(uploaded_file):
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
# Genre
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
# Cover
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

# --------------------------------------------------
# Empfehlungen
# --------------------------------------------------
def get_song_details_from_lastfm(title: str, artist: str) -> dict | None:
    data = lastfm_request({
        "method": "track.getInfo",
        "track": title,
        "artist": artist,
        "autocorrect": 1
    })

    track = data.get("track")
    if not track:
        return None

    album = track.get("album", {})
    images = album.get("image", [])
    cover = images[-1].get("#text") if images else None

    return {
        "title": track.get("name"),
        "artist": track.get("artist", {}).get("name"),
        "album": album.get("title"),
        "cover": cover
    }

def get_recommendations_by_artist(artist: str, limit: int = 6) -> list[dict]:
    data = lastfm_request({
        "method": "artist.getTopTracks",
        "artist": artist,
        "limit": limit,
        "autocorrect": 1
    })

    tracks = data.get("toptracks", {}).get("track", [])
    recs = []

    for t in tracks:
        details = get_song_details_from_lastfm(t.get("name"), artist)
        if details:
            recs.append(details)

    return recs

def get_recommendations_by_genre(genres: list[str], limit: int = 6) -> list[dict]:
    if not genres:
        return []

    tag = genres[0]
    data = lastfm_request({
        "method": "tag.getTopTracks",
        "tag": tag,
        "limit": limit
    })

    tracks = data.get("tracks", {}).get("track", [])
    recs = []

    for t in tracks:
        artist = t.get("artist", {}).get("name")
        title = t.get("name")
        details = get_song_details_from_lastfm(title, artist)
        if details:
            recs.append(details)

    return recs
