import { useState } from 'react';

const INITIAL_STATE = {
  // Static profile features
  profilePic: '1',
  numsInUsername: '0.1',
  followers: '100',
  following: '200',
  accountAge: '365',
  // Behavioral features
  avgLikes: '25',
  avgComments: '5',
  urlRatio: '0.1',
  // Text
  bioText: '',
  username: '',
};

export default function DetectorForm({ onSubmit, isLoading }) {
  const [form, setForm] = useState(INITIAL_STATE);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const payload = {
      features: [
        parseFloat(form.profilePic) || 0,
        parseFloat(form.numsInUsername) || 0,
        parseFloat(form.followers) || 0,
        parseFloat(form.following) || 0,
        parseFloat(form.accountAge) || 0,
      ],
      bio_text: form.bioText || 'No bio provided.',
      avg_likes_per_post: parseFloat(form.avgLikes) || 0,
      avg_comments_per_post: parseFloat(form.avgComments) || 0,
      url_ratio: parseFloat(form.urlRatio) || 0,
      username: form.username || 'unknown_user',
    };

    onSubmit(payload);
  };

  return (
    <div className="glass-card">
      <h2 className="glass-card__title">
        <span
          className="glass-card__title-icon"
          style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}
        >
          🔍
        </span>
        Profile Scanner
      </h2>
      <form onSubmit={handleSubmit} className="form-section">
        {/* Username & Bio */}
        <div className="form-group">
          <label className="form-group__label" htmlFor="username">
            Username
          </label>
          <input
            id="username"
            name="username"
            type="text"
            className="form-group__input"
            placeholder="e.g. crypto_bot_9999"
            value={form.username}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-group__label" htmlFor="bioText">
            Bio / Description
          </label>
          <textarea
            id="bioText"
            name="bioText"
            className="form-group__input"
            placeholder="Paste the profile's biography text here..."
            value={form.bioText}
            onChange={handleChange}
            rows={3}
          />
        </div>

        {/* Divider: Static Features */}
        <div className="form-divider">
          <span className="form-divider__line" />
          <span className="form-divider__text">Profile Features</span>
          <span className="form-divider__line" />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-group__label" htmlFor="profilePic">
              Has Profile Pic (0 / 1)
            </label>
            <input
              id="profilePic"
              name="profilePic"
              type="number"
              step="1"
              min="0"
              max="1"
              className="form-group__input"
              value={form.profilePic}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label className="form-group__label" htmlFor="numsInUsername">
              Digit Ratio in Username
            </label>
            <input
              id="numsInUsername"
              name="numsInUsername"
              type="number"
              step="0.01"
              min="0"
              max="1"
              className="form-group__input"
              value={form.numsInUsername}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-group__label" htmlFor="followers">
              Followers
            </label>
            <input
              id="followers"
              name="followers"
              type="number"
              min="0"
              className="form-group__input"
              value={form.followers}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label className="form-group__label" htmlFor="following">
              Following
            </label>
            <input
              id="following"
              name="following"
              type="number"
              min="0"
              className="form-group__input"
              value={form.following}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-group__label" htmlFor="accountAge">
            Account Age (days)
          </label>
          <input
            id="accountAge"
            name="accountAge"
            type="number"
            min="0"
            className="form-group__input"
            value={form.accountAge}
            onChange={handleChange}
          />
        </div>

        {/* Divider: Behavioral Features */}
        <div className="form-divider">
          <span className="form-divider__line" />
          <span className="form-divider__text">Behavioral Tracking</span>
          <span className="form-divider__line" />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-group__label" htmlFor="avgLikes">
              Avg Likes / Post
            </label>
            <input
              id="avgLikes"
              name="avgLikes"
              type="number"
              step="0.1"
              min="0"
              className="form-group__input"
              value={form.avgLikes}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label className="form-group__label" htmlFor="avgComments">
              Avg Comments / Post
            </label>
            <input
              id="avgComments"
              name="avgComments"
              type="number"
              step="0.1"
              min="0"
              className="form-group__input"
              value={form.avgComments}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-group__label" htmlFor="urlRatio">
            URL Ratio (0.0 - 1.0)
          </label>
          <input
            id="urlRatio"
            name="urlRatio"
            type="number"
            step="0.01"
            min="0"
            max="1"
            className="form-group__input"
            placeholder="Fraction of posts containing links"
            value={form.urlRatio}
            onChange={handleChange}
          />
        </div>

        {/* Submit */}
        <button type="submit" className="btn-analyze" disabled={isLoading}>
          {isLoading ? (
            <>
              <span className="spinner" />
              Analyzing Profile...
            </>
          ) : (
            'Analyze Profile'
          )}
        </button>
      </form>
    </div>
  );
}
