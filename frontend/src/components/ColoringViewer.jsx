import React from 'react';
import './ColoringViewer.css';

const ColoringViewer = ({ coloringResult, onDownloadAll }) => {
  if (!coloringResult || !coloringResult.images || coloringResult.images.length === 0) {
    return null;
  }

  const handleDownloadImage = (imageUrl, index) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `coloriage_${index + 1}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
