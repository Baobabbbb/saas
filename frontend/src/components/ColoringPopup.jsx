import React, { useRef, useEffect, useState } from 'react';
import './ColoringPopup.css';
import { downloadColoringAsPDF } from '../utils/coloringPdfUtils';

const ColoringPopup = ({ coloringResult, onClose, selectedTheme }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const popupRef = useRef(null);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      popupRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target.classList.contains('coloring-popup-overlay')) {
      onClose();
    }
  };
  const handleDownloadPDF = () => {
    if (coloringResult?.images) {
      const title = selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages';
      downloadColoringAsPDF(coloringResult.images, title);
    }
  };

  if (!coloringResult || !coloringResult.images || coloringResult.images.length === 0) {
    return null;
  }

  const imageItem = coloringResult.images[0]; // Une seule image
  const imageUrl = imageItem.image_url || imageItem;

  return (
    <div className="coloring-popup-overlay" onClick={handleOverlayClick}>
      <div className="coloring-popup-content" ref={popupRef}>
        <div className="coloring-background" />

        <button className="coloring-close-btn" onClick={onClose}>×</button>

        <button className="coloring-fullscreen-btn" onClick={toggleFullscreen}>
          {isFullscreen ? '✖ Quitter le plein écran' : '⛶ Plein écran'}
        </button>

        <div className="coloring-container">
          <h2 className="coloring-title">🎨 Votre coloriage</h2>
          
          <div className="coloring-image-wrapper">
            <img
              src={imageUrl}
              alt="Coloriage"
              className="coloring-popup-image"
            />
          </div>          <div className="coloring-popup-actions">            <button
              className="coloring-download-btn"
              onClick={handleDownloadPDF}
            >
              📄 Télécharger le coloriage
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColoringPopup;
