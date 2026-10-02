from __future__ import annotations
import io
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
load_dotenv()
MEET_SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.readonly",
    "https://www.googleapis.com/auth/meetings.space.settings",
    "https://www.googleapis.com/auth/drive.readonly",
]
class GoogleMeetClient:
    """
    Google Meet REST integration.

    Two modes are supported:
    1. Live/continuous transcript polling from Google Meet transcript entries.
    2. Post-meeting retrieval of the complete Meet transcript.

    Google Meet's REST API is not a raw microphone recorder. For live audio/video,
    Google's separate Meet Media API is required and is currently Developer Preview.
    This implementation intentionally uses the stable REST transcript/artifact path.
    """
    def __init__(
        self,
        client_secret_file: Optional[str] = None,
        token_file: Optional[str] = None,
    ):
        self.client_secret_file = (
            client_secret_file
            or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET_FILE", "credentials.json")
        )
        self.token_file = (
            token_file
            or os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "google_token.json")
        )
        self.creds = self._load_credentials()
        self.meet = build("meet", "v2", credentials=self.creds, cache_discovery=False)
        self.drive = build("drive", "v3", credentials=self.creds, cache_discovery=False)
    def _load_credentials(self) -> Credentials:
        creds = None
        if Path(self.token_file).exists():
            creds = Credentials.from_authorized_user_file(
                self.token_file,
                MEET_SCOPES,
            )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        if not creds or not creds.valid:
            if not Path(self.client_secret_file).exists():
                raise FileNotFoundError(
                    f"Google OAuth client file not found: {self.client_secret_file}. "
                    "Download an OAuth Desktop App client JSON from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file,
                MEET_SCOPES,
            )
            creds = flow.run_local_server(port=0)
        Path(self.token_file).write_text(
            creds.to_json(),
            encoding="utf-8",
        )
        return creds
    @staticmethod
    def normalize_meeting_code(value: str) -> str:
        value = (value or "").strip()
        match = re.search(r"meet\.google\.com/([a-zA-Z0-9-]+)", value)
        return match.group(1).lower() if match else value.lower()
    def get_space(self, meeting_code_or_url: str) -> Dict:
        meeting_code = self.normalize_meeting_code(meeting_code_or_url)
        return self.meet.spaces().get(
            name=f"spaces/{meeting_code}"
        ).execute()
    def configure_auto_transcription(
        self,
        meeting_code_or_url: str,
        enabled: bool = True,
    ) -> Dict:
        """
        Preconfigure automatic transcription for a meeting space.
        This requires the user to be the meeting organizer and the settings scope.
        """
        space = self.get_space(meeting_code_or_url)
        name = space["name"]
        body = {
            "config": {
                "artifactConfig": {
                    "transcriptionConfig": {
                        "autoTranscriptionGeneration": "ON" if enabled else "OFF"
                    }
                }
            }
        }
        return self.meet.spaces().patch(
            name=name,
            body=body,
            updateMask="config.artifactConfig.transcriptionConfig.autoTranscriptionGeneration",
        ).execute()
    def get_active_conference(self, meeting_code_or_url: str) -> Optional[str]:
        space = self.get_space(meeting_code_or_url)
        active = space.get("activeConference")
        return active.get("conferenceRecord") if active else None
    def find_latest_conference(
        self,
        meeting_code_or_url: str,
        include_ended: bool = True,
    ) -> Optional[Dict]:
        meeting_code = self.normalize_meeting_code(meeting_code_or_url)
        filter_parts = [f'space.meeting_code = "{meeting_code}"']
        if not include_ended:
            filter_parts.append("end_time IS NULL")
        response = self.meet.conferenceRecords().list(
            pageSize=10,
            filter=" AND ".join(filter_parts),
        ).execute()
        conferences = response.get("conferenceRecords", [])
        if not conferences:
            return None
        conferences.sort(
            key=lambda x: x.get("startTime", ""),
            reverse=True,
        )
        return conferences[0]
    def list_transcripts(self, conference_record: str) -> List[Dict]:
        response = self.meet.conferenceRecords().transcripts().list(
            parent=conference_record,
            pageSize=100,
        ).execute()
        return response.get("transcripts", [])
    def list_transcript_entries(self, transcript_name: str) -> List[Dict]:
        entries: List[Dict] = []
        page_token = None
        while True:
            kwargs = {
                "parent": transcript_name,
                "pageSize": 100,
            }
            if page_token:
                kwargs["pageToken"] = page_token
            response = (
                self.meet.conferenceRecords()
                .transcripts()
                .entries()
                .list(**kwargs)
                .execute()
            )
            entries.extend(response.get("transcriptEntries", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        entries.sort(key=lambda x: x.get("startTime", ""))
        return entries
    def get_complete_transcript(
        self,
        meeting_code_or_url: str,
        wait_for_file: bool = False,
        timeout_seconds: int = 180,
    ) -> Dict:
        conference = self.find_latest_conference(meeting_code_or_url)
        if not conference:
            return {"error": "No conference record found for this meeting code."}
        conference_record = conference["name"]
        transcripts = self.list_transcripts(conference_record)

        if not transcripts:
            return {
                "error": (
                    "No Google Meet transcript exists for this conference. "
                    "Make sure transcription was enabled/started."
                ),
                "conference_record": conference_record,
            }
        transcript = transcripts[-1]
        if wait_for_file:
            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                current = self.meet.conferenceRecords().transcripts().get(
                    name=transcript["name"]
                ).execute()
                state = current.get("state", "")
                transcript = current
                if state == "FILE_GENERATED":
                    break
                time.sleep(5)
        entries = self.list_transcript_entries(transcript["name"])
        return {
            "conference_record": conference_record,
            "transcript": transcript,
            "entries": entries,
            "text": self._entries_to_text(entries),
        }
    def stream_transcript(
        self,
        meeting_code_or_url: str,
        poll_seconds: int = 5,
        max_minutes: int = 180,
    ):
        """
        Generator yielding newly observed transcript entries while the meeting
        is active. It does not download audio; it polls Meet's transcript data.
        """
        started = time.time()
        seen = set()
        conference_record = None

        while time.time() - started < max_minutes * 60:
            try:
                if not conference_record:
                    conference_record = self.get_active_conference(meeting_code_or_url)
                    if not conference_record:
                        conference = self.find_latest_conference(
                            meeting_code_or_url,
                            include_ended=False,
                        )
                        if conference:
                            conference_record = conference["name"]
                if not conference_record:
                    time.sleep(poll_seconds)
                    continue
                transcripts = self.list_transcripts(conference_record)
                for transcript in transcripts:
                    entries = self.list_transcript_entries(transcript["name"])
                    for entry in entries:
                        key = entry.get("name") or (
                            entry.get("startTime", "") + "|" + entry.get("text", "")
                        )
                        if key not in seen:
                            seen.add(key)
                            yield entry
                conference = self.meet.conferenceRecords().get(
                    name=conference_record
                ).execute()
                if conference.get("endTime"):
                    for transcript in self.list_transcripts(conference_record):
                        for entry in self.list_transcript_entries(transcript["name"]):
                            key = entry.get("name") or (
                                entry.get("startTime", "") + "|" + entry.get("text", "")
                            )
                            if key not in seen:
                                seen.add(key)
                                yield entry
                    return
            except Exception as exc:
                yield {
                    "_system_error": str(exc),
                    "startTime": "",
                    "text": "",
                }

            time.sleep(max(2, poll_seconds))

    @staticmethod
    def _entries_to_text(entries: List[Dict]) -> str:
        lines = []
        for entry in entries:
            speaker = entry.get("participant", "Unknown speaker")
            text = entry.get("text", "").strip()
            if text:
                lines.append(f"{speaker}: {text}")
        return "\n".join(lines)

    def download_drive_file(self, file_id: str, destination: str) -> str:
        request = self.drive.files().get(
            fileId=file_id,
            alt="media",
        )
        with open(destination, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return destination

    def download_latest_recording(
        self,
        meeting_code_or_url: str,
        destination: str,
    ) -> str:
        conference = self.find_latest_conference(meeting_code_or_url)
        if not conference:
            raise RuntimeError("No conference found.")

        recordings = (
            self.meet.conferenceRecords()
            .recordings()
            .list(parent=conference["name"], pageSize=100)
            .execute()
            .get("recordings", [])
        )

        if not recordings:
            raise RuntimeError("No Meet recording exists for this conference.")

        recordings.sort(key=lambda x: x.get("startTime", ""))
        latest = recordings[-1]
        drive_destination = latest.get("driveDestination", {})
        file_id = drive_destination.get("fileId")

        if not file_id:
            raise RuntimeError(
                "The recording does not expose a Google Drive file ID yet."
            )

        return self.download_drive_file(file_id, destination)
