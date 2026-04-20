import streamlit as st
from songfinder_api import (
    recognize_song,
    get_recommended_songs_by_artist_mb,
    get_recommended_songs_by_genre_mb
)

st.set_page_config(page_title="Song-Erkennung", page_icon="🎵")

st.title("🎵 Song-Erkennung mit KI")
st.write("Lade eine Audiodatei hoch oder gib eine Audio- oder YouTube-URL ein.")

# ---------------------------
# Eingabe
# ---------------------------
uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

audio_url = st.text_input(
    "Oder Audio-/YouTube-URL eingeben"
)

# ---------------------------
# Song erkennen
# ---------------------------
if st.button("Song erkennen"):
    with st.spinner("Song wird erkannt..."):
        result = recognize_song(uploaded_file, audio_url)

    if not result:
        st.error("Song konnte nicht erkannt werden.")
    else:
        st.success("Song erkannt!")

        # ---------------------------
        # Erkannter Song
        # ---------------------------
        st.subheader("🎶 Erkannter Song")
        show_song_card = lambda song: (
            st.container(border=True)
        )

        with st.container(border=True):
            col1, col2 = st.columns([1, 3])

            if result.get("cover"):
                col1.image(result["cover"], width=120)

            col2.write(f"**Titel:** {result.get('title')}")
            col2.write(f"**Künstler:** {result.get('artist')}")
            col2.write(f"**Album:** {result.get('album')}")
            col2.write(
                f"**Genre:** {', '.join(result.get('genre', [])) or 'Unbekannt'}"
            )

        # ---------------------------
        # Empfehlungen
        # ---------------------------
        st.divider()
        st.subheader("🎧 Song-Empfehlungen")

        # Künstler
        st.write("### 🎤 Weitere Songs vom Künstler")
        artist_recs = get_recommended_songs_by_artist_mb(result["artist"])
        if artist_recs:
            for song in artist_recs:
                show_song(song := song)
        else:
            st.write("Keine Empfehlungen gefunden.")

        # Genre
        st.write("### 🏷️ Songs mit ähnlichem Genre")
        genre_recs = get_recommended_songs_by_genre_mb(result.get("genre", []))
        if genre_recs:
            for song in genre_recs:
                show_song(song := song)
        else:
            st.write("Keine Empfehlungen gefunden.")


def show_song(song: dict):
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])

        if song.get("cover"):
            col1.image(song["cover"], width=120)

        col2.write(f"**Titel:** {song.get('title', 'Unbekannt')}")
        col2.write(f"**Künstler:** {song.get('artist', 'Unbekannt')}")
        col2.write(f"**Album:** {song.get('album', 'Unbekannt')}")
