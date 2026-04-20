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
MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"
MUSICBRAINZ_HEADERS = {
    "User-Agent": "SongErkennungSchulprojekt/1.0 (schule@example.de)"
}


def api_key_available() -> bool:
    return AUDD_API_KEY is not None and AUDD_API_KEY.strip() != ""


# =========================================================
# Öffentliche Funktionen
# =========================================================
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


# =========================================================
# AudD → MusicBrainz Auswertung
# =========================================================
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

    # 🎯 Genre-Fallback-Logik
    genres = _get_genres_with_fallback(title, artist, album)

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "genre": genres,
        "cover": cover_url
    }


# =========================================================
# MusicBrainz Genre-Logik
# =========================================================
def _get_genres_with_fallback(title: str, artist: str, album: str) -> list[str]:
    """
    1. Recording-Tags
    2. Album-Tags (Release Group)
    3. Artist-Tags
    """
    genres = _get_recording_genres(title, artist)
    if genres:
        return genres

    genres = _get_album_genres(album, artist)
    if genres:
        return genres

    genres = _get_artist_genres(artist)
    return genres


def _get_recording_genres(title: str, artist: str) -> list[str]:
    return _search_musicbrainz(
        endpoint="recording",
        query=f'recording:"{title}" AND artist:"{artist}"'
    )


def _get_album_genres(album: str, artist: str) -> list[str]:
    return _search_musicbrainz(
        endpoint="release-group",
        query=f'releasegroup:"{album}" AND artist:"{artist}"'
    )


def _get_artist_genres(artist: str) -> list[str]:
    return _search_musicbrainz(
        endpoint="artist",
        query=f'artist:"{artist}"'
    )


def _search_musicbrainz(endpoint: str, query: str) -> list[str]:
    """
    Allgemeine Suche nach Tags bei MusicBrainz
    """
    if not query:
        return []

    url = f"{MUSICBRAINZ_BASE_URL}/{endpoint}"
    params = {
        "query": query,
        "fmt": "json",
        "limit": 1
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=MUSICBRAINZ_HEADERS,
            timeout=10
        )
        data = response.json()
    except Exception:
        return []

    key = f"{endpoint}s"
    results = data.get(key, [])
    if not results:
        return []

    tags = results[0].get("tags", [])
    return [tag["name"].title() for tag in tags]
