import streamlit as st
from songfinder_api import (
    recognize_song_from_file,
    recognize_song_from_url,
    api_key_available,
    get_similar_songs_by_artist,
    get_similar_songs_by_genre
)

st.set_page_config(
    page_title="🎵 Song-Erkennung",
    layout="centered"
)

st.title("🎵 Song-Erkennungs-App")
st.write("Erkennt Songs und ermittelt Genre-Tags aus einer offenen Musikdatenbank.")

# API-Key prüfen
if not api_key_available():
    st.error(
        "❌ Kein API-Key gefunden.\n\n"
        "Bitte setze die Umgebungsvariable `AUDD_API_KEY` "
        "(z. B. über Streamlit Secrets)."
    )
    st.stop()

st.divider()

eingabe = st.radio(
    "Eingabemethode auswählen:",
    ("Audiodatei hochladen", "Audio-URL eingeben")
)

ergebnis = None

if eingabe == "Audiodatei hochladen":
    datei = st.file_uploader(
        "Audiodatei auswählen (MP3 oder WAV)",
        type=["mp3", "wav"]
    )

    if datei:
        with st.spinner("🎧 Song wird erkannt..."):
            ergebnis = recognize_song_from_file(datei)

elif eingabe == "Audio-URL eingeben":
    url = st.text_input("Audio-URL eingeben")

    if url:
        with st.spinner("🌐 Song wird erkannt..."):
            ergebnis = recognize_song_from_url(url)

# -----------------------------
# Ergebnisanzeige
# -----------------------------
if ergebnis:
    st.success("✅ Song erkannt!")

    st.subheader("🎶 Erkannte Informationen")
    st.write(f"**Titel:** {ergebnis.get('title', 'Unbekannt')}")
    st.write(f"**Künstler:** {ergebnis.get('artist', 'Unbekannt')}")
    st.write(f"**Album:** {ergebnis.get('album', 'Unbekannt')}")

    genres = ergebnis.get("genre", [])
    if genres:
        st.write("**Genres:**")
        st.markdown(" • " + " • ".join(genres))
    else:
        st.write("**Genres:** Unbekannt")

    if ergebnis.get("cover"):
        st.image(ergebnis["cover"], caption="Coverbild")

elif ergebnis is None and (
    (eingabe == "Audiodatei hochladen" and "datei" in locals() and datei)
    or (eingabe == "Audio-URL eingeben" and "url" in locals() and url)
):
    st.error("❌ Kein Song erkannt.")

# =========================================================
# Empfehlungen
# =========================================================
if ergebnis:
    st.divider()
    st.subheader("🎧 Empfohlene Songs")

    # --- Gleicher Künstler ---
    st.write("**🎤 Weitere Songs vom Künstler:**")
    artist_songs = get_similar_songs_by_artist(
        artist=ergebnis["artist"],
        exclude_title=ergebnis["title"]
    )

    if artist_songs:
        for song in artist_songs:
            st.markdown(f"- {song}")
    else:
        st.write("Keine weiteren Songs gefunden.")

    # --- Ähnliches Genre ---
    st.write("**🏷️ Songs mit ähnlichem Genre:**")
    genre_songs = get_similar_songs_by_genre(ergebnis.get("genre", []))

    if genre_songs:
        for song in genre_songs:
            st.markdown(f"- {song}")
    else:
        st.write("Keine genreähnlichen Songs gefunden.")
