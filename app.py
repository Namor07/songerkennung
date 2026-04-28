import random
import streamlit as st
from songfinder_api import (
    recognize_song,
    get_recommendations_by_artist,
    get_recommendations_by_genre
)

st.set_page_config(
    page_title="Song Wrapped",
    page_icon="🎧",
    layout="wide"
)

# ==================================================
# CSS – Spotify Wrapped Style (zentriert & begrenzt)
# ==================================================
st.markdown(
"""
<style>
.wrapped-section {
    max-width: 760px;
    margin: 0 auto 60px auto;
    padding: 70px 40px;
    border-radius: 28px;
    color: white;
}

.section-heading {
    max-width: 760px;
    margin: 80px auto 20px auto;
    font-size: 32px;
    font-weight: 800;
}

.wrapped-title {
    font-size: 44px;
    font-weight: 800;
    margin-bottom: 12px;
}

.wrapped-subtitle {
    font-size: 22px;
    opacity: 0.95;
}

.song-meta {
    font-size: 20px;
    margin-top: 10px;
}

.wrapped-cover {
    max-width: 260px;
    border-radius: 18px;
    margin-top: 25px;
}
</style>
""",
unsafe_allow_html=True
)

# ==================================================
# Farben (Wrapped-Feeling)
# ==================================================
GRADIENTS = [
    "linear-gradient(135deg, #7f00ff, #e100ff)",
    "linear-gradient(135deg, #1db954, #1ed760)",
    "linear-gradient(135deg, #ff512f, #dd2476)",
    "linear-gradient(135deg, #396afc, #2948ff)",
    "linear-gradient(135deg, #ffb347, #ffcc33)",
]

def random_bg():
    return random.choice(GRADIENTS)

# ==================================================
# Session State
# ==================================================
if "result" not in st.session_state:
    st.session_state.result = None

# ==================================================
# UI
# ==================================================
st.title("🎧 Dein Song Wrapped")
st.write("Lade eine Audiodatei hoch und erhalte dein persönliches Musik-Wrapped.")

uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

# ==================================================
# Song erkennen
# ==================================================
if st.button("Wrapped erstellen"):
    if not uploaded_file:
        st.warning("Bitte zuerst eine Audiodatei hochladen.")
    else:
        with st.spinner("Dein Wrapped wird erstellt …"):
            st.session_state.result = recognize_song(uploaded_file)

        if not st.session_state.result:
            st.error("Song konnte nicht erkannt werden.")

# ==================================================
# Wrapped anzeigen
# ==================================================
result = st.session_state.result

if result:

    # ----------------------------------------------
    # STORY 1 – ERKANNTER SONG
    # ----------------------------------------------
    st.markdown(
f"""
<div class="wrapped-section" style="background:{random_bg()}">
    <div class="wrapped-title">Du hast gehört</div>
    <div class="wrapped-subtitle">{result["title"]} – {result["artist"]}</div>
    <div class="song-meta">🎵 Album: {result.get("album", "Unbekannt")}</div>
    <div class="song-meta">🎧 Genre: {", ".join(result.get("genre", [])) or "Unbekannt"}</div>
    {f"<img src='{result['cover']}' class='wrapped-cover'>" if result.get("cover") else ""}
</div>
""",
unsafe_allow_html=True
    )

    # ----------------------------------------------
    # ÜBERSCHRIFT: Künstler
    # ----------------------------------------------
    st.markdown(
        "<div class='section-heading'>🔥 Weitere Songs vom Künstler</div>",
        unsafe_allow_html=True
    )

    artist_recs = get_recommendations_by_artist(result["artist"])

    for song in artist_recs:
        st.markdown(
f"""
<div class="wrapped-section" style="background:{random_bg()}">
    <div class="wrapped-title">{song["title"]}</div>
    <div class="wrapped-subtitle">{song["artist"]}</div>
    <div class="song-meta">🎵 Album: {song.get("album", "Unbekannt")}</div>
    {f"<img src='{song['cover']}' class='wrapped-cover'>" if song.get("cover") else ""}
</div>
""",
unsafe_allow_html=True
        )

    # ----------------------------------------------
    # ÜBERSCHRIFT: Genre
    # ----------------------------------------------
    st.markdown(
        "<div class='section-heading'>🎧 Empfehlungen aus dem gleichen Genre</div>",
        unsafe_allow_html=True
    )

    genre_recs = get_recommendations_by_genre(result.get("genre", []))

    for song in genre_recs:
        st.markdown(
f"""
<div class="wrapped-section" style="background:{random_bg()}">
    <div class="wrapped-title">{song["title"]}</div>
    <div class="wrapped-subtitle">{song["artist"]}</div>
    <div class="song-meta">🎵 Album: {song.get("album", "Unbekannt")}</div>
    {f"<img src='{song['cover']}' class='wrapped-cover'>" if song.get("cover") else ""}
</div>
""",
unsafe_allow_html=True
        )
