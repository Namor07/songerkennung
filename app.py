import streamlit as st
from songfinder_api import recognize_song

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
            result = recognize_song(uploaded_file)

        if not result:
            st.error("Song konnte nicht erkannt werden.")
        else:
            st.success("Song erkannt!")
            st.subheader("🎶 Erkannter Song")
            show_song_card(result)import streamlit as st
from songfinder_api import recognize_song

st.set_page_config(page_title="Song-Erkennung", page_icon="🎵")
st.title("🎵 Song-Erkennung")
st.write("Lade eine Audiodatei hoch oder gib eine Audio- oder YouTube-URL ein.")

uploaded_file = st.file_uploader(
    "Audiodatei hochladen (MP3 oder WAV)",
    type=["mp3", "wav"]
)

audio_url = st.text_input(
    "Oder Audio- / YouTube-URL eingeben"
)

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

if st.button("Song erkennen"):
    with st.spinner("Song wird erkannt …"):
        result = recognize_song(uploaded_file, audio_url)

    if not result:
        st.error("Song konnte nicht erkannt werden.")
    else:
        st.success("Song erkannt!")
        st.subheader("🎶 Erkannter Song")
        show_song_card(result)
