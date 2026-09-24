# 🎯 Hybrid Fake Profile Detector

A sophisticated ML-powered system for detecting fake social media profiles using a hybrid approach combining XGBoost, DistilBERT, and Gemini AI. Built with FastAPI, Express.js, and React.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Technologies](#technologies)

---

## 🎯 Overview

This project implements a **hybrid fake profile detection system** that combines multiple AI/ML models:

1. **XGBoost Model** - Analyzes 8 tabular features (profile metrics and behavior patterns)
2. **DistilBERT Model** - Analyzes profile bio text for authenticity signals
3. **Gemini AI** - Generates detailed forensic reasoning reports

The system provides a combined probability score and conflict detection when models disagree.

---

## ✨ Features

- ✅ Hybrid ML pipeline (XGBoost + DistilBERT)
- ✅ Real-time profile analysis
- ✅ Gemini AI-powered reasoning reports
- ✅ Conflict detection when models disagree
- ✅ REST API for easy integration
- ✅ Modern React frontend with real-time results
- ✅ Docker support for production deployment
- ✅ Comprehensive logging and error handling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Client (Port 5173)                 │
│                   (Vite + React + Axios)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                Express Gateway (Port 3000)                  │
│              (Node.js + Axios + Gemini SDK)                 │
│  - Receives profile data                                    │
│  - Forwards to AI Engine                                    │
│  - Calls Gemini for reasoning                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI AI Engine (Port 8000)                 │
│         (Python + XGBoost + DistilBERT + PyTorch)           │
│  - XGBoost: Tabular feature scoring                         │
│  - DistilBERT: Text bio analysis                            │
│  - Combined score calculation                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Requirements

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: ~2GB free (for ML models)

### Software Requirements
- **Python**: 3.9 or higher
- **Node.js**: 20.0.0 or higher
- **npm**: 10.0.0 or higher
- **Git**: Latest version

### API Keys
- **Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 💾 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/SekingSenpai/Hybrid-Fake-Profile-Detector.git
cd Hybrid-Fake-Profile-Detector
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-3.5-flash-lite
```

**Get your API key from:** https://aistudio.google.com/app/apikey

### Step 3: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.\.venv\Scripts\Activate.ps1

# Activate it (macOS/Linux)
source .venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
cd ai_engine
pip install -r requirements.txt
cd ..
```

### Step 5: Install Node Dependencies

```bash
# Server dependencies
cd server
npm install
cd ..

# Client dependencies
cd client
npm install
cd ..
```

---

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model to use | `gemini-3.5-flash-lite` |

### AI Engine Configuration

Edit `ai_engine/main.py` to adjust:
- `XGBOOST_WEIGHT`: Weight for XGBoost model (default: 0.6)
- `DISTILBERT_WEIGHT`: Weight for DistilBERT model (default: 0.4)
- `CONFLICT_THRESHOLD`: Threshold for conflict detection (default: 0.5)

---

## 🚀 Running the Project

### Quick Start (3 Terminals)

**Terminal 1 - AI Engine (FastAPI)**
```bash
cd ai_engine
python main.py
```
✅ Runs on: http://localhost:8000

**Terminal 2 - Server (Express Gateway)**
```bash
cd server
npm start
```
✅ Runs on: http://localhost:3000

**Terminal 3 - Client (React)**
```bash
cd client
npm run dev
```
✅ Runs on: http://localhost:5173

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

---

## 📁 Project Structure

```
Hybrid-Fake-Profile-Detector/
├── ai_engine/                 # Python FastAPI ML service
│   ├── main.py               # FastAPI app with /predict endpoint
│   ├── requirements.txt       # Python dependencies
│   ├── models/               # Trained ML models
│   ├── train.py              # Model training script
│   └── Dockerfile            # Docker configuration
│
├── server/                    # Node.js Express gateway
│   ├── index.js              # Main Express app
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Docker configuration
│
├── client/                    # React Vite frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api/              # API client
│   │   └── App.jsx           # Main app component
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   └── index.html            # HTML entry point
│
├── .env                       # Environment variables (create this)
├── .env.example              # Environment template
├── .gitignore                # Git ignore file
├── docker-compose.yml        # Docker Compose configuration
├── QUICKSTART.txt            # Quick start guide
└── README.md                 # This file
```

---

## 🔌 API Endpoints

### AI Engine (FastAPI)

#### GET `/health`
Health check endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy"
}
```

#### POST `/predict`
Predict fake profile probability

Request:
```json
{
  "features": [1.0, 0.5, 1000, 500, 365, 50, 10, 0.3],
  "bio_text": "I love travel and photography"
}
```

Response:
```json
{
  "combined_probability": 0.350000,
  "xgboost_score": 0.400000,
  "distilbert_score": 0.200000,
  "conflict_flag": false
}
```

### Express Gateway

#### GET `/health`
Health check endpoint

#### POST `/analyze`
Analyze a profile and generate reasoning report

Request:
```json
{
  "features": [1.0, 0.5, 1000, 500],
  "bio_text": "I love travel and photography",
  "avg_likes_per_post": 50,
  "avg_comments_per_post": 10,
  "url_ratio": 0.3,
  "username": "john_doe",
  "followers": 1000
}
```

Response:
```json
{
  "scores": {
    "combined_probability": 0.350000,
    "xgboost_score": 0.400000,
    "distilbert_score": 0.200000,
    "conflict_flag": false
  },
  "reasoning_report": "Detailed Gemini-generated reasoning report..."
}
```

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY is not set"
**Solution:**
- Verify `.env` file exists in the root directory
- Check that `GEMINI_API_KEY` is not empty
- Restart the server after updating `.env`

### "Cannot connect to AI Engine"
**Solution:**
- Ensure Terminal 1 (AI Engine) is running
- Check for "All models loaded – AI Engine ready." message
- Verify http://localhost:8000/health is accessible
- Check firewall settings

### "Port already in use"
**Solution:**
```bash
# For Client (change port)
npm run dev -- --port 5174

