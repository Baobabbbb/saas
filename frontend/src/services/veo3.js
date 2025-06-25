// Service pour l'intégration avec l'API Runway Gen-4 Turbo
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

class RunwayAnimationService {
  constructor() {
    this.baseUrl = BACKEND_URL;
  }

  async generateAnimation(animationData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          style: animationData.style,
          theme: animationData.theme,
          orientation: animationData.orientation,
          prompt: animationData.prompt,
          title: animationData.title || 'Mon Dessin Animé',
          description: animationData.description || 'Dessin animé créé avec Veo3'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Erreur lors de la génération');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans generateAnimation:', error);
      throw error;
    }
  }

  async getAnimationStatus(animationId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations/${animationId}/status`);
      
      if (!response.ok) {
        throw new Error('Erreur lors de la vérification du statut');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans getAnimationStatus:', error);
      throw error;
    }
  }

  async getUserAnimations(page = 1, limit = 10) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations?page=${page}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des animations');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans getUserAnimations:', error);
      throw error;
    }
  }
  // Fonction utilitaire pour créer un prompt optimisé pour Runway Gen-4 Turbo
  createOptimizedPrompt(style, theme, customPrompt) {
    let basePrompt = '';

    // Style mappings pour Runway Gen-4 Turbo
    const stylePrompts = {
      cartoon: 'vibrant cartoon animation style, colorful and playful, Disney-Pixar inspired',
      fairy_tale: 'magical fairy tale animation, enchanted atmosphere with sparkles and soft lighting',
      anime: 'anime animation style, expressive characters, Japanese animation inspired',
      realistic: 'semi-realistic animation style, detailed but child-friendly',
      paper_craft: 'paper craft stop-motion animation style, layered paper cutout effect',
      watercolor: 'watercolor animation style, soft painted textures, artistic brush strokes'
    };

    // Theme mappings
    const themePrompts = {
      adventure: 'exciting adventure scene with exploration and discovery',
      magic: 'magical scene with sparkles, spell effects, and wonder',
      animals: 'cute animals in their natural habitat, friendly and endearing',
      friendship: 'heartwarming scene showing friendship and companionship',
      space: 'space adventure with stars, planets, and cosmic elements',
      underwater: 'underwater scene with marine life and coral reefs',
      forest: 'enchanted forest with magical creatures and nature',
      superhero: 'child-friendly superhero adventure with positive themes'
    };

    // Construire le prompt
    basePrompt = `${stylePrompts[style] || 'cartoon animation style'}, ${themePrompts[theme] || 'adventure scene'}`;
    
    if (customPrompt && customPrompt.trim()) {
      basePrompt += `, ${customPrompt.trim()}`;
    }

    // Ajouter des directives pour optimiser pour les enfants et Runway
    basePrompt += ', suitable for children, bright colors, positive atmosphere, high quality animation, smooth motion';

    return basePrompt;
  }

  // Fonction pour estimer le temps de génération
  estimateGenerationTime(duration) {
    // Estimation basée sur la durée (temps en minutes)
    const baseTime = 2; // 2 minutes de base
    const durationMultiplier = duration / 5; // facteur basé sur la durée
    return Math.ceil(baseTime + (durationMultiplier * 1.5));
  }

  // Fonction pour valider les paramètres avant envoi
  validateAnimationData(data) {
    const errors = [];

    if (!data.style) {
      errors.push('Le style est requis');
    }

    if (!data.theme) {
      errors.push('Le thème est requis');
    }    // Runway Gen-4 Turbo génère des vidéos de 10 secondes
    // Pas besoin de valider la durée côté frontend

    if (data.prompt && data.prompt.length > 500) {
      errors.push('La description ne peut pas dépasser 500 caractères');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

export default new RunwayAnimationService();
