# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+ with pip
- Node.js 20.0.0+ with npm
- Gemini API Key (from Google AI Studio)

## ⚙️ Setup (One-time)

### 1. Environment Variables
Your `.env` file is already configured in the root directory:
```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.5-flash-lite
```

### 2. Virtual Environment (Already exists)
The Python virtual environment (`.venv`) is already set up in the root directory.

### 3. Install dependencies

```powershell
cd "F:\Code\Final Year Project"
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\ai_engine\requirements.txt
```

For an NVIDIA RTX 50-series GPU:

```powershell
python -m pip install --upgrade torch --index-url https://download.pytorch.org/whl/cu130
```

The trained model artifacts are included in `ai_engine/models/`. Install Git
LFS before cloning so the fine-tuned DistilBERT weights are downloaded.

### 4. Dependencies
- `ai_engine/`: Python dependencies installed via pip
- `server/`: Node dependencies in `node_modules`
- `client/`: Node dependencies in `node_modules`

---

### 5. Optional: retrain both models

```powershell
cd "F:\Code\Final Year Project\ai_engine"
python .\train.py
python .\fine_tune_distilbert.py `
  --fake ".\model_traning\fake_account.csv" `
  --legitimate ".\model_traning\legitimate_account.csv" `
  --max-samples-per-class 20000 `
  --epochs 3 `
  --batch-size 16
```

`train.py` saves the production XGBoost model and
`models\xgboost_experiments.json`. The fine-tuning script saves the
DistilBERT checkpoint to `models\distilbert-finetuned`.

---

## 🎯 Running the Project

Open **3 separate PowerShell terminals** and run these commands:

### Terminal 1: AI Engine (FastAPI)
```powershell
cd "F:\Code\Final Year Project"
.\.venv\Scripts\Activate.ps1
cd .\ai_engine
python main.py
```
✅ Runs on: **http://localhost:8000**

### Terminal 2: Server (Express Gateway)
```powershell
cd "f:\Code\Final Year Project\server"
npm start
```
✅ Runs on: **http://localhost:3000**

### Terminal 3: Client (React)
```powershell
cd "f:\Code\Final Year Project\client"
npm run dev
```
✅ Runs on: **http://localhost:5173**

---

## 📍 Access the Application
Open your browser and navigate to:
```
http://localhost:5173
```

---

## 📊 Architecture

| Component | Port | Tech Stack | Purpose |
|-----------|------|-----------|---------|
| **AI Engine** | 8000 | Python/FastAPI | ML model inference (XGBoost + DistilBERT) |
| **Server** | 3000 | Node.js/Express | API gateway & Gemini integration |
| **Client** | 5173 | React/Vite | Web UI |

---

## 🔧 Useful Commands

### Install/Update Dependencies
```powershell
# AI Engine (Python)
cd ai_engine
pip install -r requirements.txt

# Server (Node)
cd server
npm install

# Client (Node)
cd client
npm install
```

### Development Mode
```powershell
# Server (with watch mode)
cd server
npm run dev

# Client (already in dev mode with Vite)
cd client
npm run dev
```

### Build for Production
```powershell
# Client
cd client
npm run build
```

---

## ⚠️ Troubleshooting

### "GEMINI_API_KEY is not set"
- Check `.env` file exists in root directory
- Verify the API key is not empty
- The server loads `.env` from the parent directory automatically

### "Cannot connect to AI Engine"
- Ensure Terminal 1 is running and shows "All models loaded – AI Engine ready."
- Verify `http://localhost:8000/health` is accessible

### "port 5173 is already in use"
```powershell
# Kill the process or use a different port
npm run dev -- --port 5174
```

### Python venv not activating
```powershell
cd "f:\Code\Final Year Project"
.\.venv\Scripts\Activate.ps1
```

---

## 📝 Notes
- The AI Engine downloads DistilBERT on first run (~500MB) — be patient
- All three services must be running for the app to work fully
- Environment variables are auto-loaded from `.env` in the root directory
- Check the terminal logs for any errors or issues
