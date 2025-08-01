// Configuration de l'API
// Note: HTTP pour le développement, HTTPS pour la production
export const API_BASE_URL = 'http://localhost:8006';
export const ANIMATION_API_BASE_URL = 'http://localhost:8012';

// Endpoints de l'API
export const API_ENDPOINTS = {
  generateRhyme: `${API_BASE_URL}/generate_rhyme/`,
  generateAudioStory: `${API_BASE_URL}/generate_audio_story/`,
  generateColoring: `${API_BASE_URL}/generate_coloring/`,
  generateComic: `${API_BASE_URL}/generate_comic/`,
  // Animation Studio endpoints (port 8007)
  generateAnimation: `${ANIMATION_API_BASE_URL}/generate`,
  animationStatus: (animationId) => `${ANIMATION_API_BASE_URL}/status/${animationId}`,
  animationThemes: `${ANIMATION_API_BASE_URL}/themes`,
  animationDiagnostic: `${ANIMATION_API_BASE_URL}/diagnostic`,
  checkTaskStatus: (taskId) => `${API_BASE_URL}/check_task_status/${taskId}`,
  downloadAudio: (fileName, url) => `${API_BASE_URL}/download_audio/${fileName}.mp3?url=${encodeURIComponent(url)}`
};

export default {
  API_BASE_URL,
  ANIMATION_API_BASE_URL,
  API_ENDPOINTS
};
