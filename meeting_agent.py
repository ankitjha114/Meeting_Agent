from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
try:
    from google import genai
except Exception:
    genai = None
from google_meet import GoogleMeetClient
from transcriber import AudioTranscriber
from utils import (
    MeetingAnalyzer,
    SimpleMeetingRAG,
    TodoistMeetingManager,
    calculate_speaker_stats,
    transcript_entries_to_text,
)
load_dotenv()

class MeetingLLM:
    """OpenAI-first LLM with Gemini fallback from the existing .env."""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

        self.provider = "openai" if self.openai_key else "gemini"

        if self.provider == "openai":
            self.client = OpenAI(api_key=self.openai_key)
            self.model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        else:
            if genai is None:
                raise RuntimeError(
                    "google-genai is not installed and OPENAI_API_KEY is not configured."
                )
            if not self.gemini_key:
                raise RuntimeError(
                    "Configure OPENAI_API_KEY or GEMINI_API_KEY in .env."
                )
            self.client = genai.Client(api_key=self.gemini_key)
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def invoke(self, prompt: str):
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a reliable enterprise meeting intelligence "
                            "assistant. Never invent meeting facts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return SimpleNamespace(content=response.choices[0].message.content)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return SimpleNamespace(content=response.text)

def initialize_session_state():
    defaults = {
        "transcript": "",
        "transcript_entries": [],
        "analysis": None,
        "meeting_context": "",
        "rag": None,
        "google_client": None,
        "todoist_manager": None,
        "live_running": False,
        "live_error": "",
        "recording_transcript": "",
        "task_results": None,
        "meeting_code": "",
        "company": "",
        "objective": "",
        "attendees": "",
        "focus": "",
        "duration": 60,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def read_uploaded_documents(uploaded_files):
    texts = []

    for file in uploaded_files or []:
        suffix = Path(file.name).suffix.lower()
        try:
            data = file.getvalue()

            if suffix == ".pdf":
                from pypdf import PdfReader
                reader = PdfReader(tempfile.NamedTemporaryFile(delete=False).name)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(data)
                    tmp.flush()
                    reader = PdfReader(tmp.name)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)

            elif suffix == ".docx":
                from docx import Document
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(data)
                    tmp.flush()
                    doc = Document(tmp.name)
                    text = "\n".join(p.text for p in doc.paragraphs)

            else:
                text = data.decode("utf-8", errors="ignore")

            texts.append(f"### {file.name}\n{text}")

        except Exception as exc:
            st.warning(f"Could not read {file.name}: {exc}")

    return texts


def build_meeting_context():
    return f"""
Company: {st.session_state['company']}
Meeting objective: {st.session_state['objective']}
Meeting duration: {st.session_state['duration']} minutes
Attendees:
{st.session_state['attendees']}
Focus areas:
{st.session_state['focus']}
Google Meet code/URL:
{st.session_state['meeting_code']}
""".strip()

def analyze_current_transcript():
    if not st.session_state["transcript"].strip():
        st.error("There is no transcript to analyze.")
        return

    llm = get_llm()
    analyzer = MeetingAnalyzer(llm)

    with st.spinner("Analyzing summary, decisions, action items, risks and follow-ups..."):
        result = analyzer.analyze(
            st.session_state["transcript"],
            build_meeting_context(),
        )

    if "error" in result:
        st.error(result["error"])
        return

    st.session_state["analysis"] = result

    rag = SimpleMeetingRAG(max_chunks=5)
    rag.build(
        [
            st.session_state["transcript"],
            st.session_state["meeting_context"],
        ]
    )
    st.session_state["rag"] = rag

def get_llm():
    return MeetingLLM()
