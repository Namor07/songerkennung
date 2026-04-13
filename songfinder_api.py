import os
import requests

# -----------------------------
# AudD (Song-Erkennung)
# -----------------------------
AUDD_API_URL = "https://api.audd.io/"
AUDD_API_KEY = os.getenv("AUDD_API_KEY")

# -----------------------------
# MusicBrainz (Genres)
# -----------------------------
MUSICBRAINZ_SEARCH_URL = "https://musicbrainz.org/ws/2/recording/"
MUSICBRAINZ_HEADERS = {
    "User-Agent": "SongErkennungSchulprojekt/1.0 (kontakt@schule.de)"
}


def api_key_available() -> bool:
    return AUDD_API_KEY is not None and AUDD_API_KEY.strip() != ""


# -----------------------------
# Öffentliche Funktionen
# -----------------------------
def recognize_song_from_file(audio_file):
    files = {
        "file": (audio_file.name, audio_file, audio_file.type)
    }

    data = {
        "api_token": AUDD_API_KEY,
        "return": "spotify"
    }

    response = requests.post(
        AUDD_API_URL,
        data=data,
        files=files,
        timeout=30
    )

    return _parse_audd_response(response.json())


def recognize_song_from_url(audio_url: str):
    data = {
        "api_token": AUDD_API_KEY,
        "url": audio_url,
        "return": "spotify"
    }

    response = requests.post(
        AUDD_API_URL,
        data=data,
        timeout=30
    )

    return _parse_audd_response(response.json())


# -----------------------------
# Interne Helferfunktionen
# -----------------------------
def _parse_audd_response(api_response: dict):
    if api_response.get("status") != "success":
        return None

    result = api_response.get("result")
    if not result:
        return None

    title = result.get("title")
    artist = result.get("artist")
    album = result.get("album")

    # Cover (optional)
    cover_url = None
    spotify_data = result.get("spotify")
    if spotify_data:
        images = spotify_data.get("album", {}).get("images", [])
        if images:
            cover_url = images[0].get("url")

    # 🎯 Genres über MusicBrainz
    genres = _get_genres_from_musicbrainz(title, artist)

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "genre": genres,
        "cover": cover_url
    }


def _get_genres_from_musicbrainz(title: str, artist: str) -> list[str]:
    """
    Sucht nach Recording-Tags (Genres) bei MusicBrainz
    """
    if not title or not artist:
        return []

    params = {
        "query": f'recording:"{title}" AND artist:"{artist}"',
        "fmt": "json",
        "limit": 1
    }

    try:
        response = requests.get(
            MUSICBRAINZ_SEARCH_URL,
            params=params,
            headers=MUSICBRAINZ_HEADERS,
            timeout=10
        )
        data = response.json()
    except Exception:
        return []

    recordings = data.get("recordings", [])
    if not recordings:
        return []

    tags = recordings[0].get("tags", [])
    genres = [tag["name"].title() for tag in tags]

    return genres
