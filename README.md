# Lead Qualification and Scheduling Pipeline

AI-powered voice bot for automated lead qualification with intelligent scheduling and Microsoft Outlook Calendar integration. Features natural language processing, voice activity detection, and a modern web dashboard for lead management.

## 🎯 Features

- **🤖 AI Voice Agent** - Natural conversation flow with Voice Activity Detection (VAD)
- **📊 Lead Qualification** - Automated lead scoring and comprehensive data collection
- **📅 Smart Scheduling** - Microsoft Outlook automatic calendar scheduling with round-robin assignment
- **🎨 Modern Dashboard** - React + TypeScript web interface for lead management
- **🎙️ Call Recording** - Audio storage with MongoDB GridFS
- **📝 Conversation Transcripts** - Full text logs of all conversations
- **🔄 Token Caching** - No repeated authentication for calendar integration

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Voice Bot  │────▶│  Groq LLM    │────▶│  Database   │
│  (VAD)      │     │  (llama-3.3) │     │  (MongoDB)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                          │
       │            ┌──────────────┐             │
       └───────────▶│  Deepgram    │             │
                    │  (STT + TTS) │             │
                    └──────────────┘             │
                                                  │
┌─────────────┐     ┌──────────────┐            │
│   Calendar  │────▶│  Microsoft   │            │
│  Manager    │     │  Graph API   │            │
└─────────────┘     └──────────────┘            │
                                                  │
┌─────────────┐     ┌──────────────┐            │
│  Dashboard  │────▶│ Flask Server │◀───────────┘
│  (React)    │     │   (API)      │
└─────────────┘     └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for dashboard development)
- MongoDB Atlas account
- Microsoft Azure account (for calendar integration)
- Groq API key
- Deepgram API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/DalMakkhani/Lead-Qualification-and-Scheduling-Pipeline.git
cd Lead-Qualification-and-Scheduling-Pipeline
```

2. **Set up Python environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install flask pymongo python-dotenv requests msal groq deepgram-sdk pyaudio wave webrtcvad flask-cors
```

3. **Configure environment variables**

Create a `.env` file in the project root:

```env
# AI APIs
GROQ_API_KEY=your_groq_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# MongoDB
MONGODB_URI=your_mongodb_connection_string_here

# Microsoft Azure Calendar Integration
MICROSOFT_CLIENT_ID=your_azure_client_id_here
MICROSOFT_CLIENT_SECRET=your_azure_client_secret_here
MICROSOFT_TENANT_ID=your_azure_tenant_id_here
MICROSOFT_REDIRECT_URI=http://localhost:5000/auth/callback

# Bot Configuration
BOT_EMAIL=your_bot_email@gmail.com
SALES_EXECUTIVES=executive1@email.com:Executive Name,executive2@email.com:Executive Name
```

4. **Start the server**
```bash
python server.py
```

Server runs on: `http://localhost:5000`

## 📋 Detailed Setup Instructions

### 1. MongoDB Atlas Setup

#### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new cluster (M0 Free tier is sufficient)

#### Step 2: Create Database
1. Click "Browse Collections"
2. Click "Add My Own Data"
3. Database name: `lead_qualification_db`
4. Collection name: `leads`

#### Step 3: Get Connection String
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Select "Python" and version "3.12 or later"
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:<password>@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add this to your `.env` file as `MONGODB_URI`

#### Step 4: Configure Network Access
1. Go to "Network Access" in Atlas
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (0.0.0.0/0) for development
4. Click "Confirm"

#### Step 5: Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Set username and password (use these in connection string)
5. Set role to "Read and write to any database"
6. Click "Add User"

### 2. Microsoft Graph API Setup (Calendar Integration)

#### Step 1: Create Azure Account
1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign up or sign in with Microsoft account

#### Step 2: Register Application
1. Go to "Azure Active Directory" (or "Microsoft Entra ID")
2. Click "App registrations" → "New registration"
3. Fill in details:
   - **Name**: Lead Qualification Bot
   - **Supported account types**: "Accounts in any organizational directory and personal Microsoft accounts"
   - **Redirect URI**: Select "Web" and enter `http://localhost:5000/auth/callback`
4. Click "Register"

#### Step 3: Get Application Credentials
1. On the app overview page, copy:
   - **Application (client) ID** → `MICROSOFT_CLIENT_ID` in `.env`
   - **Directory (tenant) ID** → `MICROSOFT_TENANT_ID` in `.env`

