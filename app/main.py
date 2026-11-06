
import streamlit as st

from app.rag.foundry_agent import FoundryAgent
from app.speech.speech_to_text import SpeechToText
from app.speech.text_to_speech import TextToSpeech


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Voice RAG Assistant",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Voice RAG Assistant")
st.caption("Ask questions about your uploaded PDF documents using text or voice.")


# --------------------------------------------------
# Session state initialization
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "agent" not in st.session_state:
    st.session_state.agent = None

if "speech_service" not in st.session_state:
    st.session_state.speech_service = None

if "tts_service" not in st.session_state:
    st.session_state.tts_service = None


# --------------------------------------------------
# Initialize services
# --------------------------------------------------

try:
    if st.session_state.agent is None:
        st.session_state.agent = FoundryAgent()
        st.session_state.conversation_id = (
            st.session_state.agent.create_conversation()
        )

    if st.session_state.speech_service is None:
        st.session_state.speech_service = SpeechToText()

    if st.session_state.tts_service is None:
        st.session_state.tts_service = TextToSpeech()

except Exception as error:
    st.error(f"Could not initialize services: {error}")
    st.stop()


# --------------------------------------------------
# Voice response setting
# --------------------------------------------------

speak_answers = st.toggle(
    "Read answers aloud",
    value=True,
    help="Automatically generate audio for assistant responses.",
)


# --------------------------------------------------
# Display conversation history
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Replay previously generated audio if available.
        if message["role"] == "assistant" and message.get("audio"):
            st.audio(message["audio"], format="audio/mp3")


# --------------------------------------------------
# Process user question
# --------------------------------------------------

def process_question(question: str):

    if not question or not question.strip():
        return

    question = question.strip()

    # Display and store user question.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate RAG answer.
    with st.chat_message("assistant"):

        try:
            with st.spinner("Searching documents and generating answer..."):

                answer = st.session_state.agent.ask(
                    st.session_state.conversation_id,
                    question,
                )

            st.markdown(answer)

            audio_bytes = None

            # Generate spoken answer when enabled.
            if speak_answers:

                with st.spinner("Generating spoken response..."):

                    audio_bytes = (
                        st.session_state.tts_service.synthesize(answer)
                    )

                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")

            # Store assistant response.
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "audio": audio_bytes,
                }
            )

        except Exception as error:
            st.error(f"Error processing your question: {error}")


# --------------------------------------------------
# Text input
# --------------------------------------------------

question = st.chat_input(
    "Type your question about your documents..."
)


# --------------------------------------------------
# Voice input
# --------------------------------------------------

st.divider()

st.subheader("🎙️ Ask using your voice")

audio_input = st.audio_input("Record your question")

if audio_input:

    if st.button("Transcribe and Ask", type="primary"):

        try:
            with st.spinner("Converting speech to text..."):

                recognized_text = (
                    st.session_state.speech_service.transcribe(
                        audio_input.getvalue()
                    )
                )

            if recognized_text:
                st.success(f"Recognized: {recognized_text}")
                process_question(recognized_text)

            else:
                st.warning("No speech was recognized.")

        except Exception as error:
            st.error(f"Speech recognition failed: {error}")


# --------------------------------------------------
# Handle typed questions
# --------------------------------------------------

if question:
    process_question(question)
