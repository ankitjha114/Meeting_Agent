from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

class AudioTranscriber:
    """
    Transcribe complete meeting recordings with OpenAI.

    For long/video recordings, ffmpeg is used to extract audio and split it into
    manageable chunks. Install ffmpeg and make sure `ffmpeg` is on PATH.
    """

    SUPPORTED = {
        ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a",
        ".wav", ".webm", ".ogg", ".flac"
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv(
            "OPENAI_TRANSCRIBE_MODEL",
            "gpt-4o-transcribe",
        )
        self.client = OpenAI(api_key=self.api_key)

    def _ffmpeg_available(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def _extract_audio(self, source: str, output_dir: str) -> str:
        target = str(Path(output_dir) / "meeting_audio.mp3")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                source,
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-b:a",
                "64k",
                target,
            ],
            check=True,
            capture_output=True,
        )
        return target

    def _split_audio(self, source: str, output_dir: str, minutes: int = 8) -> List[str]:
        pattern = str(Path(output_dir) / "chunk_%03d.mp3")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                source,
                "-f",
                "segment",
                "-segment_time",
                str(minutes * 60),
                "-reset_timestamps",
                "1",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-b:a",
                "64k",
                pattern,
            ],
            check=True,
            capture_output=True,
        )
        return sorted(str(p) for p in Path(output_dir).glob("chunk_*.mp3"))

    def _transcribe_file(self, path: str, prompt: Optional[str] = None) -> Dict:
        with open(path, "rb") as audio:
            kwargs = {
                "model": self.model,
                "file": audio,
            }
            if prompt:
                kwargs["prompt"] = prompt

            result = self.client.audio.transcriptions.create(**kwargs)

        return {
            "text": getattr(result, "text", ""),
            "model": self.model,
        }

    def transcribe(
        self,
        source_path: str,
        language: Optional[str] = None,
        progress_callback=None,
    ) -> Dict:
        if not self.api_key:
            return {"error": "OPENAI_API_KEY is not configured."}

        source = Path(source_path)
        if not source.exists():
            return {"error": f"File not found: {source_path}"}

        if source.suffix.lower() not in self.SUPPORTED:
            return {
                "error": (
                    f"Unsupported file type: {source.suffix}. "
                    f"Supported: {', '.join(sorted(self.SUPPORTED))}"
                )
            }

        prompt = None
        if language:
            prompt = f"The meeting language is {language}. Preserve names, acronyms and technical terms."

        with tempfile.TemporaryDirectory(prefix="meeting_transcribe_") as work:
            try:
                working_file = str(source)
                if source.suffix.lower() in {".mp4", ".webm", ".mpeg", ".mpga", ".m4a"}:
                    if not self._ffmpeg_available():
                        working_file = str(source)
                    else:
                        working_file = self._extract_audio(str(source), work)

                chunks = []
                if self._ffmpeg_available():
                    try:
                        chunks = self._split_audio(working_file, work, minutes=8)
                    except Exception:
                        chunks = []

                if not chunks:
                    chunks = [working_file]

                texts = []
                for index, chunk in enumerate(chunks, start=1):
                    if progress_callback:
                        progress_callback(index, len(chunks), Path(chunk).name)

                    result = self._transcribe_file(chunk, prompt=prompt)
                    if result.get("text"):
                        texts.append(result["text"].strip())

                full_text = "\n\n".join(texts).strip()
                return {
                    "text": full_text,
                    "chunks": len(chunks),
                    "model": self.model,
                }

            except Exception as exc:
                return {"error": f"Transcription failed: {exc}"}
