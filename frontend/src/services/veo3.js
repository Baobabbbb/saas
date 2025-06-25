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

  // Configuration des styles compatibles Stable Diffusion/Runway
  getAvailableStyles() {
    return {
      cartoon: {
        name: 'Cartoon',
        description: 'Style cartoon coloré et amusant',
        prompt: 'vibrant cartoon animation style, colorful and playful, Disney-Pixar inspired',
        icon: '🎨',
        color: '#FF6B6B'
      },
      anime: {
        name: 'Anime',
        description: 'Style anime avec personnages expressifs',
        prompt: 'anime animation style, expressive characters, Japanese animation inspired',
        icon: '🎭',
        color: '#4ECDC4'
      },
      realistic: {
        name: 'Réaliste',
        description: 'Style semi-réaliste adapté aux enfants',
        prompt: 'semi-realistic animation style, detailed but child-friendly',
        icon: '🎪',
        color: '#45B7D1'
      },
      watercolor: {
        name: 'Aquarelle',
        description: 'Style aquarelle artistique',
        prompt: 'watercolor animation style, soft painted textures, artistic brush strokes',
        icon: '🎨',
        color: '#96CEB4'
      },
      pixel_art: {
        name: 'Pixel Art',
        description: 'Style rétro en pixel art',
        prompt: 'pixel art animation style, retro gaming aesthetic, colorful pixels',
        icon: '🕹️',
        color: '#FFEAA7'
      },
      claymation: {
        name: 'Pâte à modeler',
        description: 'Style clay animation en 3D',
        prompt: 'claymation stop-motion animation style, 3D clay characters, textured surfaces',
        icon: '🏺',
        color: '#DDA0DD'
      }
    };
  }

  // Thèmes/environnements compatibles
  getAvailableThemes() {
    return {
      adventure: {
        name: 'Aventure',
        description: 'Scènes d\'exploration et découverte',
        prompt: 'exciting adventure scene with exploration and discovery',
        icon: '🗺️',
        color: '#FF6B6B'
      },
      magic: {
        name: 'Magie',
        description: 'Monde magique avec effets étincelants',
        prompt: 'magical scene with sparkles, spell effects, and wonder',
        icon: '✨',
        color: '#A29BFE'
      },
      animals: {
        name: 'Animaux',
        description: 'Animaux mignons dans leur habitat',
        prompt: 'cute animals in their natural habitat, friendly and endearing',
        icon: '🐾',
        color: '#00B894'
      },
      space: {
        name: 'Espace',
        description: 'Aventure spatiale avec étoiles et planètes',
        prompt: 'space adventure with stars, planets, and cosmic elements',
        icon: '🚀',
        color: '#6C5CE7'
      },
      underwater: {
        name: 'Sous-marin',
        description: 'Monde sous-marin avec vie marine',
        prompt: 'underwater scene with marine life and coral reefs',
        icon: '🌊',
        color: '#00CEC9'
      },
      forest: {
        name: 'Forêt',
        description: 'Forêt enchantée avec créatures magiques',
        prompt: 'enchanted forest with magical creatures and nature',
        icon: '🌲',
        color: '#00B894'
      },
      city: {
        name: 'Ville',
        description: 'Environnement urbain coloré',
        prompt: 'colorful city environment, friendly urban setting',
        icon: '🏙️',
        color: '#0984E3'
      },
      countryside: {
        name: 'Campagne',
        description: 'Paysage rural paisible',
        prompt: 'peaceful countryside landscape, rolling hills, nature',
        icon: '🌾',
        color: '#00B894'
      }
    };
  }

  // Ambiances/moods disponibles
  getAvailableMoods() {
    return {
      joyful: {
        name: 'Joyeux',
        description: 'Ambiance joyeuse et énergique',
        icon: '😊',
        color: '#FDCB6E'
      },
      peaceful: {
        name: 'Paisible',
        description: 'Ambiance calme et sereine',
        icon: '🕊️',
        color: '#74B9FF'
      },
      magical: {
        name: 'Magique',
        description: 'Ambiance mystérieuse et féerique',
        icon: '🔮',
        color: '#A29BFE'
      },
      playful: {
        name: 'Ludique',
        description: 'Ambiance amusante et espiègle',
        icon: '🎈',
        color: '#FF7675'
      },
      adventurous: {
        name: 'Aventureux',
        description: 'Ambiance d\'exploration et découverte',
        icon: '⚡',
        color: '#00B894'
      },
      dreamy: {
        name: 'Rêveur',
        description: 'Ambiance douce et onirique',
        icon: '☁️',
        color: '#DDA0DD'
      },
      exciting: {
        name: 'Excitant',
        description: 'Ambiance dynamique et stimulante',
        icon: '🎆',
        color: '#E17055'
      }
    };
  }

  // Fonction utilitaire pour créer un prompt optimisé
  createOptimizedPrompt(style, theme, customPrompt) {
    const styles = this.getAvailableStyles();
    const themes = this.getAvailableThemes();
    
    let basePrompt = '';

    // Construire le prompt
    basePrompt = `${styles[style]?.prompt || 'cartoon animation style'}, ${themes[theme]?.prompt || 'adventure scene'}`;
    
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

  // Fonction pour valider les paramètres de génération narrative
  validateStoryAnimationData(data) {
    const errors = [];

    if (!data.story || data.story.trim().length < 10) {
      errors.push('L\'histoire doit contenir au moins 10 caractères');
    }

    if (data.story && data.story.length > 1000) {
      errors.push('L\'histoire ne peut pas dépasser 1000 caractères');
    }

    if (!data.style) {
      errors.push('Le style visuel est requis');
    }

    if (!data.theme) {
      errors.push('Le thème/environnement est requis');
    }

    const availableStyles = Object.keys(this.getAvailableStyles());
    if (data.style && !availableStyles.includes(data.style)) {
      errors.push('Style non supporté');
    }

    const availableThemes = Object.keys(this.getAvailableThemes());
    if (data.theme && !availableThemes.includes(data.theme)) {
      errors.push('Thème non supporté');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Fonction pour valider les paramètres avant envoi (animation classique)
  validateAnimationData(data) {
    const errors = [];

    if (!data.style) {
      errors.push('Le style est requis');
    }

    if (!data.theme) {
      errors.push('Le thème est requis');
    }

    if (data.prompt && data.prompt.length > 500) {
      errors.push('La description ne peut pas dépasser 500 caractères');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Nouvelle fonction pour génération d'animation narrative avec CrewAI
  async generateStoryAnimation(storyText, stylePreferences = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations/generate-story`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: storyText,
          style_preferences: {
            style: stylePreferences.style || 'cartoon coloré',
            mood: stylePreferences.mood || 'joyeux',
            target_age: stylePreferences.target_age || '3-8 ans',
            ...stylePreferences
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la génération narrative');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans generateStoryAnimation:', error);
      throw error;
    }
  }

  // Test du pipeline CrewAI
  async testCrewAI(testStory = null) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations/test-crewai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: testStory || "Un petit lapin découvre un jardin magique plein de couleurs."
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur test CrewAI');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans testCrewAI:', error);
      throw error;
    }
  }

  // Nouvelle méthode pour générer des animations narratives
  async generateNarrativeAnimation(storyData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/animations/generate-narrative`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: storyData.story,
          style: storyData.style,
          theme: storyData.theme,
          orientation: storyData.orientation || 'landscape'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Erreur lors de la génération narrative');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur dans generateNarrativeAnimation:', error);
      throw error;
    }
  }

  // Méthode pour générer des animations cohérentes avec CrewAI
  async generateCohesiveAnimation(storyData) {
    try {
      console.log('🎬 Génération animation cohérente CrewAI:', storyData);
      
      const response = await fetch(`${this.baseUrl}/api/animations/generate-cohesive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: storyData.story,
          style: storyData.style || 'cartoon',
          theme: storyData.theme || 'adventure',
          orientation: storyData.orientation || 'landscape',
          duration: storyData.duration || 60, // 60 secondes par défaut
          quality: storyData.quality || 'medium', // fast, medium, high
          title: storyData.title || 'Animation CrewAI'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || errorData.error || 'Erreur lors de la génération cohérente');
      }

      const result = await response.json();
      
      console.log('✅ Animation cohérente générée:', {
        id: result.id,
        duration: result.total_duration,
        scenes: result.total_scenes,
        consistency_score: result.visual_consistency_score,
        agents_used: result.agents_used
      });

      return result;
    } catch (error) {
      console.error('❌ Erreur dans generateCohesiveAnimation:', error);
      throw error;
    }
  }
}

export default new RunwayAnimationService();
