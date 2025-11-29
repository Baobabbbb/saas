import React from 'react';
import './ColoringViewer.css';

const ColoringViewer = ({ coloringResult, onDownloadAll, onOpenColoring, onColorizeNow }) => {
  if (!coloringResult || !coloringResult.images || coloringResult.images.length === 0) {
    return null;
  }

  const handleDownloadImage = async (imageUrl, index) => {
    try {
      // Récupérer l'image via fetch pour créer un blob
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error('Erreur lors du téléchargement');
      
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      const baseName = (coloringResult?.title || 'coloriage').replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.download = `${baseName}_${index + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Nettoyer l'URL blob après un court délai
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Erreur lors du téléchargement:', error);
      // Fallback: essayer le téléchargement direct
      const link = document.createElement('a');
      link.href = imageUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      const baseName = (coloringResult?.title || 'coloriage').replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.download = `${baseName}_${index + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };
  return (
    <div className="coloring-viewer">
      <div className="coloring-grid">
        {coloringResult.images.map((imageItem, index) => {
          const imageUrl = imageItem.image_url || imageItem;
          return (
            <div
              key={index}
              className="coloring-item"
            >
              <div className="coloring-image-container">
                <img
                  src={imageUrl}
                  alt={`Coloriage ${index + 1}`}
                  className="coloring-image"
                />
              </div>
              <div className="coloring-info">
                <span>Coloriage {index + 1}</span>
                <div className="coloring-item-actions">
                  <button
                    className="coloring-item-btn coloring-open-btn"
                    onClick={() => onOpenColoring?.(imageUrl)}
                    title="Ouvrir le coloriage"
                  >
                    👁️ Ouvrir
                  </button>
                  <button
                    className="coloring-item-btn coloring-colorize-btn"
                    onClick={() => onColorizeNow?.(imageUrl)}
                    title="Colorier maintenant"
                  >
                    🎨 Colorier
                  </button>
                  <button
                    className="coloring-item-btn coloring-download-btn"
                    onClick={() => handleDownloadImage(imageUrl, index)}
                    title="Télécharger le coloriage"
                  >
                    📥 Télécharger
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="coloring-actions">
        <button className="download-all-button" onClick={onDownloadAll}>
          📄 Télécharger en PDF
        </button>
      </div>
    </div>
  );
};

export default ColoringViewer;
