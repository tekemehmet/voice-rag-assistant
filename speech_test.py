
import streamlit as st

from app.speech.speech_to_text import SpeechToText

st.set_page_config(
    page_title="Speech-to-Text Test",
    page_icon="🎙️",
)

st.title("🎙️ Speech-to-Text Test")
st.caption("Record a question and convert it into text.")

try:
    speech_service = SpeechToText()
except Exception as error:
    st.error(f"Speech configuration error: {error}")
    st.stop()

audio = st.audio_input("Record your question")

if audio:
    st.audio(audio)

    if st.button("Convert to Text"):
        with st.spinner("Recognizing speech..."):
            try:
                transcript = speech_service.transcribe(audio.getvalue())

                if transcript:
                    st.success("Speech recognized successfully!")
                    st.write("### Recognized Text")
                    st.write(transcript)
                else:
                    st.warning("No speech was recognized.")

            except Exception as error:
                st.error(f"Speech recognition failed: {error}")
