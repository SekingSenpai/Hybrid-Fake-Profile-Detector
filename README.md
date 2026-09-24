# 🎯 Hybrid Fake Profile Detector

A sophisticated ML-powered system for detecting fake social media profiles using a hybrid approach combining XGBoost, DistilBERT, and Gemini AI. Built with FastAPI, Express.js, and React.

## 📋 Quick Navigation

- **[Quick Start](#-quick-start)** - Get running in 5 minutes
- **[Full Documentation](README_FULL.md)** - Complete setup guide
- **[Quick Start Text](QUICKSTART.txt)** - Plain text guide

## ✨ Features

- ✅ Hybrid ML pipeline (XGBoost + DistilBERT)
- ✅ Real-time profile analysis
- ✅ Gemini AI-powered reasoning reports
- ✅ Conflict detection when models disagree
- ✅ REST API for easy integration
- ✅ Modern React frontend
- ✅ Docker support
- ✅ Comprehensive logging

## 🏗️ Architecture

```
React Client (Port 5173)
        ↓
Express Gateway (Port 3000)
        ↓
FastAPI AI Engine (Port 8000)
    (XGBoost + DistilBERT + Gemini)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 20.0+
- Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

### 1️⃣ Clone & Setup

```bash
git clone https://github.com/SekingSenpai/Hybrid-Fake-Profile-Detector.git
cd Hybrid-Fake-Profile-Detector
```

### 2️⃣ Environment Setup

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3️⃣ Install Dependencies

```bash
# Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux
cd ai_engine && pip install -r requirements.txt && cd ..

# Node (Server)
cd server && npm install && cd ..

# Node (Client)
cd client && npm install && cd ..
```

### 4️⃣ Run (3 Terminals)

**Terminal 1 - AI Engine:**
```bash
cd ai_engine
python main.py
```

**Terminal 2 - Server:**
```bash
cd server
npm start
```

**Terminal 3 - Client:**
```bash
cd client
npm run dev
```

### 5️⃣ Open in Browser
```
http://localhost:5173
```

---

## 📖 Detailed Documentation

For complete setup instructions, API details, and troubleshooting, see:
- **[Full README](README_FULL.md)** - Comprehensive guide
- **[QUICKSTART.txt](QUICKSTART.txt)** - Quick reference (plain text)

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend ML** | FastAPI, XGBoost, PyTorch, DistilBERT |
| **API Gateway** | Node.js, Express.js, Axios |
| **Frontend** | React, Vite, Axios |
| **AI Reasoning** | Google Gemini API |
| **Deployment** | Docker, Docker Compose |

## 📁 Project Structure

```
├── ai_engine/          # FastAPI ML service
├── server/             # Express.js gateway
├── client/             # React frontend
├── README_FULL.md      # Full documentation
├── QUICKSTART.txt      # Quick start guide
└── docker-compose.yml  # Docker configuration
```

## 🔌 API Example

**POST** `/analyze` (Express Gateway)
```json
{
  "features": [1.0, 0.5, 1000, 500],
  "bio_text": "I love travel and photography",
  "avg_likes_per_post": 50,
  "avg_comments_per_post": 10,
  "url_ratio": 0.3
}
```

Response:
```json
{
  "scores": {
    "combined_probability": 0.35,
    "xgboost_score": 0.40,
    "distilbert_score": 0.20,
    "conflict_flag": false
  },
  "reasoning_report": "Detailed AI-generated analysis..."
}
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "GEMINI_API_KEY not set" | Check `.env` file in root directory |
| "Cannot connect to AI Engine" | Ensure Terminal 1 is running |
| "Port already in use" | Change port or kill existing process |
| "DistilBERT timeout" | First run downloads model (~500MB), be patient |

**More troubleshooting:** See [README_FULL.md](README_FULL.md#-troubleshooting)

## 🐳 Docker Deployment

```bash
docker-compose up
```

Services run on:
- AI Engine: http://localhost:8000
- Server: http://localhost:3000
- Client: http://localhost:5173

## 📊 Model Information

**XGBoost** (8 features):
- Profile picture, username digits, followers, following
- Account age, likes/post, comments/post, URL ratio

**DistilBERT**:
- Analyzes profile bio text
- Fine-tuned for sentiment analysis

**Scoring**:
```
Combined = 0.6 × XGBoost + 0.4 × DistilBERT
Conflict = |XGBoost - DistilBERT| > 0.5
```

## 👨‍💻 Author

**Arghadip Sarkar**  
B.Tech CSE (AIML) | West Bengal, India  
GitHub: [@SekingSenpai](https://github.com/SekingSenpai)

## 📝 License

This is a Final Year Project for B.Tech in CSE (AIML).

---

**Need help?** Check [README_FULL.md](README_FULL.md) for detailed documentation.
