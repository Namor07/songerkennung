import streamlit as st
from songfinder_api import (
    recognize_song_from_file,
    recognize_song_from_url,
    api_key_available
)

st.set_page_config(
    page_title="🎵 Song-Erkennung",
    layout="centered"
)

st.title("🎵 Song-Erkennungs-App")
st.write(
    "Diese App erkennt Songs mithilfe einer KI-gestützten Musikerkennungs-API."
)

# API-Key prüfen
if not api_key_available():
    st.error(
        "❌ Kein API-Key gefunden.\n\n"
        "Bitte hinterlege den API-Key als Umgebungsvariable "
        "`AUDD_API_KEY` (z. B. über Streamlit Secrets)."
    )
    st.stop()

st.divider()

eingabe = st.radio(
    "Eingabemethode auswählen:",
    ("Audiodatei hochladen", "Audio-URL eingeben")
)

ergebnis = None

# --- Datei-Upload ---
if eingabe == "Audiodatei hochladen":
    datei = st.file_uploader(
        "Audiodatei auswählen (MP3 oder WAV)",
        type=["mp3", "wav"]
    )

    if datei:
        with st.spinner("🎧 Song wird erkannt..."):
            ergebnis = recognize_song_from_file(datei)

# --- URL-Eingabe ---
elif eingabe == "Audio-URL eingeben":
    url = st.text_input("Audio-URL eingeben")

    if url:
        with st.spinner("🌐 Song wird erkannt..."):
            ergebnis = recognize_song_from_url(url)

# --- Ergebnis anzeigen ---
if ergebnis:
    st.success("✅ Song erfolgreich erkannt!")

    st.subheader("🎶 Erkannte Informationen")
    st.write(f"**Titel:** {ergebnis.get('title', 'Unbekannt')}")
    st.write(f"**Künstler:** {ergebnis.get('artist', 'Unbekannt')}")
    st.write(f"**Album:** {ergebnis.get('album', 'Unbekannt')}")
    st.write(f"**Genre:** {ergebnis.get('genre', 'Unbekannt')}")

    if ergebnis.get("cover"):
        st.image(ergebnis["cover"], caption="Coverbild")

elif ergebnis is None and (
    (eingabe == "Audiodatei hochladen" and "datei" in locals() and datei)
    or (eingabe == "Audio-URL eingeben" and "url" in locals() and url)
):
    st.error("❌ Kein Song erkannt.")
