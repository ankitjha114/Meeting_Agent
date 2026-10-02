from __future__ import annotations
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import requests
from dotenv import load_dotenv
load_dotenv()

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def extract_json(text: str) -> Dict[str, Any]:
    """Safely extract a JSON object from an LLM response."""
    if not text:
        return {"error": "Empty model response"}

    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]

    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {"data": value}
    except json.JSONDecodeError as exc:
        return {"error": f"Failed to parse JSON: {exc}", "raw": text}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TodoistTools:
    BASE_URL = "https://api.todoist.com/rest/v2"

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or env("TODOIST_API_KEY") or env("Todoist_api_key")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs):
        if not self.api_token:
            return {"error": "TODOIST_API_KEY is not configured."}

        try:
            response = requests.request(
                method,
                f"{self.BASE_URL}{path}",
                headers=self.headers,
                timeout=30,
                **kwargs,
            )
            if response.ok:
                return response.json() if response.content else {}
            return {
                "error": f"Todoist API {response.status_code}: "
                          f"{response.text[:500]}"
            }
        except requests.RequestException as exc:
            return {"error": f"Todoist request failed: {exc}"}

    def list_projects(self):
        return self._request("GET", "/projects")

    def get_project(self, project_name: str):
        projects = self.list_projects()
        if isinstance(projects, dict) and "error" in projects:
            return projects

        for project in projects:
            if project.get("name", "").strip().lower() == project_name.strip().lower():
                return project
        return None

    def create_project(self, project_name: str, color: str = "berry_red"):
        existing = self.get_project(project_name)
        if existing:
            return existing
        return self._request(
            "POST",
            "/projects",
            json={"name": project_name, "color": color},
        )

    def get_collaborators(self, project_id: str):
        return self._request("GET", f"/projects/{project_id}/collaborators")

    def create_task(
        self,
        content: str,
        project_id: str,
        due_string: Optional[str] = None,
        priority: int = 3,
        assignee_id: Optional[str] = None,
    ):
        data = {
            "content": content,
            "project_id": project_id,
            "priority": max(1, min(int(priority or 3), 4)),
        }
        if due_string:
            data["due_string"] = due_string
        if assignee_id:
            data["assignee_id"] = assignee_id
        return self._request("POST", "/tasks", json=data)

    def create_and_assign_task(
        self,
        content: str,
        project_name: str,
        due_string: Optional[str] = None,
        priority: int = 3,
        assignee_name: Optional[str] = None,
    ):
        project = self.get_project(project_name) or self.create_project(project_name)
        if not project or "error" in project:
            return project or {"error": "Could not create/find Todoist project."}

        assignee_id = None
        if assignee_name:
            collaborators = self.get_collaborators(project["id"])
            if isinstance(collaborators, list):
                for person in collaborators:
                    if person.get("name", "").strip().lower() == assignee_name.strip().lower():
                        assignee_id = person.get("id")
                        break

        return self.create_task(
            content=content,
            project_id=project["id"],
            due_string=due_string,
            priority=priority,
            assignee_id=assignee_id,
        )

class TelegramCommunicator:
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        self.bot_token = bot_token or env("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or env("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, message: str):
        if not self.configured:
            return {"error": "Telegram is not configured."}

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
                timeout=20,
            )
            if response.ok:
                return response.json()
            return {"error": f"Telegram {response.status_code}: {response.text[:500]}"}
        except requests.RequestException as exc:
            return {"error": f"Telegram request failed: {exc}"}

    def ask_confirmation(self, question: str, options: Optional[List[str]] = None):
        options = options or ["Yes", "No"]
        if not self.configured:
            return {"error": "Telegram is not configured."}

        keyboard = [
            [{"text": option, "callback_data": option[:64]}]
            for option in options
        ]
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": question,
                    "reply_markup": json.dumps({"inline_keyboard": keyboard}),
                },
                timeout=20,
            )
            if response.ok:
                return response.json()
            return {"error": f"Telegram {response.status_code}: {response.text[:500]}"}
        except requests.RequestException as exc:
            return {"error": f"Telegram request failed: {exc}"}


class TaskExtractor:
    def __init__(self, llm):
        self.llm = llm

    def extract_tasks_from_transcript(self, transcript: str):
        prompt = f"""
You are a meeting action-item extraction agent.

Analyze this meeting transcript and return ONLY valid JSON.

Schema:
{{
  "projects": [
    {{
      "name": "Project name",
      "tasks": [
        {{
          "content": "Specific action",
          "assignee": "Person or null",
          "due_string": "Natural-language due date or null",
          "priority": 1,
          "evidence": "Short transcript evidence"
        }}
      ]
    }}
  ]
}}

Rules:
- Do not invent owners or deadlines.
- Only create an action when someone needs to do something.
- priority 1 is lowest and 4 is highest.
- If no project is explicitly named, use "Meeting Follow-ups".
- Return JSON only.

Transcript:
{transcript}
"""
        response = self.llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        return extract_json(content)


