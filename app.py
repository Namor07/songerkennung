import random
import streamlit as st
from songfinder_api import (
    recognize_song,
    get_recommendations_by_artist,
    get_recommendations_by_genre
)

st.set_page_config(
    page_title="Song-Erkennung",
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
    max-width: 680px;          /* schmaler */
    margin: 0 auto 40px auto;  /* weniger Abstand */
    padding: 50px 34px;        /* kompakter */
    border-radius: 24px;
    color: white;
}

.section-heading {
    max-width: 680px;
    margin: 60px auto 16px auto;
    font-size: 28px;
    font-weight: 800;
}

.wrapped-title {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 8px;
}

.wrapped-subtitle {
    font-size: 20px;
    opacity: 0.95;
}

.song-meta {
    font-size: 18px;
    margin-top: 6px;
}

.wrapped-cover {
    max-width: 220px;
    border-radius: 16px;
    margin-top: 20px;
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
# ==================================================
# ZENTRIERTER HEADER / INPUT (schmal)
# ==================================================
st.markdown("""
<style>
.center-box h1 {
    font-size: 56px;   /* größer, aber nicht kitschig */
    font-weight: 900;
    margin-bottom: 10px;
    text-align: center;
}

.center-box p {
    font-size: 22px;
    opacity: 0.95;
    line-height: 1.4;
    text-align: center;
}

.upload-box {
    max-width: 420px;
    margin: 0 auto;
}

.small-button button {
    padding: 6px 18px;
    font-size: 16px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="center-box">
    <h1>🎧 Song-Erkennung</h1>
    <p>
        Lade einen Song hoch, lasse diesen erkennen und erhalte
        dein persönliches Musik-Wrapped. 🔥
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Upload schmal + Button klein
# -----------------------------
col1, col2, col3 = st.columns([1, 1.4, 1])

with col2:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Audiodatei hochladen (MP3 oder WAV)",
        type=["mp3", "wav"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

    recognize_clicked = st.button("🎶 Song erkennen")

    st.markdown(
        "<style>.stButton>button {margin-top: 10px;}</style>",
        unsafe_allow_html=True
    )

# ==================================================
# Song erkennen
# ==================================================
if recognize_clicked:
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
        "<div class='section-heading'>🎸 Weitere Songs vom Künstler</div>",
        unsafe_allow_html=True
    )
    TARGET_COUNT = 6
    artist_recs = get_recommendations_by_artist(result["artist"])    
    seen_songs = set()

    filtered_artist_songs = []

    for song in artist_recs:
        key = f"{song['artist']} - {song['title']}"
    
        if key in seen_songs:
            continue
    
        seen_songs.add(key)
        filtered_artist_songs.append(song)
    
        if len(filtered_artist_songs) == TARGET_COUNT:
            break
            
        for song in filtered_artist_songs:
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

    TARGET_COUNT = 6
    genre_recs = get_recommendations_by_genre(result.get("genre", []))

    filtered_genre_songs = []

    for song in genre_recs:
        key = f"{song['artist']} - {song['title']}"
    
        if key in seen_songs:
            continue
    
        seen_songs.add(key)
        filtered_genre_songs.append(song)
    
        if len(filtered_genre_songs) == TARGET_COUNT:
            break
        
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
