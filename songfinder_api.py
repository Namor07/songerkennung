import requests

AUDD_API_URL = "https://api.audd.io/"

# ---------------------------
# Song-Erkennung (AudD)
# ---------------------------
def recognize_song(uploaded_file, audio_url):
    data = {}

    if uploaded_file:
        files = {"file": uploaded_file}
    elif audio_url:
        data["url"] = audio_url
        files = None
    else:
        return None

    response = requests.post(AUDD_API_URL, data=data, files=files)
    result = response.json().get("result")

    if not result:
        return None

    title = result.get("title")
    artist = result.get("artist")
    album = result.get("album")

    genres = get_genres_from_musicbrainz(artist)
    cover = get_cover_from_musicbrainz(artist, album)

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "genre": genres,
        "cover": cover
    }

# ---------------------------
# MusicBrainz Genre
# ---------------------------
def get_genres_from_musicbrainz(artist):
    url = "https://musicbrainz.org/ws/2/artist"
    params = {
        "query": f'artist:"{artist}"',
        "fmt": "json",
        "limit": 1
    }

    r = requests.get(url, params=params)
    data = r.json()

    artists = data.get("artists", [])
    if not artists:
        return []

    tags = artists[0].get("tags", [])
    return [t["name"] for t in tags[:3]]

# ---------------------------
# Cover Art Archive
# ---------------------------
def get_cover_from_musicbrainz(artist, album):
    if not album:
        return None

    url = "https://musicbrainz.org/ws/2/release"
    params = {
        "query": f'release:"{album}" AND artist:"{artist}"',
        "fmt": "json",
        "limit": 1
    }

    r = requests.get(url, params=params)
    releases = r.json().get("releases", [])

    if not releases:
        return None

    release_id = releases[0]["id"]
    cover_url = f"https://coverartarchive.org/release/{release_id}"

    try:
        cover_data = requests.get(cover_url).json()
        return cover_data["images"][0]["image"]
    except Exception:
        return None

# ---------------------------
# Empfehlungen: Künstler
# ---------------------------
def get_recommended_songs_by_artist_mb(artist, limit=5):
    url = "https://musicbrainz.org/ws/2/recording"
    params = {
        "query": f'artist:"{artist}"',
        "fmt": "json",
        "limit": limit
    }

    r = requests.get(url, params=params)
    recordings = r.json().get("recordings", [])

    results = []
    for rec in recordings:
        releases = rec.get("releases", [])
        album = releases[0]["title"] if releases else None
        cover = get_cover_from_musicbrainz(artist, album)

        results.append({
            "title": rec.get("title"),
            "artist": artist,
            "album": album,
            "cover": cover
        })

    return results

# ---------------------------
# Empfehlungen: Genre
# ---------------------------
def get_recommended_songs_by_genre_mb(genres, limit=5):
    if not genres:
        return []

    genre = genres[0]

    url = "https://musicbrainz.org/ws/2/recording"
    params = {
        "query": f'tag:"{genre}"',
        "fmt": "json",
        "limit": limit
    }

    r = requests.get(url, params=params)
    recordings = r.json().get("recordings", [])

    results = []
    for rec in recordings:
        artist_credit = rec.get("artist-credit", [])
        artist = artist_credit[0]["name"] if artist_credit else None

        releases = rec.get("releases", [])
        album = releases[0]["title"] if releases else None
        cover = get_cover_from_musicbrainz(artist, album)

        results.append({
            "title": rec.get("title"),
            "artist": artist,
            "album": album,
            "cover": cover
        })

    return results
