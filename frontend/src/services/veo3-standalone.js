// Version standalone du service d'animation (sans modules ES6)
class StandaloneRunwayAnimationService {
  constructor() {
    this.baseUrl = "http://127.0.0.1:8000";
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
        color: '#FF7675'
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
        color: '#6C5CE7'
      },
      space: {
        name: 'Espace',
        description: 'Aventure spatiale avec étoiles et planètes',
        prompt: 'space adventure with stars, planets, and cosmic elements',
        icon: '🚀',
        color: '#74B9FF'
      },
      underwater: {
        name: 'Sous-marin',
        description: 'Monde sous-marin avec vie marine',
        prompt: 'underwater scene with marine life and coral reefs',
        icon: '🌊',
        color: '#00B894'
      },
      forest: {
        name: 'Forêt',
        description: 'Forêt enchantée avec créatures magiques',
        prompt: 'enchanted forest with magical creatures and nature',
        icon: '🌲',
        color: '#00CEC9'
      },
      city: {
        name: 'Ville',
        description: 'Environnement urbain coloré',
        prompt: 'colorful city environment, friendly urban setting',
        icon: '🏙️',
        color: '#FDCB6E'
      },
      countryside: {
        name: 'Campagne',
        description: 'Paysage rural paisible',
        prompt: 'peaceful countryside landscape, rolling hills, nature',
        icon: '🌾',
        color: '#E17055'
      },
      fantasy: {
        name: 'Fantasy',
        description: 'Monde fantastique avec châteaux',
        prompt: 'fantasy world with castles, dragons, medieval settings',
        icon: '🏰',
        color: '#B2BEC3'
      },
      winter: {
        name: 'Hiver',
        description: 'Paysage d\'hiver féerique',
        prompt: 'winter wonderland with snow, ice crystals, cozy atmosphere',
        icon: '❄️',
        color: '#81ECEC'
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

  // Validation des données
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

  // Génération d'animation narrative avec CrewAI
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
            style: stylePreferences.style || 'cartoon',
            theme: stylePreferences.theme || 'adventure',
            mood: stylePreferences.mood || 'joyful',
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
}

// Instance globale
const runwayService = new StandaloneRunwayAnimationService();
