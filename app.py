import streamlit as st
from songfinder_api import (
    recognize_song,
    get_recommendations_by_artist,
    get_recommendations_by_genre
)

st.set_page_config(page_title="Song-Erkennung", page_icon="🎵")

# --------------------------------------------------
# Spotify-ähnliches CSS
# --------------------------------------------------
st.markdown("""
<style>
.song-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 20px;
}

.song-card {
    background-color: #181818;
    border-radius: 12px;
    padding: 12px;
    transition: background-color 0.2s;
}

.song-card:hover {
    background-color: #282828;
}

.song-cover {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 10px;
}

.song-title {
    font-weight: 700;
    font-size: 14px;
    color: white;
}

.song-artist {
    font-size: 13px;
    color: #b3b3b3;
}

.song-album {
    font-size: 12px;
    color: #777;
}

.genre-badge {
    display: inline-block;
    margin-top: 6px;
    padding: 2px 8px;
    font-size: 11px;
    border-radius: 999px;
    background-color: #1db954;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🎵 Song-Erkennung")
st.write("Lade eine Audiodatei hoch, um den Song zu erkennen.")

uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

# --------------------------------------------------
# UI Helper
# --------------------------------------------------
def show_spotify_card(song: dict):
    cover = song.get("cover") or "https://via.placeholder.com/300?text=No+Cover"
    title = song.get("title", "Unbekannt")
    artist = song.get("artist", "Unbekannt")
    album = song.get("album", "Unbekannt")
    genres = song.get("genre", [])

    genre_html = ""
    if genres:
        genre_html = f'<div class="genre-badge">{genres[0]}</div>'

    st.markdown(f"""
    <div class="song-card">
        <img src="{cover}" class="song-cover">
        <div class="song-title">{title}</div>
        <div class="song-artist">{artist}</div>
        <div class="song-album">{album}</div>
        {genre_html}
    </div>
    """, unsafe_allow_html=True)


def show_song_grid(songs: list[dict]):
    st.markdown('<div class="song-grid">', unsafe_allow_html=True)
    for song in songs:
        show_spotify_card(song)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Song erkennen
# --------------------------------------------------
if st.button("Song erkennen"):
    if not uploaded_file:
        st.warning("Bitte zuerst eine Audiodatei hochladen.")
    else:
        with st.spinner("Song wird erkannt …"):
            st.session_state.result = recognize_song(uploaded_file)

        if not st.session_state.result:
            st.error("Song konnte nicht erkannt werden.")

# --------------------------------------------------
# Ergebnis + Empfehlungen
# --------------------------------------------------
result = st.session_state.result

if result:
    st.subheader("🎶 Erkannter Song")
    show_song_grid([result])

    st.divider()
    st.subheader("🎧 Song-Empfehlungen")

    # Gleicher Künstler
    st.write("### 🎤 Weitere bekannte Songs vom Künstler")
    artist_recs = get_recommendations_by_artist(result["artist"])
    if artist_recs:
        show_song_grid(artist_recs)
    else:
        st.write("Keine Empfehlungen gefunden.")

    # Gleiches Genre
    st.write("### 🏷️ Beliebte Songs aus ähnlichem Genre")
    genre_recs = get_recommendations_by_genre(result.get("genre", []))
    if genre_recs:
        show_song_grid(genre_recs)
    else:
        st.write("Keine Empfehlungen gefunden.")
