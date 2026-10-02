# Meeting_Agent
# 🤖 AI Meeting Command Center

> **Prepare → Capture → Transcribe → Understand → Act → Follow Up**

AI Meeting Command Center is an end-to-end meeting intelligence application built with **Python + Streamlit**. It is designed to help a company manage the complete meeting lifecycle rather than only generating a meeting summary.

The system combines:

- 📝 Pre-meeting preparation
- 🎥 Google Meet integration
- 🎙️ Live/continuous transcript capture
- 📁 Full meeting recording transcription
- 🧠 AI-powered meeting intelligence
- 🔎 Meeting Q&A / RAG
- ✅ Action-item extraction
- 📋 Todoist task automation
- 📲 Telegram notifications
- 📊 Speaker participation analytics
- 📄 Markdown / JSON / transcript exports

---

# 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Why This Project](#-why-this-project)
3. [Core Features](#-core-features)
4. [Complete Workflow](#-complete-workflow)
5. [System Architecture](#-system-architecture)
6. [Project Structure](#-project-structure)
7. [Technology Stack](#-technology-stack)
8. [Requirements](#-requirements)
9. [Installation](#-installation)
10. [Environment Variables](#-environment-variables)
11. [Google Meet OAuth Setup](#-google-meet-oauth-setup)
12. [Todoist Setup](#-todoist-setup)
13. [Telegram Setup](#-telegram-setup)
14. [Running the Application](#-running-the-application)
15. [How to Use Every Feature](#-how-to-use-every-feature)
16. [Testing Guide](#-testing-guide)
17. [Recording Transcription](#-recording-transcription)
18. [Google Meet Live Transcription](#-google-meet-live-transcription)
19. [Meeting Intelligence](#-meeting-intelligence)
20. [Meeting Q&A / RAG](#-meeting-qa--rag)
21. [Todoist Automation](#-todoist-automation)
22. [Telegram Notifications](#-telegram-notifications)
23. [Reports and Exports](#-reports-and-exports)
24. [Security](#-security)
25. [Troubleshooting](#-troubleshooting)
26. [Known Limitations](#-known-limitations)
27. [Production Architecture](#-production-architecture)
28. [Future Enhancements](#-future-enhancements)
29. [GitHub Deployment](#-github-deployment)
30. [Project Summary](#-project-summary)

---

# 🚀 Project Overview

**AI Meeting Command Center** is a meeting automation and intelligence platform that connects the different stages of a business meeting into one workflow.

Instead of treating a meeting as:

```text
Meeting
   ↓
Recording
   ↓
Summary
```

this project treats it as:

```text
                 PRE-MEETING
                     ↓
             Meeting Preparation
                     ↓
               Meeting Capture
                     ↓
              Transcription
                     ↓
             AI Understanding
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Summary     Decisions    Action Items
        ↓            ↓            ↓
        └────────────┼────────────┘
                     ↓
                  Todoist
                     ↓
                Team Tasks
                     ↓
                 Telegram
                     ↓
                Follow-up
```

The goal is to turn meeting information into **structured, actionable business information**.

---

# 🎯 Why This Project

Companies generate a large amount of information during meetings:

- Decisions
- Responsibilities
- Deadlines
- Customer requirements
- Risks
- Questions
- Follow-up actions
- Project changes

The problem is that much of this information remains inside recordings, transcripts, chat messages, or people's memory.

This application attempts to solve that problem by creating a single workflow:

```text
Meeting data
     ↓
Transcript
     ↓
Structured intelligence
     ↓
Tasks
     ↓
Notifications
     ↓
Reports
```

---

# ✨ Core Features

## 1. 📝 Meeting Preparation

Before a meeting, provide:

- Company/client name
- Meeting objective
- Meeting date
- Expected duration
- Attendees
- Attendee roles
- Attendee companies
- Focus areas
- Concerns
- Supporting documents

The AI generates:

- Context analysis
- Meeting strategy
- Time-boxed agenda
- Talking points
- Discussion questions
- Executive briefing
- Success criteria

---

## 2. 🎥 Google Meet Integration

The application can connect to Google Meet using Google OAuth.

It supports:

- Google Meet URL
- Google Meet meeting code
- Google OAuth authentication
- Conference lookup
- Transcript retrieval
- Transcript entry retrieval
- Speaker information
- Meeting recordings/artifacts where available

The Google Meet integration uses Google's APIs rather than attempting to scrape the Google Meet web interface.

---

## 3. 🎙️ Continuous Meeting Transcript Capture

The application can poll Google Meet transcript entries while a meeting is taking place.

Conceptually:

```text
Google Meet
     ↓
Meet transcript entries
     ↓
Polling
     ↓
New entries detected
     ↓
Live transcript displayed
```

The transcript can contain:

- Speaker
- Timestamp
- Spoken content

### Important

This is **structured Google Meet transcript retrieval**, not direct raw microphone interception.

Google Meet's APIs distinguish between transcript/artifact access and raw real-time media access. This project uses the transcript/API route.

---

## 4. 🎧 Full Recording Transcription

You can upload a complete meeting recording.

Supported common formats include:

```text
MP3
MP4
M4A
WAV
WebM
OGG
FLAC
```

The application can:

```text
Recording
   ↓
Audio extraction
   ↓
Audio chunking
   ↓
Speech-to-text
   ↓
Chunk combination
   ↓
Complete transcript
```

This is useful when:

- The meeting already happened
- A recording was downloaded
- Live transcript access was unavailable
- You want to analyze an existing meeting archive

---

## 5. 🧠 Meeting Intelligence

Once a transcript is available, the application can generate structured meeting intelligence.

### Executive Summary

A concise overview of the meeting.

### Key Discussion Points

Important subjects discussed.

### Decisions

Explicit decisions made during the meeting.

### Action Items

Tasks identified from the conversation.

### Owners

People responsible for actions when identifiable.

### Deadlines

Due dates mentioned in the conversation.

### Priorities

Relative importance of action items.

### Risks / Blockers

Potential issues that may prevent progress.

### Open Questions

Questions that remain unresolved.

### Follow-up Topics

Topics requiring future discussion.

### Client / Customer Signals

Relevant customer requirements, concerns, objections, or requests.

### Next Meeting Agenda

Potential agenda for the next meeting.

### Follow-up Email Draft

A draft that can be reviewed and sent to participants.

---

# 🔎 Meeting Q&A / RAG

The project includes a meeting Q&A assistant.

It can use:

- Meeting context
- Uploaded documents
- Transcript content
- Generated meeting information

You can ask questions such as:

```text
What were the main objectives of the meeting?
```

```text
Who is responsible for the CRM integration?
```

```text
What deadline did the team agree on?
```

```text
What risks were discussed?
```

```text
What decisions were made?
```

```text
What information is missing from the meeting?
```

The application uses local TF-IDF retrieval for the Q&A layer, which helps keep basic retrieval inexpensive and local.

---

# 📋 Todoist Automation

Meeting action items can be converted into Todoist tasks.

Example:

```text
Meeting:
AI Customer Support Project

Action Item:
Build AI chatbot

Owner:
Priya

Deadline:
Friday
```

becomes:

```text
Todoist Project:
AI Customer Support Project

Task:
Build AI chatbot
```

The integration can also:

- Create projects
- Find existing projects
- Create tasks
- Assign tasks where a matching Todoist collaborator exists
- Set priorities
- Set due dates when supported by the extracted information

---

# 📲 Telegram Notifications

Telegram can be used as a team notification channel.

After tasks are created, the application can send a summary such as:

```text
Meeting Task Summary

Project:
AI Customer Support Project

Tasks Created:
6

- Build AI chatbot
- Prepare evaluation report
- Create marketing campaign
- Prepare customer announcement
```

This allows the team to receive meeting outcomes without opening the Streamlit dashboard.

---

# 📊 Speaker Participation Analytics

For Google Meet transcripts where speaker information is available, the system can calculate basic participation information such as:

- Speaker names
- Number of transcript entries
- Approximate word counts
- Relative transcript contribution

These are descriptive transcript statistics and should not be treated as a complete measurement of meeting participation or employee performance.

---

# 📄 Reports and Exports

The application supports exporting meeting information in machine-readable and human-readable formats.

Typical outputs include:

```text
Meeting Transcript
Meeting Intelligence Report
Analysis JSON
Structured Transcript JSON
Markdown Reports
```

This makes the system useful for:

- Internal documentation
- Project records
- Client follow-ups
- Knowledge bases
- Future automation pipelines

---

# 🔄 Complete Workflow

A typical workflow is:

```text
1. Configure Meeting
        ↓
2. Add company/client
        ↓
3. Add objective
        ↓
4. Add attendees
        ↓
5. Add focus areas
        ↓
6. Upload supporting documents
        ↓
7. Generate meeting preparation
        ↓
8. Start Google Meet / upload recording
        ↓
9. Obtain transcript
        ↓
10. Analyze transcript
        ↓
11. Extract decisions
        ↓
12. Extract action items
        ↓
13. Identify owners/deadlines
        ↓
14. Create Todoist tasks
        ↓
15. Notify team on Telegram
        ↓
16. Generate meeting report
        ↓
17. Prepare follow-up
```

---

# 🏗️ System Architecture

```text
                        ┌─────────────────────┐
                        │   Streamlit UI      │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       Meeting Setup          Google Meet          Recording
              │                    │                    │
              │                    ▼                    ▼
              │              Meet Transcript      Audio Extraction
              │                    │                    │
              │                    │              Speech-to-Text
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   ▼
                           Meeting Transcript
                                   │
                                   ▼
                         AI Meeting Intelligence
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
             Summary           Decisions         Action Items
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                            Todoist Tasks
                                   │
                                   ▼
                            Telegram Alerts
                                   │
                                   ▼
                           Reports / Exports
```

---

# 📁 Project Structure

```text
AI Meeting/
│
├── meeting_agent.py
├── utils.py
├── google_meet.py
├── transcriber.py
│
├── requirements.txt
│
├── .env
├── .env.example
├── .gitignore
│
├── credentials.json
│
└── google_token.json
```

### `meeting_agent.py`

Main Streamlit application.

Responsible for:

- UI
- Meeting configuration
- Meeting preparation
- Google Meet controls
- Recording uploads
- Intelligence generation
- Q&A
- Todoist workflow
- Reports
- Exports

---

## `utils.py`

Contains reusable integrations and meeting-processing utilities.

Major components include:

```text
TodoistTools
TranscriptExtractor
TelegramCommunicator
TaskExtractor
TodoistMeetingManager
```

---

## `google_meet.py`

Handles Google Meet API functionality.

Responsibilities include:

- Google OAuth
- Credential management
- Meet URL/code handling
- Conference lookup
- Transcript retrieval
- Transcript entry retrieval
- Recording/artifact handling

---

## `transcriber.py`

Handles uploaded meeting recording transcription.

Responsibilities include:

- Audio extraction
- FFmpeg integration
- File chunking
- OpenAI transcription
- Transcript combination

---

## `requirements.txt`

Contains Python dependencies required by the application.

---

## `.env.example`

Template for environment variables.

Do not put production secrets into this file.

---

## `.env`

Your real local credentials.

This file must never be committed to GitHub.

---

## `credentials.json`

Google OAuth Desktop Client JSON downloaded from Google Cloud.

This must remain private.

---

## `google_token.json`

Generated after successful Google OAuth authentication.

This must remain private.

---

# 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application UI |
| Google Meet API | Meeting/conference/transcript access |
| Google Drive API | Meeting artifacts/recording access |
| Google OAuth | Google account authorization |
| Gemini | Optional text-analysis LLM |
| OpenAI | Recording transcription and optional chat analysis |
| Todoist REST API | Task management |
| Telegram Bot API | Team notifications |
| scikit-learn | Local TF-IDF retrieval |
| pandas | Data processing |
| pypdf | PDF processing |
| FFmpeg | Audio/video processing |

---

# 💻 Requirements

Recommended:

```text
Python 3.11+
Python 3.12 recommended
Windows / macOS / Linux
Internet connection
```

For uploaded video/audio transcription:

```text
FFmpeg
```

You also need API credentials for the integrations you want to use.

---

# 📦 Installation

## 1. Clone or copy the project

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Meeting
```

Or simply place the downloaded project folder somewhere on your computer.

---

# 2. Create a virtual environment

For Windows:

```powershell
python -m venv .aienv
```

Activate it:

```powershell
.aienv\Scripts\Activate.ps1
```

If you already have an environment:

```powershell
.aienv\Scripts\activate
```

---

# 3. Verify Python

```powershell
python --version
```

Recommended:

```text
Python 3.12.x
```

Also verify:

```powershell
where python
```

The first path should point to your `.aienv` environment.

---

# 4. Install dependencies

```powershell
pip install -r requirements.txt
```

Upgrade pip if necessary:

```powershell
python -m pip install --upgrade pip
```

---

# 🎙️ FFmpeg Installation

FFmpeg is required for video/audio processing.

Verify:

```powershell
ffmpeg -version
```

If Windows says:

```text
ffmpeg is not recognized
```

install FFmpeg and add its `bin` directory to your system PATH.

Then reopen VS Code/PowerShell and run:

```powershell
ffmpeg -version
```

again.

---

# 🔐 Environment Variables

Create:

```text
.env
```

in the project root.

Example:

```env
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=your_openai_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TRANSCRIBE_MODEL=gpt-4o-transcribe

TODOIST_API_KEY=your_todoist_token

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

GOOGLE_OAUTH_CLIENT_SECRET_FILE=credentials.json
GOOGLE_OAUTH_TOKEN_FILE=google_token.json
```

The application also supports the legacy variable names used in the original project where applicable.

---

# 🟢 Gemini

Gemini is used for text-analysis functionality when:

```env
GEMINI_API_KEY=...
```

is configured.

Model:

```env
GEMINI_MODEL=gemini-2.5-flash
```

can be changed to a supported Gemini model available to your account/API.

---

# 🟣 OpenAI

OpenAI is primarily used for uploaded audio/video transcription.

```env
OPENAI_API_KEY=...
```

Example:

```env
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TRANSCRIBE_MODEL=gpt-4o-transcribe
```

If you do not configure an OpenAI key, uploaded-recording transcription will not work through the OpenAI transcription pipeline.

---

# 📋 Todoist Setup

Create/access a Todoist API token from your Todoist developer/account settings.

Add:

```env
TODOIST_API_KEY=your_token
```

The application can then:

- Create projects
- Create tasks
- Find projects
- Match collaborators
- Set due dates
- Set priorities

---

# 📲 Telegram Setup

Create a Telegram bot using BotFather.

Get:

```text
Bot Token
```

Then identify the target chat/group ID.

Add:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Make sure your bot has permission to send messages to the target chat/group.

---

# ☁️ Google Meet OAuth Setup

Google Meet access is different from an API key.

You need:

```text
credentials.json
```

This is an OAuth Desktop application credential.

---

## Step 1 — Create Google Cloud Project

Open:

```text
https://console.cloud.google.com/
```

Create or select a project.

Example:

```text
AI Meeting Assistant
```

---

## Step 2 — Enable APIs

Enable the APIs required by your workflow, including:

```text
Google Meet REST API
Google Drive API
```

---

## Step 3 — Configure OAuth

Open Google Auth Platform in Google Cloud Console.

Configure:

- App name
- Support email
- Developer contact
- Audience
- Test users if required

For a personal Google account, the OAuth application will generally be configured for external testing rather than an internal-only Workspace application.

---

## Step 4 — Create OAuth Client

Create an OAuth Client ID with application type:

```text
Desktop app
```

Download the JSON.

Rename it:

```text
credentials.json
```

Place it in the project root:

```text
AI Meeting/
│
├── meeting_agent.py
├── google_meet.py
├── credentials.json
└── ...
```

---

# 🔑 `google_token.json`

You do **not** manually create this file.

The first time the application authenticates with Google:

```text
credentials.json
       ↓
OAuth login
       ↓
User grants permission
       ↓
Access/refresh token
       ↓
google_token.json
```

After that, the application can reuse the stored authorization until it needs to be re-authorized.

---

# ▶️ Running the Application

Activate your environment:

```powershell
.aienv\Scripts\Activate.ps1
```

Then:

```powershell
streamlit run meeting_agent.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

If it doesn't open automatically, copy the Local URL shown in the terminal into your browser.

---

# 🖥️ Application Sections

The application is organized into:

```text
1. Meeting Setup
2. Live Meet
3. Recording
4. Intelligence
5. Q&A
6. Tasks
7. Reports
```

Each section handles a different stage of the meeting lifecycle.

---

# 1️⃣ Meeting Setup

Enter:

### Company / client

Example:

```text
TechNova Solutions
```

### Meeting objective

```text
Discuss the launch of an AI-powered customer support platform,
finalize MVP requirements, assign responsibilities, and agree on
the launch timeline.
```

### Attendees

Example:

```text
Rahul Sharma - Project Manager - TechNova Solutions
Priya Mehta - AI Engineer - TechNova Solutions
Arjun Kapoor - Marketing Manager - TechNova Solutions
Sarah Wilson - Client Representative - ABC Enterprises
```

### Focus areas

```text
MVP features
AI chatbot accuracy
CRM integration
Budget
Marketing strategy
Launch deadline
Team responsibilities
Technical risks
```

Upload relevant PDFs/TXT documents if available.

Then click:

```text
Prepare Meeting
```

---

# 2️⃣ Live Meet

Enter:

```text
Google Meet URL
```

or the meeting code.

Example:

```text
abc-defg-hij
```

Authenticate Google if required.

The application can then:

- Find the meeting/conference
- Retrieve transcript information
- Capture new transcript entries
- Display speaker/timestamp information
- Load the complete transcript after the meeting

---

# 3️⃣ Recording

Upload a meeting recording.

Examples:

```text
meeting.mp3
meeting.wav
meeting.m4a
meeting.mp4
meeting.webm
```

For your first test, use a short 1–3 minute recording.

The application will:

```text
Upload
  ↓
Validate
  ↓
Extract audio if necessary
  ↓
Chunk
  ↓
Transcribe
  ↓
Combine
  ↓
Display transcript
```

---

# 4️⃣ Intelligence

After a transcript exists, run the meeting intelligence workflow.

Expected outputs include:

```text
Executive Summary
Key Discussion Points
Decisions
Action Items
Owners
Deadlines
Priorities
Risks / Blockers
Open Questions
Follow-up Topics
Client / Customer Signals
Next Meeting Agenda
Follow-up Email
```

---

# 5️⃣ Q&A

Ask questions against your meeting material.

Example:

```text
What were the key decisions?
```

```text
Who owns the AI chatbot?
```

```text
What is the launch deadline?
```

```text
What risks were discussed?
```

```text
What was the client's main concern?
```

The retrieval layer uses local TF-IDF search over the available meeting content.

---

# 6️⃣ Tasks

Action items extracted from the meeting can be sent to Todoist.

Example transcript:

```text
Priya will build the AI chatbot by Friday.

Arjun will prepare the marketing campaign by next Wednesday.

Rahul will coordinate the engineering team.
```

Expected tasks:

```text
Build AI chatbot
Prepare marketing campaign
Coordinate engineering team
```

---

# 7️⃣ Reports

Generate and download meeting outputs.

Typical files:

```text
meeting_transcript.txt
meeting_analysis.json
meeting_report.md
structured_transcript.json
```

These can be stored in your project archive or uploaded to another company knowledge system later.

---

# 🧪 Testing Guide

The safest way to test the application is feature-by-feature.

---

## Test 1 — Meeting Preparation

Use:

```text
Company:
TechNova Solutions

Objective:
Discuss the launch of a new AI-powered customer support platform,
finalize MVP scope, assign responsibilities, and agree on the launch timeline.

Attendees:
Rahul Sharma - Project Manager
Priya Mehta - AI Engineer
Arjun Kapoor - Marketing Manager

Focus:
MVP
AI chatbot
CRM integration
Budget
Marketing
Launch deadline
```

Click:

```text
Prepare Meeting
```

Verify that the preparation sections are generated.

---

# Test 2 — Document Q&A

Create:

```text
project_requirements.txt
```

with:

```text
Project Requirements

The AI customer support platform must support:

1. Customer question answering.
2. CRM integration.
3. Automatic ticket creation.
4. Customer sentiment detection.
5. Human agent escalation.
6. Analytics dashboard.

The MVP must be completed within 6 weeks.

Engineering is responsible for the AI system and CRM integration.

Marketing is responsible for the launch campaign.

The estimated project budget is $25,000.
```

Upload it.

Ask:

```text
What are the MVP requirements?
```

Then:

```text
What is the project deadline?
```

Then:

```text
What is the estimated budget?
```

---

# Test 3 — Hallucination / Grounding

Ask:

```text
What is the company's Tokyo office address?
```

If the information isn't in your documents, the system should not invent a specific address.

---

# Test 4 — Recording Transcription

Use a short meeting recording.

Example spoken content:

```text
We need to launch the AI customer support MVP by October 30.

Priya will build the AI chatbot by Friday.

Arjun will prepare the marketing campaign by next Wednesday.

We also need Salesforce integration.

Let's review the progress next Monday.
```

Upload it.

Verify the transcript.

---

# Test 5 — Meeting Intelligence

Use the resulting transcript.

Verify that the system identifies:

```text
Launch deadline
AI chatbot task
Marketing task
Salesforce integration
Progress review
```

---

# Test 6 — Todoist

Send the extracted action items to Todoist.

Verify that the project and tasks appear in your Todoist account.

---

# Test 7 — Telegram

Send the meeting task notification.

Verify that your Telegram chat receives the task summary.

---

# Test 8 — Google Meet

Create a test Google Meet.

Enable/allow meeting transcription according to your Google Workspace/Meet configuration.

Say:

```text
Priya will complete the AI chatbot by Friday.

Arjun will prepare the marketing campaign.

Rahul will coordinate the engineering team.

The MVP launch target is October 30.
```

Then retrieve the transcript.

Verify:

```text
Speaker
Timestamp
Transcript
```

---

# 🔁 Recommended End-to-End Test

After individual components work, test the complete pipeline:

```text
Google Meet
     ↓
Transcript
     ↓
Meeting Intelligence
     ↓
Action Items
     ↓
Todoist
     ↓
Telegram
     ↓
Final Report
```

This is the most important integration test.

---

# 🎙️ Recording Transcription Details

For uploaded video:

```text
MP4
 ↓
FFmpeg
 ↓
Audio
 ↓
Chunking
 ↓
OpenAI transcription
 ↓
Combined transcript
```

Long recordings are split into manageable chunks to avoid sending an unnecessarily large audio file in a single request.

The resulting chunks are combined in their original order.

---

# 🎥 Google Meet Live Transcription Details

The live workflow uses Google Meet transcript entries.

Conceptually:

```text
Meeting starts
     ↓
Google Meet generates transcript
     ↓
Application polls transcript entries
     ↓
Application identifies new entries
     ↓
New entries are displayed
     ↓
Transcript is accumulated
```

This should not be confused with raw audio capture.

For raw real-time audio/video streaming, Google provides separate media capabilities with different access requirements.

---

# 🧠 AI Meeting Intelligence Pipeline

The intelligence pipeline is designed around structured information extraction.

```text
Raw transcript
      ↓
Cleaning
      ↓
LLM analysis
      ↓
Structured meeting intelligence
      ↓
Action item extraction
      ↓
Owner/deadline extraction
      ↓
External task creation
```

A useful mental model is:

```text
LLM = Understanding
Todoist = Execution
Telegram = Communication
Streamlit = Control Center
Google Meet = Meeting Source
```

---

# 📋 Todoist Workflow

```text
Transcript
   ↓
Task extraction
   ↓
Project identification
   ↓
Task identification
   ↓
Owner identification
   ↓
Due-date identification
   ↓
Todoist project
   ↓
Todoist task
```

Where possible, the system can match an extracted owner against Todoist collaborators.

---

# 📲 Telegram Workflow

```text
Meeting
   ↓
Action items
   ↓
Todoist
   ↓
Task summary
   ↓
Telegram
```

Telegram should be treated as a notification channel rather than the system of record for tasks.

---

# 🔐 Security

## Never commit secrets

Do not commit:

```text
.env
credentials.json
google_token.json
```

Your `.gitignore` should contain:

```gitignore
.env
credentials.json
google_token.json
__pycache__/
*.pyc
.venv/
.aienv/
```

---

## API keys

Never write:

```python
OPENAI_API_KEY = "sk-..."
```

inside Python files.

Use:

```env
OPENAI_API_KEY=...
```

instead.

---

## Important credential rotation

If a real API key/token has ever been posted publicly, shared in screenshots, committed to GitHub, or pasted into an AI/chat service, treat it as exposed.

Revoke/rotate it from the corresponding provider and replace it in your local `.env`.

---

# ⚠️ Privacy Considerations

Meeting transcripts may contain:

- Customer information
- Employee information
- Financial information
- Business strategy
- Confidential product information
- Internal discussions

Before using this application with real company meetings, establish the organization's requirements for:

- Consent
- Recording
- Data retention
- Access control
- Vendor/API processing
- Confidential information
- Employee privacy
- Customer privacy

Do not assume that because an API technically accepts a transcript, the organization is automatically permitted to process that transcript.

---

# 🛠️ Troubleshooting

## Streamlit doesn't start

Run:

```powershell
python -m streamlit run meeting_agent.py
```

instead of:

```powershell
streamlit run meeting_agent.py
```

---

## `ModuleNotFoundError`

Activate the environment:

```powershell
.aienv\Scripts\Activate.ps1
```

Then:

```powershell
pip install -r requirements.txt
```

---

## Check installed Python

```powershell
python --version
where python
```

---

## Google OAuth doesn't work

Check:

```text
credentials.json
```

exists in the project root.

Also verify:

- Google Meet API enabled
- Google Drive API enabled
- OAuth client type is Desktop
- Correct Google account is being used
- Test user is configured if the application is in testing mode

If an old token is invalid, remove the local:

```text
google_token.json
```

and authenticate again.

---

## Google Meet transcript is empty

Possible reasons include:

- Meeting transcription wasn't enabled
- Transcript isn't available yet
- The authenticated account doesn't have access
- The account isn't the organizer/authorized user
- Google Workspace configuration restricts the feature
- The conference has no generated transcript
- The transcript has not propagated through the API yet

Wait briefly and retry before assuming the integration is broken.

---

## Recording transcription fails

Check:

```powershell
ffmpeg -version
```

Then verify:

```env
OPENAI_API_KEY=...
```

Also test with a short recording first.

---

## Todoist tasks aren't created

Check:

```env
TODOIST_API_KEY=...
```

Then verify the token is valid and the account has access to the Todoist API.

---

## Todoist assignment doesn't work

The extracted owner must match a Todoist collaborator where collaborator assignment is being used.

For example:

```text
Transcript:
Priya Mehta will build the chatbot.
```

Todoist must have an appropriate collaborator that can be matched to:

```text
Priya Mehta
```

---

## Telegram notification fails

Check:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Verify that:

- Bot exists
- Token is valid
- Bot can access the target chat
- Chat ID is correct
- Bot has permission to send messages

---

# ⚠️ Known Limitations

## 1. Google Meet live transcription is not raw audio streaming

The application retrieves Google Meet transcript information.

It does not directly intercept the microphone/audio stream.

---

## 2. Google Meet permissions matter

A valid OAuth login does not automatically mean every meeting or transcript is accessible.

The Google account must have appropriate permissions and the relevant Meet artifacts must exist.

---

## 3. Transcript availability can be delayed

Google Meet may require time to generate or expose transcript information.

---

## 4. AI extraction isn't guaranteed to be perfect

LLMs can misunderstand:

- Ambiguous owners
- Relative dates
- Multiple people with similar names
- Implied decisions
- Sarcasm
- Unclear commitments

External actions such as task creation should therefore be reviewed in a production workflow.

---

## 5. Todoist assignment requires matching collaborators

An extracted person's name does not automatically create a Todoist account or collaborator.

---

## 6. Local TF-IDF retrieval is not a full enterprise vector database

The Q&A system is intentionally lightweight.

For a production deployment, consider:

```text
pgvector
Qdrant
Pinecone
Weaviate
Chroma
FAISS
```

depending on scale and architecture.

---

# 🏭 Production Architecture

For a serious company deployment, Streamlit should eventually become the control interface rather than the entire backend.

A stronger architecture would be:

```text
                    Google Meet
                         │
                         ▼
                 Meeting Ingestion
                         │
                         ▼
                  Queue / Worker
                         │
                         ▼
                  Transcript Store
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Summary Agent  Decision Agent  Task Agent
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  Human Approval
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
         Todoist      Telegram       Email
            │            │            │
            └────────────┼────────────┘
                         ▼
                    Audit Log
                         │
                         ▼
                    Analytics
```

---

# 🔮 Future Enhancements

Potential future versions can add:

## Communication

- Slack integration
- Microsoft Teams
- Email follow-up
- WhatsApp Business API

## Calendar

- Google Calendar
- Outlook Calendar
- Automatic next-meeting scheduling

## CRM

- Salesforce
- HubSpot
- Zoho CRM

## Storage

- Google Drive
- Google Cloud Storage
- AWS S3
- Azure Blob Storage

## AI

- Speaker-aware summarization
- Sentiment/interaction analysis with appropriate safeguards
- Meeting quality metrics
- Customer objection extraction
- Sales opportunity extraction
- Competitive intelligence
- Automatic follow-up generation
- Company knowledge RAG
- Multi-agent workflows

## Enterprise

- User authentication
- Role-based access
- Organization/workspace separation
- Audit logs
- Encryption
- Database persistence
- Background workers
- Job queues
- Retry mechanisms
- Monitoring
- Usage analytics

---

# 🤖 Possible Future Agent Architecture

A more advanced version could split the intelligence into specialized agents:

```text
                    Meeting Transcript
                           │
                           ▼
                  ┌─────────────────┐
                  │ Orchestrator    │
                  └────────┬────────┘
                           │
       ┌───────────────────┼────────────────────┐
       ▼                   ▼                    ▼
 Context Agent        Decision Agent       Task Agent
       │                   │                    │
       ▼                   ▼                    ▼
 Risk Agent          Follow-up Agent       CRM Agent
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                    Human Approval
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Todoist       Telegram       Email
```

This architecture can make the system more modular and easier to scale.

---

# 📈 Scaling Considerations

For small personal/team usage:

```text
Streamlit
+
Python
+
APIs
```

is sufficient.

For larger organizations:

```text
Frontend
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
Redis / Queue
   ↓
Background Workers
   ↓
LLM Providers
   ↓
External Integrations
```

should be considered.

---

# 🧪 Recommended Testing Strategy

Use three stages.

## Stage 1 — Unit Testing

Test:

- Transcript parsing
- JSON parsing
- Task extraction
- Todoist project creation
- Telegram message generation
- Audio conversion

## Stage 2 — Integration Testing

Test:

```text
Google Meet → Transcript
Transcript → AI
AI → Todoist
Todoist → Telegram
```

## Stage 3 — End-to-End Testing

Run:

```text
Real Meeting
     ↓
Real Transcript
     ↓
AI Analysis
     ↓
Human Review
     ↓
Todoist
     ↓
Telegram
     ↓
Report
```

Use a test meeting and test credentials before connecting production company accounts.

---

# 🌐 GitHub Deployment

Before pushing to GitHub:

```powershell
git status
```

Verify that you do **not** see:

```text
.env
credentials.json
google_token.json
```

Then:

```powershell
git add .
git commit -m "Initial AI Meeting Command Center"
git push
```

Your repository should contain:

```text
meeting_agent.py
utils.py
google_meet.py
transcriber.py
requirements.txt
.env.example
.gitignore
README.md
```

but not your secrets.

---

# 📝 Example `.env.example`

Use placeholders:

```env
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=your_openai_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TRANSCRIBE_MODEL=gpt-4o-transcribe

TODOIST_API_KEY=your_todoist_token_here

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

GOOGLE_OAUTH_CLIENT_SECRET_FILE=credentials.json
GOOGLE_OAUTH_TOKEN_FILE=google_token.json
```

---

# 🚀 Quick Start

For an experienced user:

```powershell
# 1. Activate environment
.aienv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env

# 4. Put Google OAuth file here
# credentials.json

# 5. Optional: verify FFmpeg
ffmpeg -version

# 6. Start application
streamlit run meeting_agent.py
```

Then open:

```text
http://localhost:8501
```

---

# 🧩 Quick Architecture Summary

```text
┌─────────────────────────────────────────────────────┐
│              AI MEETING COMMAND CENTER              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  PRE-MEETING                                        │
│  ├── Company context                                │
│  ├── Objectives                                     │
│  ├── Attendees                                      │
│  ├── Documents                                      │
│  └── Meeting strategy                               │
│                                                     │
│  DURING MEETING                                     │
│  ├── Google Meet                                    │
│  └── Transcript capture                            │
│                                                     │
│  AFTER MEETING                                      │
│  ├── Recording transcription                       │
│  ├── Summary                                        │
│  ├── Decisions                                      │
│  ├── Action items                                   │
│  ├── Risks                                          │
│  └── Follow-up                                      │
│                                                     │
│  AUTOMATION                                         │
│  ├── Todoist                                        │
│  ├── Telegram                                       │
│  └── Reports                                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

# 💼 Business Use Cases

This architecture can be adapted for:

### Sales Meetings

Extract:

- Customer requirements
- Objections
- Follow-ups
- Opportunities
- Next actions

### Project Meetings

Extract:

- Tasks
- Owners
- Deadlines
- Blockers
- Decisions

### Client Meetings

Extract:

- Requirements
- Change requests
- Commitments
- Concerns
- Follow-up actions

### Management Meetings

Extract:

- Decisions
- Strategic priorities
- Risks
- Ownership
- Next steps

### Internal Team Meetings

Extract:

- Team tasks
- Dependencies
- Deadlines
- Open questions

---

# 📌 Project Objective

The long-term objective of this project is to move from a simple AI meeting summarizer toward a **Meeting Operations Assistant**.

The desired lifecycle is:

```text
                 ┌───────────────┐
                 │ Before Meeting│
                 └───────┬───────┘
                         ↓
                  Prepare Brief
                         ↓
                 ┌───────────────┐
                 │ During Meeting│
                 └───────┬───────┘
                         ↓
                    Transcript
                         ↓
                 ┌───────────────┐
                 │ After Meeting │
                 └───────┬───────┘
                         ↓
                   Intelligence
                         ↓
                  Action Items
                         ↓
                 Human Approval
                         ↓
                ┌────────┴────────┐
                ↓                 ↓
             Todoist          Telegram
                ↓                 ↓
                └────────┬────────┘
                         ↓
                    Follow-up
```

---

# 👨‍💻 Author

**Ankit Kumar Jha**

B.Tech Computer Science Engineering

AI / Machine Learning / Agentic AI / Automation Developer

---

# ⭐ Project Highlights

This project demonstrates practical implementation of:

- Generative AI
- LLM-based information extraction
- Agentic workflows
- Meeting intelligence
- Retrieval-Augmented Q&A
- Google APIs
- OAuth authentication
- Speech-to-text
- Audio/video processing
- Task automation
- Notification automation
- API integrations
- Streamlit application development
- Environment-based secret management

---

# 📜 License

Add the license that you intend to use before publishing the repository publicly.

For example:

```text
MIT License
```

if you choose MIT.

---

# ⚠️ Disclaimer

This project is an engineering/automation application.

AI-generated summaries, decisions, tasks, deadlines, and extracted information should be reviewed by a human before they are used for consequential business actions.

The application should not automatically make important business decisions solely from an AI-generated interpretation of a meeting.

---

# 🎉 Final Workflow

The complete vision of the project is:

```text
                 🤝 MEETING
                     │
                     ▼
             📝 PREPARATION
                     │
                     ▼
             🎥 GOOGLE MEET
                     │
                     ▼
              🎙️ TRANSCRIPT
                     │
                     ▼
             🧠 AI ANALYSIS
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Summary     Decisions     Tasks
        │            │            │
        │            │            ▼
        │            │         Todoist
        │            │            │
        │            │            ▼
        │            │         Telegram
        │            │
        └────────────┼────────────┐
                     ▼            │
                📊 REPORT        │
                     │            │
                     └──────┬─────┘
                            ▼
                     📧 FOLLOW-UP
                            │
                            ▼
                     📅 NEXT MEETING
```

**AI Meeting Command Center** is designed to turn meetings from passive conversations into structured, trackable and actionable workflows.
