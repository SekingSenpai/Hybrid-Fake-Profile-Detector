import Markdown from 'react-markdown';

function getVerdictClass(combined) {
  if (combined >= 0.7) return 'fake';
  if (combined >= 0.4) return 'suspicious';
  return 'genuine';
}

function getVerdictText(combined) {
  if (combined >= 0.7) return 'FAKE';
  if (combined >= 0.4) return 'SUSPICIOUS';
  return 'GENUINE';
}

function ScoreBar({ label, value, variant }) {
  const percent = Math.min(Math.max(value * 100, 0), 100);
  return (
    <div className="score-bar">
      <div className="score-bar__header">
        <span className="score-bar__name">{label}</span>
        <span className="score-bar__value">{(value * 100).toFixed(1)}%</span>
      </div>
      <div className="score-bar__track">
        <div
          className={`score-bar__fill score-bar__fill--${variant}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

export default function ResultsPanel({ result, error }) {
  // Error state
  if (error) {
    return (
      <div className="glass-card results-panel">
        <h2 className="glass-card__title">
          <span
            className="glass-card__title-icon"
            style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}
          >
            ⚠️
          </span>
          Error
        </h2>
        <div className="error-banner">{error}</div>
      </div>
    );
  }

  // Empty state
  if (!result) {
    return (
      <div className="glass-card results-panel">
        <div className="empty-state">
          <div className="empty-state__icon">🛡️</div>
          <div className="empty-state__title">Ready to Scan</div>
          <div className="empty-state__desc">
            Fill in the profile details on the left and hit
            &quot;Analyze Profile&quot; to get your AI-powered forensic report.
          </div>
        </div>
      </div>
    );
  }

  const { scores, reasoning_report } = result;
  const verdictClass = getVerdictClass(scores.combined_probability);
  const verdictText = getVerdictText(scores.combined_probability);

  return (
    <div className="glass-card results-panel">
      <h2 className="glass-card__title">
        <span
          className="glass-card__title-icon"
          style={{
            background: 'rgba(139, 92, 246, 0.15)',
            color: '#8b5cf6',
          }}
        >
          📊
        </span>
        Analysis Results
      </h2>

      {/* Verdict Banner */}
      <div className={`verdict-banner verdict-banner--${verdictClass}`}>
        <div className="verdict-banner__content">
          <div className="verdict-banner__label">Verdict</div>
          <div className="verdict-banner__text">{verdictText}</div>
        </div>
        <div className="verdict-banner__score">
          <div className="verdict-banner__score-value">
            {(scores.combined_probability * 100).toFixed(1)}%
          </div>
          <div className="verdict-banner__score-label">Combined Score</div>
        </div>
      </div>

      {/* Score Bars */}
      <div className="score-bars">
        <ScoreBar
          label="XGBoost (Profile + Behavioral)"
          value={scores.xgboost_score}
          variant="xgb"
        />
        <ScoreBar
          label="DistilBERT (Text Analysis)"
          value={scores.distilbert_score}
          variant="bert"
        />
        <ScoreBar
          label="Combined Probability"
          value={scores.combined_probability}
          variant="combined"
        />
      </div>

      {/* Conflict badge */}
      <div
        className={`conflict-badge ${
          scores.conflict_flag
            ? 'conflict-badge--conflict'
            : 'conflict-badge--agree'
        }`}
      >
        {scores.conflict_flag ? '⚡ Models Disagree' : '✓ Models Agree'}
      </div>

      {/* Reasoning Report */}
      {reasoning_report && (
        <div className="report-section">
          <div className="report-section__title">
            🧠 Gemini Forensic Report
          </div>
          <div className="report-content">
            <Markdown>{reasoning_report}</Markdown>
          </div>
        </div>
      )}
    </div>
  );
}
