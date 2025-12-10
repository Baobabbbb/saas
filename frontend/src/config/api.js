// Configuration de l'API
// Utiliser des URLs relatives par défaut pour le déploiement (même domaine Railway)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Endpoints de l'API
export const API_ENDPOINTS = {
  generateRhyme: `${API_BASE_URL}/generate_rhyme/`,
  generateAudioStory: `${API_BASE_URL}/generate_audio_story/`,
  generateColoring: `${API_BASE_URL}/generate_coloring/`,
  generateComic: `${API_BASE_URL}/generate_comic/`,
  generateAnimation: `${API_BASE_URL}/generate-quick`,
  checkTaskStatus: (taskId) => `${API_BASE_URL}/check_task_status/${taskId}`,
  downloadAudio: (fileName, url) => `${API_BASE_URL}/download_audio/${fileName}.mp3?url=${encodeURIComponent(url)}`
};

export default {
  API_BASE_URL,
  API_ENDPOINTS
};
