// Service d'animation utilisant la nouvelle pipeline complète
const API_BASE_URL = 'http://127.0.0.1:8000';

export const generateCompleteAnimation = async (animationData) => {
  try {
    console.log('🎬 Démarrage génération animation complète:', animationData);
    
    // Calculer les durées
    const totalDuration = animationData.duration_preferences?.total_duration || parseInt(animationData.duration) || 30;
    const sceneDuration = animationData.duration_preferences?.scene_duration || Math.min(5, Math.max(2, totalDuration / 6));
    
    const response = await fetch(`${API_BASE_URL}/api/animations/generate-complete`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        story: animationData.story,
        style_preferences: {
          visual_style: animationData.style_preferences?.visual_style || animationData.style || 'cartoon',
          theme: animationData.style_preferences?.theme || animationData.theme || 'adventure',
          color_palette: animationData.style_preferences?.color_palette || 'vibrant',
          target_audience: animationData.style_preferences?.target_audience || 'children'
        },
        duration_preferences: {
          total_duration: totalDuration,
          scene_duration: sceneDuration,
          total_max_duration: totalDuration
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Erreur HTTP : ${response.status}`);
    }
    
    const result = await response.json();
    console.log('✅ Réponse animation reçue:', result);
    
    return result;
  } catch (error) {
    console.error('❌ Erreur génération animation:', error);
    throw error;
  }
};

export const generateProductionAnimation = async (animationData) => {
  try {
    console.log('🎬 Démarrage génération animation production:', animationData);
    
    // Calculer les durées
    const totalDuration = animationData.duration_preferences?.total_duration || parseInt(animationData.duration) || 30;
    const sceneDuration = animationData.duration_preferences?.scene_duration || Math.min(5, Math.max(2, totalDuration / 6));
    
    const response = await fetch(`${API_BASE_URL}/generate-production`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        story: animationData.story,
        style_preferences: {
          visual_style: animationData.style_preferences?.visual_style || animationData.style || 'cartoon',
          theme: animationData.style_preferences?.theme || animationData.theme || 'adventure',
          color_palette: animationData.style_preferences?.color_palette || 'vibrant',
          target_audience: animationData.style_preferences?.target_audience || 'children'
        },
        duration_preferences: {
          total_duration: totalDuration,
          scene_duration: sceneDuration,
          total_max_duration: totalDuration
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Erreur HTTP : ${response.status}`);
    }
    
    const result = await response.json();
    console.log('✅ Réponse animation production reçue:', result);
    
    return result;
  } catch (error) {
    console.error('❌ Erreur génération animation production:', error);
    throw error;
  }
};