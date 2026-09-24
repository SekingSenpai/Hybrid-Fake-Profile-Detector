import axios from 'axios';

const API_BASE = 'http://localhost:3000';

/**
 * Analyze a social media profile for authenticity.
 * @param {object} data
 * @param {number[]} data.features - 5 static profile features
 * @param {string} data.bio_text - Profile bio / description
 * @param {number} data.avg_likes_per_post - Behavioral: avg likes
 * @param {number} data.avg_comments_per_post - Behavioral: avg comments
 * @param {number} data.url_ratio - Behavioral: fraction of posts with URLs
 * @param {string} data.username - Username for metadata
 * @returns {Promise<{scores: object, reasoning_report: string}>}
 */
export async function analyzeProfile(data) {
  const response = await axios.post(`${API_BASE}/analyze`, data, {
    timeout: 30000,
  });
  return response.data;
}
