import { API_BASE_URL, ANIMATION_API_BASE_URL } from '../config/api';

/**
 * Service pour la gestion des animations
 * Gère la génération, le suivi du statut et la récupération des résultats
 */

class AnimationService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.animationBaseURL = ANIMATION_API_BASE_URL;
  }

  /**
   * Génère une nouvelle animation
   * @param {Object} params - Paramètres de l'animation
   * @param {string} params.theme - Thème de l'animation
   * @param {number} params.duration - Durée en secondes
   * @param {string} params.style - Style visuel
   * @param {string} params.mode - Mode de génération ('demo', 'sora2', 'production')
   * @param {string} params.custom_prompt - Prompt personnalisé optionnel
   * @returns {Promise<Object>} Résultat de l'initiation de génération
   */
  async generateAnimation({ theme, duration, style, mode, custom_prompt }) {
    try {
      const url = `${this.animationBaseURL}/generate`;

      const params = new URLSearchParams({
        theme: theme || 'space',
        duration: duration || 30,
        style: style || 'cartoon',
        mode: mode || 'demo'
      });

      if (custom_prompt) {
        params.append('custom_prompt', custom_prompt);
      }

      const response = await fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
        throw new Error(errorData.message || `Erreur HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Erreur lors de la génération d\'animation:', error);
      throw error;
    }
  }

  /**
   * Génère une animation via POST (méthode alternative)
   * @param {Object} animationData - Données de l'animation
   * @returns {Promise<Object>} Résultat de l'initiation de génération
   */
  async generateAnimationPost(animationData) {
    try {
      const url = `${this.animationBaseURL}/generate-quick-json`;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(animationData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
        throw new Error(errorData.message || `Erreur HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Erreur lors de la génération d\'animation (POST):', error);
      throw error;
    }
  }

  /**
   * Récupère le statut d'une animation en cours
   * @param {string} taskId - ID de la tâche d'animation
   * @returns {Promise<Object>} Statut de l'animation
   */
  async getAnimationStatus(taskId) {
    try {
      if (!taskId) {
        throw new Error('Task ID requis');
      }

      // Utiliser le serveur saas principal pour vérifier le statut (pas le serveur d'animation)
      const url = `${this.baseURL}/status/${taskId}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
        throw new Error(errorData.message || `Erreur HTTP ${response.status}`);
      }

      const data = await response.json();

      // Normaliser la réponse pour le format attendu par le frontend
      if (data.type === 'result' && data.data) {
        return data.data;
      }

      return data;

    } catch (error) {
      console.error('Erreur lors de la récupération du statut:', error);
      throw error;
    }
  }

  /**
   * Récupère la liste des thèmes disponibles
   * @returns {Promise<Object>} Liste des thèmes
   */
  async getThemes() {
    try {
      const url = `${this.animationBaseURL}/themes`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // Fallback vers des thèmes par défaut si l'API n'est pas disponible
        return {
          themes: {
            space: { name: 'Espace', description: 'Voyages spatiaux', icon: '🚀' },
            ocean: { name: 'Océan', description: 'Aventures sous-marines', icon: '🌊' },
            forest: { name: 'Forêt', description: 'Aventures dans la nature', icon: '🌳' },
            city: { name: 'Ville', description: 'Exploration urbaine', icon: '🏙️' },
            adventure: { name: 'Aventure', description: 'Quêtes héroïques', icon: '🏰' },
            fantasy: { name: 'Fantasy', description: 'Monde magique', icon: '✨' },
            cartoon: { name: 'Cartoon', description: 'Style cartoon classique', icon: '🎨' }
          }
        };
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Erreur lors de la récupération des thèmes:', error);
      // Retourner des thèmes par défaut en cas d'erreur
      return {
        themes: {
          space: { name: 'Espace', description: 'Voyages spatiaux', icon: '🚀' },
          ocean: { name: 'Océan', description: 'Aventures sous-marines', icon: '🌊' },
          forest: { name: 'Forêt', description: 'Aventures dans la nature', icon: '🌳' },
          city: { name: 'Ville', description: 'Exploration urbaine', icon: '🏙️' },
          adventure: { name: 'Aventure', description: 'Quêtes héroïques', icon: '🏰' },
          fantasy: { name: 'Fantasy', description: 'Monde magique', icon: '✨' },
          cartoon: { name: 'Cartoon', description: 'Style cartoon classique', icon: '🎨' }
        }
      };
    }
  }

  /**
   * Vérifie la santé du service d'animation
   * @returns {Promise<Object>} État de santé du service
   */
  async checkHealth() {
    try {
      const url = `${this.animationBaseURL}/diagnostic`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return {
          status: 'error',
          message: `Service indisponible (HTTP ${response.status})`
        };
      }

      const data = await response.json();
      return {
        status: 'healthy',
        ...data
      };

    } catch (error) {
      console.error('Erreur lors de la vérification de santé:', error);
      return {
        status: 'error',
        message: error.message
      };
    }
  }

  /**
   * Polls the animation status until completion
   * @param {string} taskId - Animation task ID
   * @param {Object} options - Polling options
   * @param {number} options.interval - Polling interval in ms (default: 1500)
   * @param {number} options.timeout - Max polling time in ms (default: 600000 = 10min)
   * @param {Function} options.onProgress - Callback for progress updates
   * @returns {Promise<Object>} Final animation result
   */
  async pollAnimationStatus(taskId, options = {}) {
    const {
      interval = 1500,
      timeout = 600000, // 10 minutes
      onProgress
    } = options;

    const startTime = Date.now();

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          // Check timeout
          if (Date.now() - startTime > timeout) {
            reject(new Error('Timeout: Animation generation took too long'));
            return;
          }

          const status = await this.getAnimationStatus(taskId);

          // Call progress callback if provided
          if (onProgress) {
            onProgress(status);
          }

          // Check if completed
          if (status.status === 'completed') {
            resolve(status);
            return;
          }

          // Check if failed
          if (status.status === 'failed') {
            reject(new Error(status.error || 'Animation generation failed'));
            return;
          }

          // Continue polling
          setTimeout(poll, interval);

        } catch (error) {
          reject(error);
        }
      };

      // Start polling
      poll();
    });
  }

  /**
   * Génère une animation avec suivi automatique du progrès
   * @param {Object} params - Paramètres de l'animation
   * @param {Object} options - Options de suivi
   * @returns {Promise<Object>} Résultat final de l'animation
   */
  async generateAnimationWithProgress(params, options = {}) {
    try {
      // Initiate animation generation
      const initResult = await this.generateAnimation(params);

      if (!initResult.task_id) {
        throw new Error('Failed to initiate animation generation');
      }

      // Poll for completion
      const finalResult = await this.pollAnimationStatus(
        initResult.task_id,
        options
      );

      return {
        ...finalResult,
        task_id: initResult.task_id
      };

    } catch (error) {
      console.error('Erreur lors de la génération avec suivi:', error);
      throw error;
    }
  }
}

// Instance singleton
const animationService = new AnimationService();

export default animationService;
