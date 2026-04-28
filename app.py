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

# --------------------------------------------------
# Wrapped-Style CSS
# --------------------------------------------------
st.markdown("""
<style>
.wrapped-section {
    padding: 70px 40px;
    border-radius: 28px;
    margin-bottom: 50px;
    color: white;
}

.wrapped-title {
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 10px;
}

.wrapped-subtitle {
    font-size: 22px;
    opacity: 0.95;
}

.wrapped-cover {
    max-width: 280px;
    border-radius: 18px;
    margin-top: 25px;
}

.song-meta {
    font-size: 20px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Farbverläufe (Spotify-Wrapped-Feeling)
# --------------------------------------------------
GRADIENTS = [
    "linear-gradient(135deg, #7f00ff, #e100ff)",
    "linear-gradient(135deg, #1db954, #1ed760)",
    "linear-gradient(135deg, #ff512f, #dd2476)",
    "linear-gradient(135deg, #396afc, #2948ff)",
    "linear-gradient(135deg, #ffb347, #ffcc33)",
]

def random_bg():
    return random.choice(GRADIENTS)

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("🎧 Dein Song Wrapped")
st.write("Lade eine Audiodatei hoch und erhalte dein persönliches Musik-Wrapped.")

uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

# --------------------------------------------------
# Song erkennen
# --------------------------------------------------
if st.button("Wrapped erstellen"):
    if not uploaded_file:
        st.warning("Bitte zuerst eine Audiodatei hochladen.")
    else:
        with st.spinner("Dein Wrapped wird erstellt …"):
            st.session_state.result = recognize_song(uploaded_file)

        if not st.session_state.result:
            st.error("Song konnte nicht erkannt werden.")

# --------------------------------------------------
# Wrapped anzeigen
# --------------------------------------------------
result = st.session_state.result

if result:
    # ==================================================
    # STORY 1 – ERKANNTER SONG
    # ==================================================
    st.markdown(f"""
    <div class="wrapped-section" style="background:{random_bg()}">
        <div class="wrapped-title">Du hast gehört</div>
        <div class="wrapped-subtitle">
            {result["title"]} – {result["artist"]}
        </div>

        <div class="song-meta">🎵 Album: {result.get("album", "Unbekannt")}</div>
        <div class="song-meta">
            🎧 Genre: {", ".join(result.get("genre", [])) or "Unbekannt"}
        </div>

        {"<img src='" + result["cover"] + "' class='wrapped-cover'>" if result.get("cover") else ""}
    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # STORY 2 – SONGS VOM KÜNSTLER
    # ==================================================
    artist_recs = get_recommendations_by_artist(result["artist"])

    if artist_recs:
        st.subheader("🔥 Mehr Songs von diesem Künstler")

        for song in artist_recs:
            st.markdown(f"""
            <div class="wrapped-section" style="background:{random_bg()}">
                <div class="wrapped-title">{song["title"]}</div>
                <div class="wrapped-subtitle">{song["artist"]}</div>

                <div class="song-meta">🎵 Album: {song.get("album", "Unbekannt")}</div>

                {"<img src='" + song["cover"] + "' class='wrapped-cover'>" if song.get("cover") else ""}
            </div>
            """, unsafe_allow_html=True)

    # ==================================================
    # STORY 3 – SONGS AUS GLEICHEM GENRE
    # ==================================================
    genre_recs = get_recommendations_by_genre(result.get("genre", []))

    if genre_recs:
        st.subheader("🎧 Dein Genre-Vibe")

        for song in genre_recs:
            st.markdown(f"""
            <div class="wrapped-section" style="background:{random_bg()}">
                <div class="wrapped-title">{song["title"]}</div>
                <div class="wrapped-subtitle">{song["artist"]}</div>

                <div class="song-meta">🎵 Album: {song.get("album", "Unbekannt")}</div>

                {"<img src='" + song["cover"] + "' class='wrapped-cover'>" if song.get("cover") else ""}
            </div>
            """, unsafe_allow_html=True)