2. Go to "Certificates & secrets"
3. Click "New client secret"
4. Add description: "Lead Bot Secret"
5. Set expiry (24 months recommended)
6. Click "Add"
7. **Copy the secret VALUE immediately** → `MICROSOFT_CLIENT_SECRET` in `.env`
   ⚠️ You can't see this again!

#### Step 4: Configure API Permissions
1. Go to "API permissions"
2. Click "Add a permission"
3. Choose "Microsoft Graph"
4. Select "Delegated permissions"
5. Add these permissions:
   - `Calendars.ReadWrite` - Create calendar events
   - `Mail.Send` - Send email reminders
   - `User.Read` - Read user profile
6. Click "Add permissions"
7. Click "Grant admin consent" (if you're admin) or ask your admin

#### Step 5: Configure Authentication
1. Go to "Authentication"
2. Under "Advanced settings" → "Allow public client flows"
3. Set to "Yes"
4. Click "Save"

### 3. Groq API Setup

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up for an account
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Name it "Lead Qualification Bot"
6. Copy the key → `GROQ_API_KEY` in `.env`

### 4. Deepgram API Setup

1. Go to [Deepgram Console](https://console.deepgram.com/)
2. Sign up for an account (free tier available)
3. Navigate to "API Keys"
4. Click "Create a New API Key"
5. Name it "Lead Bot"
6. Copy the key → `DEEPGRAM_API_KEY` in `.env`

### 5. Bot Email Configuration

1. Create a Gmail account for the bot (e.g., `leadbot@gmail.com`)
2. Add to `.env`: `BOT_EMAIL=leadbot@gmail.com`
3. This email will be used as the calendar organizer

### 6. Sales Executives Configuration

Add your sales team emails to `.env`:
```env
SALES_EXECUTIVES=john@company.com:John Doe,sarah@company.com:Sarah Smith
```

Format: `email:Name,email:Name,...`

The bot will use round-robin assignment to distribute leads.

## 🎮 Usage

### Running the Voice Bot

**Text Mode (keyboard input):**
```bash
python groqEleveLabsTalker_VAD.py "Lead Name" "Company Name"
```

**Voice Mode (microphone input):**
```bash
python groqEleveLabsTalker_VAD.py "Lead Name" "Company Name" --voice
```

### Accessing the Dashboard

1. Start the server: `python server.py`
2. Open browser: `http://localhost:5000`
3. View leads, recordings, and transcripts

### Calendar Integration Flow

1. First time: Bot will show device code
2. Visit the URL and enter the code
3. Sign in with Microsoft account
4. Grant permissions
5. Token is cached - no re-authentication needed!

## 📁 Project Structure

```
Lead-Qualification-and-Scheduling-Pipeline/
├── server.py                      # Flask server (API + Dashboard)
├── groqEleveLabsTalker_VAD.py    # Voice bot with VAD
├── database.py                    # MongoDB operations
├── calendar_manager.py            # Outlook calendar integration
├── dashboard/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── types/
│   ├── dist/                      # Built static files
│   └── package.json
├── .env                           # Environment configuration (DO NOT COMMIT)
└── README.md                      # This file
```

## 🔧 Technology Stack

### Backend
- Python 3.12, Flask 3.1.2, MongoDB Atlas, Microsoft Graph API, MSAL

### AI/ML
- Groq (llama-3.3-70b), Deepgram (STT+TTS), WebRTC VAD

### Frontend
- React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui

## 📊 Database Schema

```json
{
  "lead_name": "string",
  "company_name": "string",
  "contact_info": {
    "phone": "string",
    "email": "string"
  },
  "call_metadata": {
    "timestamp": "datetime",
    "call_outcome": "qualified | not_interested | ...",
    "duration_seconds": "number",
    "audio_recording_id": "ObjectId"
  },
  "requirement": { },
  "conversation_transcript": "string",
  "scheduled_call": { }
}
```

## 🔌 API Endpoints

- `GET /api/health` - Server health
- `GET /api/leads` - All leads (with filters)
- `GET /api/leads/<id>` - Specific lead
- `GET /api/audio/<id>` - Audio recording

## 🐛 Troubleshooting

**MongoDB timeout:** Check IP whitelist in Atlas  
**Calendar auth fails:** Verify Azure redirect URI and permissions  
**White screen:** Hard refresh browser (Ctrl+Shift+R)

## 📝 License

All rights reserved. Proprietary software.

## 👤 Author

Arjun Mirabballi

---

**Version:** 1.0.0  
**Last Updated:** January 22, 2026
