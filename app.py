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
    padding: 80px 40px;
    border-radius: 24px;
    margin-bottom: 60px;
    color: white;
}

.bg-purple {
    background: linear-gradient(135deg, #7f00ff, #e100ff);
}

.bg-green {
    background: linear-gradient(135deg, #1db954, #1ed760);
    color: black;
}

.bg-orange {
    background: linear-gradient(135deg, #ff512f, #dd2476);
}

.wrapped-title {
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 10px;
}

.wrapped-subtitle {
    font-size: 22px;
    opacity: 0.9;
}

.wrapped-cover {
    max-width: 320px;
    border-radius: 16px;
    margin-top: 30px;
}

.wrapped-list {
    font-size: 22px;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

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
    # ----------------------------
    # Story 1 – Erkannter Song
    # ----------------------------
    st.markdown(f"""
    <div class="wrapped-section bg-purple">
        <div class="wrapped-title">Du hast gehört:</div>
        <div class="wrapped-subtitle">
            {result["title"]} – {result["artist"]}
        </div>
        <div class="wrapped-subtitle">
            Album: {result.get("album", "Unbekannt")}
        </div>
        <div class="wrapped-subtitle">
            Genre: {", ".join(result.get("genre", [])) or "Unbekannt"}
        </div>
        {"<img src='" + result["cover"] + "' class='wrapped-cover'>" if result.get("cover") else ""}
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Story 2 – Künstler-Vibe
    # ----------------------------
    artist_recs = get_recommendations_by_artist(result["artist"])

    if artist_recs:
        song_list = "<br>".join(
            f"• {s['title']}" for s in artist_recs[:5]
        )

        st.markdown(f"""
        <div class="wrapped-section bg-green">
            <div class="wrapped-title">Mehr von {result["artist"]}</div>
            <div class="wrapped-list">{song_list}</div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------
    # Story 3 – Genre-Vibe
    # ----------------------------
    genre_recs = get_recommendations_by_genre(result.get("genre", []))

    if genre_recs and result.get("genre"):
        song_list = "<br>".join(
            f"• {s['title']} – {s['artist']}"
            for s in genre_recs[:5]
        )

        st.markdown(f"""
        <div class="wrapped-section bg-orange">
            <div class="wrapped-title">
                Dein {result["genre"][0]}-Vibe
            </div>
            <div class="wrapped-list">{song_list}</div>
        </div>
        """, unsafe_allow_html=True)
