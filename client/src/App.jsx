import { useState } from 'react';
import './index.css';
import DetectorForm from './components/DetectorForm';
import ResultsPanel from './components/ResultsPanel';
import { analyzeProfile } from './api/client';

export default function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (payload) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeProfile(payload);
      setResult(data);
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.message ||
        'Something went wrong. Make sure the backend servers are running.';
      setError(String(message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-header__badge">AI-Powered Detection System</div>
        <h1>Fake Profile Detector</h1>
        <p>
          Hybrid AI analysis combining XGBoost behavioral scoring, DistilBERT
          NLP, and Gemini forensic reasoning to detect fraudulent social media
          profiles.
        </p>
      </header>

      {/* Main Grid */}
      <main className="main-grid">
        <DetectorForm onSubmit={handleAnalyze} isLoading={isLoading} />
        <ResultsPanel result={result} error={error} />
      </main>

      {/* Footer */}
      <footer className="app-footer">
        Hybrid Fake Profile Detector &mdash; Final Year Project &copy;{' '}
        {new Date().getFullYear()}
      </footer>
    </div>
  );
}