def analysis_markdown() -> str:
    data = st.session_state.get("analysis") or {}
    lines = [
        "# Meeting Intelligence Report",
        "",
        "## Executive Summary",
        data.get("executive_summary", ""),
        "",
        "## Key Points",
    ]
    lines += [f"- {x}" for x in data.get("key_points", [])]

    lines += ["", "## Decisions"]
    for item in data.get("decisions", []):
        owner = item.get("owner") or "Unassigned"
        lines.append(f"- **{item.get('decision','')}** — Owner: {owner}")
        if item.get("evidence"):
            lines.append(f"  - Evidence: {item['evidence']}")

    lines += ["", "## Action Items"]
    for item in data.get("action_items", []):
        lines.append(
            f"- **{item.get('task','')}** — "
            f"Owner: {item.get('owner') or 'Unassigned'}; "
            f"Deadline: {item.get('deadline') or 'Not specified'}; "
            f"Priority: {item.get('priority', 3)}"
        )

    lines += ["", "## Risks & Blockers"]
    for item in data.get("risks_and_blockers", []):
        lines.append(
            f"- {item.get('risk','')} — "
            f"Mitigation: {item.get('mitigation','')}"
        )

    lines += ["", "## Open Questions"]
    lines += [f"- {x}" for x in data.get("open_questions", [])]

    lines += ["", "## Follow-up Topics"]
    lines += [f"- {x}" for x in data.get("follow_up_topics", [])]

    lines += ["", "## Customer / Client Signals"]
    lines += [f"- {x}" for x in data.get("client_or_customer_signals", [])]

    lines += ["", "## Next Meeting Agenda"]
    lines += [f"- {x}" for x in data.get("next_meeting_agenda", [])]

    lines += ["", "## Follow-up Email", "", data.get("follow_up_email", "")]
    return "\n".join(lines)

def get_google_client():
    if st.session_state["google_client"] is None:
        st.session_state["google_client"] = GoogleMeetClient(
            client_secret_file=os.getenv(
                "GOOGLE_OAUTH_CLIENT_SECRET_FILE",
                "credentials.json",
            ),
            token_file=os.getenv(
                "GOOGLE_OAUTH_TOKEN_FILE",
                "google_token.json",
            ),
        )
    return st.session_state["google_client"]

def run_live_capture(meeting_code: str, poll_seconds: int, max_minutes: int):
    """
    Blocking Streamlit capture loop. Use a sensible max duration.
    New transcript entries are appended to session state.
    """
    client = get_google_client()
    placeholder = st.empty()
    status = st.empty()

    entries = []
    system_error = None

    status.info(
        f"Listening for Google Meet transcript entries for up to {max_minutes} minutes..."
    )

    for entry in client.stream_transcript(
        meeting_code,
        poll_seconds=poll_seconds,
        max_minutes=max_minutes,
    ):
        if entry.get("_system_error"):
            system_error = entry["_system_error"]
            status.warning(system_error)
            continue

        entries.append(entry)
        text = transcript_entries_to_text(entries)
        placeholder.text_area(
            "Live transcript",
            text,
            height=420,
            key=f"live_display_{len(entries)}",
        )

    if entries:
        st.session_state["transcript_entries"] = entries
        st.session_state["transcript"] = transcript_entries_to_text(entries)
        st.success(f"Captured {len(entries)} transcript entries.")

    if system_error:
        st.warning("Capture finished with an API warning. Check Google permissions.")

    st.session_state["rag"] = None


def get_latest_google_transcript(meeting_code: str):
    client = get_google_client()
    result = client.get_complete_transcript(
        meeting_code,
        wait_for_file=True,
        timeout_seconds=180,
    )

    if "error" in result:
        st.error(result["error"])
        return

    st.session_state["transcript_entries"] = result["entries"]
    st.session_state["transcript"] = result["text"]

    rag = SimpleMeetingRAG()
    rag.build([result["text"], st.session_state["meeting_context"]])
    st.session_state["rag"] = rag

    st.success(
        f"Loaded {len(result['entries'])} transcript entries from Google Meet."
    )

