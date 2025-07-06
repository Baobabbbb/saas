// Configuration de l'API
export const API_BASE_URL = 'http://localhost:8007';

// Endpoints de l'API
export const API_ENDPOINTS = {
  generateRhyme: `${API_BASE_URL}/generate_rhyme/`,
  generateAudioStory: `${API_BASE_URL}/generate_audio_story/`,
  generateColoring: `${API_BASE_URL}/generate_coloring/`,
  generateComic: `${API_BASE_URL}/generate_comic/`, // Restauré
  generateAnimation: `${API_BASE_URL}/generate_animation/`,
  checkTaskStatus: (taskId) => `${API_BASE_URL}/check_task_status/${taskId}`,
  downloadAudio: (fileName, url) => `${API_BASE_URL}/download_audio/${fileName}.mp3?url=${encodeURIComponent(url)}`
};

export default {
  API_BASE_URL,
  API_ENDPOINTS
};
