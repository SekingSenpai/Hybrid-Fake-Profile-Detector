/**
 * Hybrid Fake Profile Detector — Express Gateway
 * ================================================
 * 1. Receives profile data on POST /analyze.
 * 2. Forwards the payload to the Python AI Engine (/predict).
 * 3. Sends the combined score + metadata to Gemini 3.1 Flash-Lite
 *    for a structured forensic "Reasoning Report".
 * 4. Returns the full report to the client.
 */

import "dotenv/config";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import express from "express";
import cors from "cors";
import axios from "axios";
import { GoogleGenerativeAI } from "@google/generative-ai";

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "../.env");

// Load .env from parent directory
import dotenv from "dotenv";
dotenv.config({ path: envPath });

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const PORT = process.env.PORT || 3000;
const AI_ENGINE_URL = process.env.AI_ENGINE_URL || "http://ai_engine:8000";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-2.0-flash-lite";

if (!GEMINI_API_KEY) {
  console.warn(
    "⚠️  GEMINI_API_KEY is not set. Gemini calls will fail at runtime."
  );
}

// ---------------------------------------------------------------------------
// Gemini client (lazy — only instantiated when key exists)
// ---------------------------------------------------------------------------
const genAI = GEMINI_API_KEY ? new GoogleGenerativeAI(GEMINI_API_KEY) : null;

// ---------------------------------------------------------------------------
// Prompt template
// ---------------------------------------------------------------------------
/**
 * Build a forensic-analyst prompt that Gemini will use to produce a
 * structured reasoning report.
 */
function buildPrompt(profileData, aiScores) {
  return `Act as a forensic analyst specialising in social-media fraud detection.

You have been given a user profile along with probability scores produced by a hybrid ML pipeline (XGBoost on 8 tabular + behavioral features, and DistilBERT on bio text).

---
### Profile Metadata
${JSON.stringify(profileData, null, 2)}

### ML Pipeline Scores
- **XGBoost score (tabular + behavioral)**: ${aiScores.xgboost_score}
- **DistilBERT score (text)**: ${aiScores.distilbert_score}
- **Combined probability** (0.6·XGB + 0.4·BERT): ${aiScores.combined_probability}
- **Conflict flag** (scores differ > 0.5): ${aiScores.conflict_flag}
---

Note: The XGBoost model was trained on 8 features:
1. profile_pic (has profile picture)
2. nums_in_username (ratio of digits in username)
3. followers (follower count)
4. following (following count)
5. account_age (days since account creation)
6. avg_likes_per_post (mean likes per post — behavioral)
7. avg_comments_per_post (mean comments per post — behavioral)
8. url_ratio (fraction of posts containing external URLs — behavioral)

Review these scores and metadata to provide a **structured reasoning report** for the end-user. The report MUST contain the following sections:

1. **Verdict** — FAKE, SUSPICIOUS, or GENUINE (with confidence percentage).
2. **Key Indicators** — bullet-point list of the strongest signals from the profile data and scores.
3. **Behavioral Analysis** — analyze the behavioral features (avg likes, avg comments, url ratio) and explain what they reveal about the account's authenticity.
4. **Model Agreement Analysis** — explain whether the XGBoost and DistilBERT models agree or disagree and what that implies.
5. **Risk Factors** — any red flags that warrant further investigation.
6. **Recommendation** — actionable next steps for a platform moderator.

Be precise, objective, and cite the data provided. Do not hallucinate information that was not supplied.`;
}

// ---------------------------------------------------------------------------
// Express app
// ---------------------------------------------------------------------------
const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Health probe
app.get("/health", (_req, res) => {
  res.json({ status: "healthy", service: "express-gateway" });
});

/**
 * POST /analyze
 * Body: {
 *   features: number[5],     // 5 static profile features
 *   bio_text: string,
 *   avg_likes_per_post: number,
 *   avg_comments_per_post: number,
 *   url_ratio: number,
 *   ...metadata
 * }
 */
app.post("/analyze", async (req, res) => {
  const {
    features,
    bio_text,
    avg_likes_per_post = 0,
    avg_comments_per_post = 0,
    url_ratio = 0,
    ...metadata
  } = req.body;

  // ---- input validation ----
  if (!features || !Array.isArray(features) || features.length < 5) {
    return res
      .status(400)
      .json({ error: "'features' must be an array of at least 5 numbers." });
  }
  if (!bio_text || typeof bio_text !== "string") {
    return res
      .status(400)
      .json({ error: "'bio_text' must be a non-empty string." });
  }

  // Build the full 8-feature vector for the AI Engine
  const fullFeatures = [
    ...features.slice(0, 5),
    Number(avg_likes_per_post),
    Number(avg_comments_per_post),
    Number(url_ratio),
  ];

  try {
    // ---- Step 1: call AI Engine ----
    const aiResponse = await axios.post(`${AI_ENGINE_URL}/predict`, {
      features: fullFeatures,
      bio_text,
    });
    const aiScores = aiResponse.data;

    // ---- Step 2: call Gemini for Reasoning Report ----
    let reasoningReport = null;

    if (genAI) {
      const model = genAI.getGenerativeModel({ model: GEMINI_MODEL });
      const prompt = buildPrompt(
        { bio_text, avg_likes_per_post, avg_comments_per_post, url_ratio, ...metadata },
        aiScores
      );
      const result = await model.generateContent(prompt);
      reasoningReport = result.response.text();
    } else {
      reasoningReport =
        "Gemini API key not configured — skipping reasoning report generation.";
    }

    // ---- Step 3: respond ----
    return res.json({
      scores: aiScores,
      reasoning_report: reasoningReport,
    });
  } catch (err) {
    console.error("❌ /analyze failed:", err.message);

    // Forward upstream HTTP errors when possible
    if (err.response) {
      return res.status(err.response.status).json({
        error: "Upstream service error",
        detail: err.response.data,
      });
    }

    return res.status(500).json({ error: "Internal server error" });
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`🚀 Express gateway listening on port ${PORT}`);
  console.log(`   AI Engine URL : ${AI_ENGINE_URL}`);
  console.log(`   Gemini model  : ${GEMINI_MODEL}`);
});