class MeetingAnalyzer:
    """Post-meeting analysis: summary, decisions, risks, actions, follow-up."""

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, transcript: str, meeting_context: str = ""):
        prompt = f"""
You are a senior meeting intelligence agent.

Analyze the meeting transcript below. Return ONLY JSON using exactly this schema:
{{
  "executive_summary": "5-10 sentence summary",
  "key_points": ["..."],
  "decisions": [
    {{"decision": "...", "owner": "person or null", "evidence": "..."}}
  ],
  "action_items": [
    {{
      "task": "...",
      "owner": "person or null",
      "deadline": "date/time or null",
      "priority": 1,
      "evidence": "..."
    }}
  ],
  "risks_and_blockers": [
    {{"risk": "...", "owner": "person or null", "mitigation": "..."}}
  ],
  "open_questions": ["..."],
  "follow_up_topics": ["..."],
  "client_or_customer_signals": ["..."],
  "next_meeting_agenda": ["..."],
  "follow_up_email": "Professional email body, no subject line"
}}

Important:
- Do not invent facts.
- Distinguish decisions from suggestions.
- Keep evidence short and grounded in the transcript.
- If a field has no evidence, use [] or null.

Meeting context:
{meeting_context}

Transcript:
{transcript}
"""
        response = self.llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        return extract_json(content)


class TodoistMeetingManager:
    def __init__(
        self,
        todoist_api_token: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        llm=None,
    ):
        self.todoist_tools = TodoistTools(todoist_api_token)
        self.telegram = TelegramCommunicator(telegram_bot_token, telegram_chat_id)
        self.task_extractor = TaskExtractor(llm) if llm else None

    def create_tasks_from_analysis(
        self,
        analysis: Dict[str, Any],
        default_project: str = "Meeting Follow-ups",
    ):
        results = {
            "projects_created": [],
            "tasks_created": [],
            "task_errors": [],
        }

        actions = analysis.get("action_items", [])
        for item in actions:
            task = item.get("task")
            if not task:
                continue

            project_name = default_project
            owner = item.get("owner")
            deadline = item.get("deadline")
            priority = item.get("priority", 3)

            created = self.todoist_tools.create_and_assign_task(
                content=task,
                project_name=project_name,
                due_string=deadline,
                priority=priority,
                assignee_name=owner,
            )

            if "error" in created:
                results["task_errors"].append(created["error"])
            else:
                results["tasks_created"].append(
                    {
                        "content": task,
                        "project": project_name,
                        "assignee": owner,
                        "due": deadline,
                        "priority": priority,
                        "todoist_id": created.get("id"),
                    }
                )

        if results["tasks_created"] and self.telegram.configured:
            lines = ["*Meeting actions created*"]
            for item in results["tasks_created"]:
                line = f"• {item['content']}"
                if item.get("assignee"):
                    line += f" — {item['assignee']}"
                if item.get("due"):
                    line += f" — due {item['due']}"
                lines.append(line)
            self.telegram.send_message("\n".join(lines))

        return results

class SimpleMeetingRAG:
    """
    Lightweight local TF-IDF RAG.
    This avoids a second paid embedding API and is robust for meeting notes,
    uploaded docs and transcripts.
    """

    def __init__(self, max_chunks: int = 5):
        self.max_chunks = max_chunks
        self.chunks: List[str] = []
        self.vectorizer = None
        self.matrix = None

    def build(self, texts: Iterable[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer

        raw = []
        for text in texts:
            text = text or ""
            words = text.split()
            chunk_size = 180
            overlap = 30
            for i in range(0, len(words), chunk_size - overlap):
                chunk = " ".join(words[i : i + chunk_size])
                if chunk.strip():
                    raw.append(chunk)

        self.chunks = raw
        if not raw:
            self.vectorizer = None
            self.matrix = None
            return

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=12000,
        )
        self.matrix = self.vectorizer.fit_transform(raw)

    def retrieve(self, query: str) -> List[str]:
        if not self.vectorizer or self.matrix is None:
            return []

        from sklearn.metrics.pairwise import cosine_similarity

        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        indexes = scores.argsort()[::-1][: self.max_chunks]
        return [self.chunks[i] for i in indexes if scores[i] > 0]

    def answer(self, query: str, llm) -> str:
        context = "\n\n---\n\n".join(self.retrieve(query))
        if not context:
            return "I could not find relevant information in the meeting materials."

        prompt = f"""
Answer the user's question using ONLY the supplied meeting context.
If the context does not contain the answer, say so.

Context:
{context}

Question:
{query}
"""
        response = llm.invoke(prompt)
        return getattr(response, "content", str(response))

def transcript_entries_to_text(entries: List[Dict[str, Any]]) -> str:
    lines = []
    for entry in entries:
        speaker = (
            entry.get("participant")
            or entry.get("speaker")
            or entry.get("participantName")
            or "Unknown speaker"
        )
        text = entry.get("text", "").strip()
        start = entry.get("startTime", "")
        if text:
            prefix = f"[{start}] " if start else ""
            lines.append(f"{prefix}{speaker}: {text}")
    return "\n".join(lines)


def calculate_speaker_stats(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        speaker = (
            entry.get("participantName")
            or entry.get("speaker")
            or entry.get("participant")
            or "Unknown speaker"
        )
        words = len((entry.get("text") or "").split())
        if speaker not in stats:
            stats[speaker] = {"speaker": speaker, "words": 0, "entries": 0}
        stats[speaker]["words"] += words
        stats[speaker]["entries"] += 1

    total = sum(v["words"] for v in stats.values()) or 1
    result = []
    for value in stats.values():
        value["share_percent"] = round(value["words"] * 100 / total, 1)
        result.append(value)
    return sorted(result, key=lambda x: x["words"], reverse=True)
