
import gc
import os
import tempfile
import time

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


class SpeechToText:

    def __init__(self):
        endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
        key = os.getenv("AZURE_SPEECH_KEY")

        if not endpoint or not key:
            raise ValueError(
                "Missing AZURE_SPEECH_ENDPOINT or AZURE_SPEECH_KEY "
                "in your .env file."
            )

        self.speech_config = speechsdk.SpeechConfig(
            subscription=key,
            endpoint=endpoint,
        )

        self.speech_config.speech_recognition_language = "en-US"

    def transcribe(self, audio_bytes: bytes) -> str:

        if not audio_bytes:
            raise ValueError("No audio data received.")

        audio_path = None
        audio_config = None
        recognizer = None
        result = None

        try:
            # Save browser-recorded WAV audio to a temporary file.
            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False,
            ) as audio_file:

                audio_file.write(audio_bytes)
                audio_path = audio_file.name

            # Configure audio input.
            audio_config = speechsdk.audio.AudioConfig(
                filename=audio_path
            )

            # Create Speech Recognizer.
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config,
            )

            # Recognize one utterance.
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text

            elif result.reason == speechsdk.ResultReason.NoMatch:
                return ""

            elif result.reason == speechsdk.ResultReason.Canceled:

                details = result.cancellation_details

                raise RuntimeError(
                    f"Speech recognition canceled: "
                    f"{details.error_details}"
                )

            else:
                raise RuntimeError(
                    f"Unexpected recognition result: {result.reason}"
                )

        finally:
            # Release references to SDK objects.
            result = None
            recognizer = None
            audio_config = None

            # Ask Python to collect released SDK objects.
            gc.collect()

            # Retry temporary file deletion on Windows.
            if audio_path and os.path.exists(audio_path):

                for attempt in range(5):
                    try:
                        os.remove(audio_path)
                        break

                    except PermissionError:
                        if attempt == 4:
                            raise RuntimeError(
                                "Could not delete temporary audio file. "
                                "The Speech SDK may still be using it."
                            )

                        time.sleep(0.5)
