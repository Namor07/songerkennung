import streamlit as st
from songfinder_api import (
    recognize_song,
    get_recommendations_by_artist,
    get_recommendations_by_genre
)

if "result" not in st.session_state:
    st.session_state.result = None
    
st.set_page_config(page_title="Song-Erkennung", page_icon="🎵")

st.title("🎵 Song-Erkennung")
st.write("Lade eine Audiodatei hoch, um den Song zu erkennen.")

# ---------------------------
# Audio Upload
# ---------------------------
uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

# ---------------------------
# Anzeige-Helfer
# ---------------------------
def show_song_card(song: dict):
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])

        if song.get("cover"):
            col1.image(song["cover"], width=120)

        col2.write(f"**Titel:** {song.get('title', 'Unbekannt')}")
        col2.write(f"**Künstler:** {song.get('artist', 'Unbekannt')}")
        col2.write(f"**Album:** {song.get('album', 'Unbekannt')}")
        col2.write(
            f"**Genre:** {', '.join(song.get('genre', [])) or 'Unbekannt'}"
        )

# ---------------------------
# Song erkennen
# ---------------------------
if st.button("Song erkennen"):
    if not uploaded_file:
        st.warning("Bitte zuerst eine Audiodatei hochladen.")
    else:
        with st.spinner("Song wird erkannt …"):
            st.session_state.result = recognize_song(uploaded_file)

        if not st.session_state.result:
            st.error("Song konnte nicht erkannt werden.")

result = st.session_state.result

if result:
    st.success("Song erkannt!")
    st.subheader("🎶 Erkannter Song")
    show_song_card(result)

    st.divider()
    st.subheader("🎧 Song-Empfehlungen")

    # 🎤 Gleicher Künstler
    st.write("### 🎤 Weitere bekannte Songs vom Künstler")
    artist_recs = get_recommendations_by_artist(result["artist"])

    if artist_recs:
        for song in artist_recs:
            show_song_card(song)
    else:
        st.write("Keine Empfehlungen gefunden.")

    # 🏷️ Gleiches Genre
    st.write("### 🏷️ Beliebte Songs aus ähnlichem Genre")
    genre_recs = get_recommendations_by_genre(result.get("genre", []))

    if genre_recs:
        for song in genre_recs:
            show_song_card(song)
    else:
        st.write("Keine Empfehlungen gefunden.")

#Song-Empfehlungen

st.divider()
st.subheader("🎧 Song-Empfehlungen")

# 🎤 Gleicher Künstler
st.write("### 🎤 Weitere bekannte Songs vom Künstler")
artist_recs = get_recommendations_by_artist(result["artist"])

if artist_recs:
    for song in artist_recs:
        show_song_card(song)
else:
    st.write("Keine Empfehlungen gefunden.")

# 🏷️ Gleiches Genre
st.write("### 🏷️ Beliebte Songs aus ähnlichem Genre")
genre_recs = get_recommendations_by_genre(result.get("genre", []))

if genre_recs:
    for song in genre_recs:
        show_song_card(song)
else:
    st.write("Keine Empfehlungen gefunden.")
