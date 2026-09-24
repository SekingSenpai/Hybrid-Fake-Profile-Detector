# Hybrid Fake Profile Detector

A local full-stack application for analyzing social-media profiles with an
XGBoost profile/behavior model, a DistilBERT text model, and Gemini-generated
reasoning reports.

## Requirements

- Python 3.9 or newer
- Node.js 20 or newer
- npm
- Git
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- At least 8 GB RAM recommended

The first AI Engine start downloads the DistilBERT model from Hugging Face.
Internet access is required for that download and for Gemini reports.

## Clone the repository

```bash
git clone https://github.com/SekingSenpai/Hybrid-Fake-Profile-Detector.git
cd Hybrid-Fake-Profile-Detector
```

The repository includes `ai_engine/models/xgboost_model.pkl`. Do not delete
this file; the AI Engine loads it during startup. DistilBERT is downloaded and
cached automatically.

## Configuration

### Windows PowerShell

```powershell
Copy-Item .env.example .env
notepad .env
```

Set the values in `.env`:

```text
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash
AI_ENGINE_URL=http://localhost:8000
```

### macOS Terminal

```bash
cp .env.example .env
open -e .env
```

Use the same values shown above. Keep `.env` private; it is ignored by Git.

## Windows setup and run

Open three separate PowerShell windows.

### 1. Install Python dependencies

From the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\ai_engine\requirements.txt
```

If PowerShell blocks activation, run this once in an elevated PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2. Install Node dependencies

```powershell
cd server
npm install
cd ..\client
npm install
cd ..
```

### 3. Start the AI Engine

Terminal 1:

```powershell
cd "F:\Code\Final Year Project"
.\.venv\Scripts\Activate.ps1
cd ai_engine
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Wait for `All models loaded - AI Engine ready.` before continuing.

### 4. Start the server

Terminal 2:

```powershell
cd "F:\Code\Final Year Project\server"
npm start
```

The gateway runs at `http://localhost:3000`.

### 5. Start the frontend

Terminal 3:

```powershell
cd "F:\Code\Final Year Project\client"
npm run dev
```

Open `http://localhost:5173`.

## macOS setup and run

Open three separate Terminal windows.

### 1. Install Python dependencies

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ai_engine/requirements.txt
```

### 2. Install Node dependencies

```bash
cd server
npm install
cd ../client
npm install
cd ..
```

### 3. Start the AI Engine

Terminal 1:

```bash
cd /path/to/Hybrid-Fake-Profile-Detector
source .venv/bin/activate
cd ai_engine
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Wait for `All models loaded - AI Engine ready.` before continuing.

### 4. Start the server

Terminal 2:

```bash
cd /path/to/Hybrid-Fake-Profile-Detector/server
npm start
```

The gateway runs at `http://localhost:3000`.

### 5. Start the frontend

Terminal 3:

```bash
cd /path/to/Hybrid-Fake-Profile-Detector/client
npm run dev
```

Open `http://localhost:5173`.

## Service endpoints

| Service | URL |
| --- | --- |
| React client | http://localhost:5173 |
| Express gateway | http://localhost:3000 |
| AI Engine | http://localhost:8000 |
| AI Engine health check | http://localhost:8000/health |

The frontend sends profile analysis requests to the Express gateway at
`POST /analyze`. The gateway calls the AI Engine at `POST /predict` and then
requests a Gemini forensic report. If Gemini is temporarily unavailable, a
fallback report is returned while the local model scores remain available.

## Model notes

The XGBoost model expects these eight features, in order:

1. Profile picture
2. Digit ratio in username
3. Followers
4. Following
5. Account age in days
6. Average likes per post
7. Average comments per post
8. URL ratio

The current DistilBERT checkpoint is the SST-2 sentiment model. Its output is
used as a heuristic fake-risk signal, not as a formally trained fake-profile
probability. Treat results as screening signals rather than definitive
identity or fraud determinations.

## Troubleshooting

- **`GEMINI_API_KEY is not set`**: ensure `.env` is in the repository root and
  restart the server.
- **`getaddrinfo ENOTFOUND ai_engine`**: use
  `AI_ENGINE_URL=http://localhost:8000` for local execution.
- **`Unable to connect to the remote server` on port 8000**: start the AI
  Engine first and wait for model loading to finish.
- **Gemini `503 Service Unavailable`**: the configured model is busy or
  temporarily unavailable. The gateway tries fallback models and returns a
  local fallback report if needed.
- **First startup is slow**: DistilBERT is downloaded and loaded once, then
  reused from the local Hugging Face cache.

## Docker

For containerized execution:

```bash
docker compose up --build
```

Docker uses the service hostname `ai_engine`; local execution uses
`http://localhost:8000`.

## Project structure

```text
ai_engine/       FastAPI, XGBoost, and DistilBERT service
server/          Express gateway and Gemini integration
client/          React/Vite frontend
.env.example     Safe environment-variable template
docker-compose.yml
```