def main():
    st.set_page_config(
        page_title="AI Meeting Command Center",
        page_icon="🤖",
        layout="wide",
    )
    initialize_session_state()

    st.title("🤖 AI Meeting Command Center")
    st.caption(
        "Prepare → capture → transcribe → analyze → act → follow up"
    )

    with st.sidebar:
        st.header("Configuration")

        openai_key = st.text_input(
            "OpenAI API Key (optional; needed for recording transcription)",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key

        st.caption(
            "Text analysis can use GEMINI_API_KEY from .env automatically. "
            "OpenAI is used for uploaded audio/video transcription."
        )

        st.text_input(
            "OpenAI chat model",
            value=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            key="chat_model_ui",
        )
        os.environ["OPENAI_CHAT_MODEL"] = st.session_state["chat_model_ui"]

        st.text_input(
            "Gemini model",
            value=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            key="gemini_model_ui",
        )
        os.environ["GEMINI_MODEL"] = st.session_state["gemini_model_ui"]

        st.text_input(
            "OpenAI transcription model",
            value=os.getenv(
                "OPENAI_TRANSCRIBE_MODEL",
                "gpt-4o-transcribe",
            ),
            key="transcribe_model_ui",
        )
        os.environ["OPENAI_TRANSCRIBE_MODEL"] = st.session_state[
            "transcribe_model_ui"
        ]

        st.divider()
        st.subheader("Integrations")
        todoist_ok = bool(
            os.getenv("TODOIST_API_KEY") or os.getenv("Todoist_api_key")
        )
        telegram_ok = bool(
            (os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("telegram_bot_token"))
            and (os.getenv("TELEGRAM_CHAT_ID") or os.getenv("telegram_chat_id"))
        )
        google_creds_ok = Path(
            os.getenv(
                "GOOGLE_OAUTH_CLIENT_SECRET_FILE",
                "credentials.json",
            )
        ).exists()

        st.write(
            f"Todoist: {'✅' if todoist_ok else '❌'}\n\n"
            f"Telegram: {'✅' if telegram_ok else '❌'}\n\n"
            f"Google OAuth client: {'✅' if google_creds_ok else '❌'}"
        )

        if st.button("Test Google Meet connection", use_container_width=True):
            try:
                client = get_google_client()
                st.success("Google Meet authentication is working.")
            except Exception as exc:
                st.error(str(exc))

    tabs = st.tabs(
        [
            "1. Meeting Setup",
            "2. Live Meet",
            "3. Recording",
            "4. Intelligence",
            "5. Q&A",
            "6. Tasks",
            "7. Reports",
        ]
    )

    with tabs[0]:
        st.subheader("Meeting configuration")
        col1, col2 = st.columns(2)

        with col1:
            st.session_state["company"] = st.text_input(
                "Company / client",
                value=st.session_state["company"],
            )
            st.session_state["objective"] = st.text_area(
                "Meeting objective",
                value=st.session_state["objective"],
            )
            st.session_state["meeting_code"] = st.text_input(
                "Google Meet URL or meeting code",
                value=st.session_state["meeting_code"],
            )
            st.session_state["duration"] = st.slider(
                "Expected duration (minutes)",
                15,
                240,
                st.session_state["duration"],
            )

        with col2:
            st.session_state["attendees"] = st.text_area(
                "Attendees (one per line)",
                value=st.session_state["attendees"],
            )
            st.session_state["focus"] = st.text_area(
                "Focus areas / concerns",
                value=st.session_state["focus"],
            )

        docs = st.file_uploader(
            "Context documents",
            type=["pdf", "txt", "md", "docx"],
            accept_multiple_files=True,
        )

        if st.button(
            "Prepare Meeting Context",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["meeting_context"] = build_meeting_context()
            document_texts = read_uploaded_documents(docs)
            all_text = [
                st.session_state["meeting_context"],
                *document_texts,
            ]

            rag = SimpleMeetingRAG()
            rag.build(all_text)
            st.session_state["rag"] = rag

            st.success("Meeting context and searchable knowledge base prepared.")

        if st.session_state["meeting_context"]:
            st.code(st.session_state["meeting_context"])

    with tabs[1]:
        st.subheader("Google Meet live transcript")

        if not st.session_state["meeting_code"]:
            st.info("Enter a Google Meet URL/code in Meeting Setup first.")
        else:
            st.warning(
                "For this mode, Google Meet transcription must be enabled and "
                "the authenticated Google account must have permission to access "
                "the meeting. The app polls structured Meet transcript entries."
            )

            c1, c2 = st.columns(2)
            with c1:
                poll_seconds = st.number_input(
                    "Poll interval (seconds)",
                    3,
                    30,
                    5,
                )
            with c2:
                max_minutes = st.number_input(
                    "Maximum capture time (minutes)",
                    1,
                    240,
                    int(st.session_state["duration"]),
                )

            if st.button(
                "Enable Auto-Transcription for This Meeting Space",
                use_container_width=True,
            ):
                try:
                    client = get_google_client()
                    client.configure_auto_transcription(
                        st.session_state["meeting_code"],
                        enabled=True,
                    )
                    st.success(
                        "Auto-transcription configuration requested. "
                        "Google may require organizer privileges."
                    )
                except Exception as exc:
                    st.error(str(exc))

            if st.button(
                "Start Continuous Transcript Capture",
                type="primary",
                use_container_width=True,
            ):
                try:
                    run_live_capture(
                        st.session_state["meeting_code"],
                        int(poll_seconds),
                        int(max_minutes),
                    )
                except Exception as exc:
                    st.error(f"Live capture failed: {exc}")

            st.divider()

            if st.button(
                "Load Latest Complete Google Meet Transcript",
                use_container_width=True,
            ):
                try:
                    get_latest_google_transcript(
                        st.session_state["meeting_code"]
                    )
                except Exception as exc:
                    st.error(f"Could not retrieve transcript: {exc}")

    with tabs[2]:
        st.subheader("Full meeting recording → transcription")

        if st.session_state["meeting_code"]:
            if st.button(
                "Download Latest Google Meet Recording and Transcribe",
                use_container_width=True,
            ):
                try:
                    meet_client = get_google_client()
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp4",
                    ) as tmp:
                        recording_path = tmp.name

                    with st.spinner("Downloading the latest Meet recording from Drive..."):
                        meet_client.download_latest_recording(
                            st.session_state["meeting_code"],
                            recording_path,
                        )

                    progress = st.empty()

                    def update_meet_recording_progress(i, total, name):
                        progress.info(
                            f"Transcribing Meet recording chunk {i}/{total}: {name}"
                        )

                    with st.spinner("Transcribing the downloaded Meet recording..."):
                        transcriber = AudioTranscriber(
                            api_key=os.getenv("OPENAI_API_KEY"),
                            model=os.getenv(
                                "OPENAI_TRANSCRIBE_MODEL",
                                "gpt-4o-transcribe",
                            ),
                        )
                        result = transcriber.transcribe(
                            recording_path,
                            progress_callback=update_meet_recording_progress,
                        )

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state["recording_transcript"] = result["text"]
                        st.session_state["transcript"] = result["text"]
                        st.session_state["transcript_entries"] = []
                        st.success(
                            "Google Meet recording downloaded and transcribed."
                        )
                except Exception as exc:
                    st.error(f"Could not download/transcribe Meet recording: {exc}")

        recording = st.file_uploader(
            "Upload the complete meeting recording",
            type=[
                "mp3",
                "mp4",
                "mpeg",
                "mpga",
                "m4a",
                "wav",
                "webm",
                "ogg",
                "flac",
            ],
            key="recording_upload",
        )

        language = st.text_input(
            "Meeting language (optional)",
            placeholder="en, hi, en-IN, etc.",
        )

        if recording and st.button(
            "Transcribe Complete Recording",
            type="primary",
            use_container_width=True,
        ):
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(recording.name).suffix,
            ) as tmp:
                tmp.write(recording.getvalue())
                recording_path = tmp.name

            progress = st.empty()

            def update_progress(i, total, name):
                progress.info(f"Transcribing chunk {i}/{total}: {name}")

            try:
                transcriber = AudioTranscriber(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model=os.getenv(
                        "OPENAI_TRANSCRIBE_MODEL",
                        "gpt-4o-transcribe",
                    ),
                )
                result = transcriber.transcribe(
                    recording_path,
                    language=language or None,
                    progress_callback=update_progress,
                )

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.session_state["recording_transcript"] = result["text"]
                    st.session_state["transcript"] = result["text"]
                    st.session_state["transcript_entries"] = []
                    st.session_state["rag"] = None
                    st.success(
                        f"Recording transcribed successfully "
                        f"({result.get('chunks', 1)} chunk(s))."
                    )
            except Exception as exc:
                st.error(str(exc))

        if st.session_state["recording_transcript"]:
            st.text_area(
                "Complete recording transcript",
                st.session_state["recording_transcript"],
                height=500,
            )

    with tabs[3]:
        st.subheader("Meeting intelligence")

        if st.session_state["transcript"]:
            st.info(
                f"Current transcript: "
                f"{len(st.session_state['transcript'].split()):,} words"
            )

            if st.button(
                "Run Full Meeting Analysis",
                type="primary",
                use_container_width=True,
            ):
                try:
                    analyze_current_transcript()
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")

        else:
            st.info(
                "Capture a Meet transcript or upload a recording before analysis."
            )

        analysis = st.session_state.get("analysis")
        if analysis:
            st.divider()

            m1, m2, m3 = st.columns(3)
            m1.metric("Decisions", len(analysis.get("decisions", [])))
            m2.metric("Action items", len(analysis.get("action_items", [])))
            m3.metric("Risks / blockers", len(analysis.get("risks_and_blockers", [])))

            st.markdown("### Executive Summary")
            st.write(analysis.get("executive_summary", ""))

            with st.expander("Decisions", expanded=True):
                for item in analysis.get("decisions", []):
                    st.markdown(
                        f"**{item.get('decision','')}**  \n"
                        f"Owner: {item.get('owner') or 'Unassigned'}"
                    )
                    if item.get("evidence"):
                        st.caption(item["evidence"])

            with st.expander("Action items", expanded=True):
                if analysis.get("action_items"):
                    st.dataframe(
                        pd.DataFrame(analysis["action_items"]),
                        use_container_width=True,
                    )
                else:
                    st.write("No explicit action items found.")

            with st.expander("Risks & blockers", expanded=True):
                for item in analysis.get("risks_and_blockers", []):
                    st.markdown(
                        f"**{item.get('risk','')}** — "
                        f"{item.get('mitigation','')}"
                    )

            with st.expander("Open questions"):
                for item in analysis.get("open_questions", []):
                    st.write(f"- {item}")

            with st.expander("Next meeting agenda"):
                for item in analysis.get("next_meeting_agenda", []):
                    st.write(f"- {item}")

            with st.expander("Follow-up email"):
                st.text_area(
                    "Email draft",
                    analysis.get("follow_up_email", ""),
                    height=250,
                    key="follow_up_email_view",
                )

            if st.session_state["transcript_entries"]:
                st.markdown("### Speaker participation")
                stats = calculate_speaker_stats(
                    st.session_state["transcript_entries"]
                )
                if stats:
                    st.dataframe(
                        pd.DataFrame(stats),
                        use_container_width=True,
                    )

    with tabs[4]:
        st.subheader("Meeting Q&A / RAG assistant")

        if not st.session_state["rag"]:
            st.info("Prepare meeting context or run transcription first.")
        else:
            question = st.text_input(
                "Ask anything grounded in the meeting materials",
                placeholder="What did we decide about the launch date?",
            )

            if question:
                try:
                    answer = st.session_state["rag"].answer(question, get_llm())
                    st.markdown("### Answer")
                    st.write(answer)
                except Exception as exc:
                    st.error(str(exc))

    with tabs[5]:
        st.subheader("Action → Todoist → Telegram")

        if not st.session_state["analysis"]:
            st.info("Run meeting analysis first.")
        else:
            analysis = st.session_state["analysis"]

            if analysis.get("action_items"):
                st.dataframe(
                    pd.DataFrame(analysis["action_items"]),
                    use_container_width=True,
                )

            create_tasks = st.checkbox(
                "Create these action items in Todoist",
                value=False,
            )
            send_telegram = st.checkbox(
                "Send the created action summary to Telegram",
                value=True,
            )

            if st.button(
                "Execute Approved Actions",
                type="primary",
                use_container_width=True,
            ):
                if not create_tasks:
                    st.warning(
                        "Check 'Create these action items in Todoist' first."
                    )
                else:
                    try:
                        manager = TodoistMeetingManager(
                            todoist_api_token=(
                                os.getenv("TODOIST_API_KEY")
                                or os.getenv("Todoist_api_key")
                            ),
                            telegram_bot_token=(
                                os.getenv("TELEGRAM_BOT_TOKEN")
                                or os.getenv("telegram_bot_token")
                            ),
                            telegram_chat_id=(
                                os.getenv("TELEGRAM_CHAT_ID")
                                or os.getenv("telegram_chat_id")
                            ),
                            llm=get_llm(),
                        )

                        result = manager.create_tasks_from_analysis(
                            analysis,
                            default_project=(
                                st.session_state["company"].strip()
                                or "Meeting Follow-ups"
                            ),
                        )
                        st.session_state["task_results"] = result

                        if result["tasks_created"]:
                            st.success(
                                f"Created {len(result['tasks_created'])} Todoist task(s)."
                            )

                        if result["task_errors"]:
                            for error in result["task_errors"]:
                                st.error(error)

                    except Exception as exc:
                        st.error(f"Task automation failed: {exc}")

            if st.session_state["task_results"]:
                st.json(st.session_state["task_results"])

    with tabs[6]:
        st.subheader("Downloadable meeting artifacts")

        if st.session_state["transcript"]:
            st.download_button(
                "Download Transcript (.txt)",
                st.session_state["transcript"],
                file_name="meeting_transcript.txt",
                mime="text/plain",
                use_container_width=True,
            )

        if st.session_state["analysis"]:
            report = analysis_markdown()
            st.download_button(
                "Download Intelligence Report (.md)",
                report,
                file_name="meeting_intelligence_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

            st.download_button(
                "Download Analysis JSON",
                json.dumps(
                    st.session_state["analysis"],
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name="meeting_analysis.json",
                mime="application/json",
                use_container_width=True,
            )

        if st.session_state["transcript_entries"]:
            st.download_button(
                "Download Structured Transcript JSON",
                json.dumps(
                    st.session_state["transcript_entries"],
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name="meeting_transcript_entries.json",
                mime="application/json",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
