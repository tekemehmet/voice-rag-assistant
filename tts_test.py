
import streamlit as st

from app.speech.text_to_speech import TextToSpeech

st.set_page_config(
    page_title="Text-to-Speech Test",
    page_icon="🔊",
)

st.title("🔊 Text-to-Speech Test")
st.caption("Convert text into spoken English.")

try:
    speech_service = TextToSpeech()
except Exception as error:
    st.error(f"Speech configuration error: {error}")
    st.stop()

text = st.text_area(
    "Enter text to speak",
    value="Hello! Welcome to your Voice RAG Assistant. "
          "I can answer questions about your documents.",
    height=150,
)

if st.button("Generate Speech"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating speech..."):
            try:
                audio_bytes = speech_service.synthesize(text)

                if audio_bytes:
                    st.success("Speech generated successfully!")
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error("No audio was generated.")

            except Exception as error:
                st.error(f"Text-to-Speech failed: {error}")