# For Server (change .env or kill process)
# Change PORT in server or kill the process using port 3000

# For AI Engine (kill the process using port 8000)
```

### "ModuleNotFoundError" in Python
**Solution:**
```bash
# Activate venv and reinstall
.\.venv\Scripts\Activate.ps1
cd ai_engine
pip install -r requirements.txt
```

### "npm ERR! code ENOENT"
**Solution:**
```bash
# Reinstall node_modules
rm -r node_modules package-lock.json
npm install
```

### "DistilBERT download timeout"
**Solution:**
- The first run downloads ~500MB model (can take 2-5 minutes)
- Be patient, don't restart the service
- Subsequent runs use the cached model

### Application appears frozen
**Solution:**
- Check all 3 terminals are running without errors
- Look at terminal logs for specific error messages
- Restart all services in order: AI Engine → Server → Client

---

## 🛠️ Development

### Running in Development Mode

**Server with auto-reload:**
```bash
cd server
npm run dev
```

**Client with Vite dev server:**
```bash
cd client
npm run dev
```

### Building for Production

**Client:**
```bash
cd client
npm run build
```

Output in `client/dist/`

### Linting

**Client:**
```bash
cd client
npm run lint
```

---

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
docker-compose up
```

This starts:
- AI Engine on port 8000
- Server on port 3000
- All services with proper networking

### Stopping Services

```bash
docker-compose down
```

---

## 📊 Model Details

### XGBoost Model (8 Features)
1. **profile_pic** - Has profile picture (0/1)
2. **nums_in_username** - Ratio of digits in username
3. **followers** - Follower count
4. **following** - Following count
5. **account_age** - Days since account creation
6. **avg_likes_per_post** - Mean likes per post
7. **avg_comments_per_post** - Mean comments per post
8. **url_ratio** - Fraction of posts with URLs

### DistilBERT Model
- Pre-trained: `distilbert-base-uncased-finetuned-sst-2-english`
- Input: Profile bio text
- Output: Authenticity probability (0-1)

### Combined Score Calculation
```
Combined = 0.6 × XGBoost_Score + 0.4 × DistilBERT_Score
Conflict = |XGBoost_Score - DistilBERT_Score| > 0.5
```

---

## 🔒 Security Notes

- Never commit `.env` file (it's in `.gitignore`)
- Keep your Gemini API key private
- Don't share your API key in public repositories
- Use environment variables for all sensitive data
- Validate all user inputs on the server

---

## 📝 License

This project is part of a Final Year Project for B.Tech in CSE (AIML).

---

## 👨‍💻 Author

**Arghadip Sarkar**
- GitHub: [@SekingSenpai](https://github.com/SekingSenpai)
- Location: West Bengal, India
- Education: B.Tech CSE (AIML)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📞 Support

If you encounter any issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the terminal logs for error messages
3. Ensure all prerequisites are installed
4. Try restarting all services

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express.js Documentation](https://expressjs.com/)
- [React Documentation](https://react.dev/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Google Generative AI SDK](https://ai.google.dev/docs)

---

**Last Updated:** September 24, 2026
