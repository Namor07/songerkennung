import os
import requests

API_URL = "https://api.audd.io/"
API_KEY = os.getenv("AUDD_API_KEY")


def api_key_available() -> bool:
    """
    Prüft, ob ein API-Key gesetzt ist
    """
    return API_KEY is not None and API_KEY.strip() != ""


def recognize_song_from_file(audio_file):
    """
    Erkennt einen Song anhand einer hochgeladenen Audiodatei
    """
    files = {
        "file": (audio_file.name, audio_file, audio_file.type)
    }

    data = {
        "api_token": API_KEY,
        "return": "spotify"
    }

    response = requests.post(API_URL, data=data, files=files, timeout=30)
    return _parse_response(response.json())


def recognize_song_from_url(audio_url: str):
    """
    Erkennt einen Song anhand einer Audio-URL
    """
    data = {
        "api_token": API_KEY,
        "url": audio_url,
        "return": "spotify"
    }

    response = requests.post(API_URL, data=data, timeout=30)
    return _parse_response(response.json())


def _parse_response(api_response: dict):
    """
    Bereitet die API-Antwort verständlich auf
    """
    if api_response.get("status") != "success":
        return None

    result = api_response.get("result")
    if not result:
        return None

    # --- Coverbild ---
    cover_url = None
    spotify_data = result.get("spotify")
    if spotify_data:
        images = spotify_data.get("album", {}).get("images", [])
        if images:
            cover_url = images[0].get("url")

    # --- Genre (über Spotify-Künstlerdaten) ---
    genres = []
    if spotify_data:
        artists = spotify_data.get("artists", [])
        if artists:
            genres = artists[0].get("genres", [])

    genre_text = ", ".join(genres) if genres else "Unbekannt"

    return {
        "title": result.get("title"),
        "artist": result.get("artist"),
        "album": result.get("album"),
        "genre": genre_text,
        "cover": cover_url
    }
