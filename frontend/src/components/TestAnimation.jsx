import React, { useState, useEffect } from 'react';

const TestAnimation = () => {
  const [animationData, setAnimationData] = useState(null);
  const [loading, setLoading] = useState(false);

  const testGeneration = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/generate_animation/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: "Un petit lapin découvre un jardin magique plein de couleurs",
          duration: 30,
          style: "cartoon"
        }),
      });

      const data = await response.json();
      console.log('✅ Animation générée:', data);
      setAnimationData(data);
    } catch (error) {
      console.error('❌ Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>🧪 Test Animation Pipeline</h2>
      
      <button 
        onClick={testGeneration} 
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px', 
          backgroundColor: '#4CAF50', 
          color: 'white', 
          border: 'none', 
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? '🔄 Génération en cours...' : '🎬 Générer Animation Test'}
      </button>

      {animationData && (
        <div style={{ marginTop: '20px', border: '1px solid #ddd', padding: '20px', borderRadius: '10px' }}>
          <h3>🎉 Animation Générée ! ({animationData.generation_time?.toFixed(1)}s)</h3>
          <p><strong>Scènes:</strong> {animationData.clips?.length || 0}</p>
          <p><strong>Durée:</strong> {animationData.actual_duration || 0}s</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px', marginTop: '20px' }}>
            {animationData.clips?.map((clip, index) => {
              const imageUrl = `http://localhost:8000${clip.image_url || clip.video_url}`;
              return (
                <div key={index} style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                  <img 
                    src={imageUrl}
                    alt={`Scène ${clip.scene_number}`}
                    style={{ width: '100%', height: '150px', objectFit: 'contain', backgroundColor: '#f5f5f5' }}
                    onLoad={() => console.log(`✅ Image ${index + 1} chargée`)}
                    onError={(e) => {
                      console.log(`❌ Erreur image ${index + 1}:`, imageUrl);
                      e.target.style.backgroundColor = '#ffebee';
                      e.target.alt = `❌ Erreur scène ${clip.scene_number}`;
                    }}
                  />
                  <p><strong>Scène {clip.scene_number}</strong></p>
                  <p>Durée: {clip.duration}s</p>
                  <p>Status: {clip.status} {clip.status === 'success' ? '✅' : '⚠️'}</p>
                  <small style={{ color: '#666' }}>{clip.type}</small>
                </div>
              );
            })}
          </div>
          
          <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '5px' }}>
            <h4>📋 Détails Techniques</h4>
            <pre style={{ fontSize: '12px', overflow: 'auto' }}>
              {JSON.stringify(animationData, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestAnimation;
