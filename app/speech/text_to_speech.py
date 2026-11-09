
import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


class TextToSpeech:

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

        # English neural voice
        self.speech_config.speech_synthesis_voice_name = (
            "en-US-JennyNeural"
        )

        # MP3 output for browser playback
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3
        )

    def synthesize(self, text: str) -> bytes:

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=None,
        )

        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data

        if result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details

            raise RuntimeError(
                f"Speech synthesis canceled: {details.error_details}"
            )

        raise RuntimeError(
            f"Unexpected speech synthesis result: {result.reason}"
        )
