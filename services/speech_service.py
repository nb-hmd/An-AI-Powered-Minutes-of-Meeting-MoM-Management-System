"""
Speech Service - Audio transcription using OpenAI Whisper API.
Supports MP3, WAV, and M4A formats.
After transcription, optionally runs AI extraction on the transcript.
"""

import os
import tempfile
from models.activity_log import ActivityLogModel


class SpeechService:
    """Service for converting speech/audio to text using OpenAI Whisper API."""

    SUPPORTED_FORMATS = ["mp3", "wav", "m4a"]

    @staticmethod
    def transcribe_audio(audio_file, user_id=None) -> dict:
        """
        Transcribe an audio file to text using OpenAI Whisper API.
        Returns dict with 'success', 'text', and 'message'.
        """
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "text": "",
                    "message": "OPENAI_API_KEY is not set. Please add it to your .env file.",
                }
            return SpeechService._transcribe_with_openai(audio_file, api_key, user_id)

        except Exception as e:
            return {"success": False, "text": "", "message": f"Transcription error: {str(e)}"}

    @staticmethod
    def _transcribe_with_openai(audio_file, api_key, user_id=None):
        """Use OpenAI Whisper API for transcription."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Determine file extension from the uploaded file name
            filename = getattr(audio_file, "name", "audio.wav")
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "wav"
            if ext not in SpeechService.SUPPORTED_FORMATS:
                ext = "wav"

            # Save to temp file with correct extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            # Reset file position in case it needs to be read again
            if hasattr(audio_file, "seek"):
                audio_file.seek(0)

            with open(tmp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                )

            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            if user_id:
                ActivityLogModel.log_activity(
                    user_id=user_id, username="",
                    action="Audio Transcribed",
                    details=f"Transcribed audio ({ext.upper()}) using OpenAI Whisper API",
                )

            return {
                "success": True,
                "text": transcript.text,
                "message": "Transcription completed using OpenAI Whisper.",
            }

        except Exception as e:
            return {"success": False, "text": "", "message": f"OpenAI Whisper API error: {str(e)}"}

    @staticmethod
    def transcribe_and_extract(audio_file, user_id=None) -> dict:
        """
        Full pipeline (F15): transcribe audio, then run AI extraction
        to get discussion, decisions, and action items.
        Returns dict with 'success', 'transcript', 'discussion', 'decisions',
        'action_items', 'message'.
        """
        # Step 1: Transcribe
        transcribe_result = SpeechService.transcribe_audio(audio_file, user_id)
        if not transcribe_result["success"]:
            return {
                "success": False, "transcript": "", "discussion": "",
                "decisions": "", "action_items": [],
                "message": transcribe_result["message"],
            }

        transcript = transcribe_result["text"]

        # Step 2: Run AI extraction on the transcript
        try:
            from services.ai_service import AIService
            ai_result = AIService.format_rough_notes_to_mom(transcript, user_id)

            if ai_result["success"]:
                return {
                    "success": True,
                    "transcript": transcript,
                    "discussion": ai_result["discussion"],
                    "decisions": ai_result["decisions"],
                    "action_items": ai_result["action_items"],
                    "agenda": ai_result.get("agenda", ""),
                    "message": "Audio transcribed and AI extraction completed.",
                }
            else:
                # Transcription worked but AI extraction failed — still return transcript
                return {
                    "success": True,
                    "transcript": transcript,
                    "discussion": transcript,  # Use raw transcript as discussion
                    "decisions": "",
                    "action_items": [],
                    "agenda": "",
                    "message": f"Audio transcribed. AI extraction failed: {ai_result['message']}",
                }

        except Exception as e:
            # Transcription worked but AI failed — still return transcript
            return {
                "success": True,
                "transcript": transcript,
                "discussion": transcript,
                "decisions": "",
                "action_items": [],
                "agenda": "",
                "message": f"Audio transcribed. AI extraction error: {str(e)}",
            }
