import React, { useRef, useEffect, useState } from 'react';
import './ColoringPopup.css';
import { downloadColoringAsPDF } from '../utils/coloringPdfUtils';
import ColoringCanvas from './ColoringCanvas';

const ColoringPopup = ({ coloringResult, onClose, selectedTheme }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showColoringCanvas, setShowColoringCanvas] = useState(false);
  const [isZoomed, setIsZoomed] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
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
      // Utiliser le même titre que la page principale
      const title = coloringResult.title || (selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages');
      downloadColoringAsPDF(coloringResult.images, title);
    }
  };

  if (!coloringResult || !coloringResult.images || coloringResult.images.length === 0) {
    return null;
  }

  const imageItem = coloringResult.images[0]; // Une seule image
  const imageUrl = imageItem.image_url || imageItem;

  // Ouvrir le système de coloriage interactif
  const handleOpenColoring = () => {
    setShowColoringCanvas(true);
  };

  // Gestion du zoom
  const toggleZoom = () => {
    setIsZoomed(!isZoomed);
  };

  const zoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.5, 3));
    setIsZoomed(true);
  };

  const zoomOut = () => {
    if (zoomLevel > 1) {
      setZoomLevel(prev => Math.max(prev - 0.5, 1));
      if (zoomLevel - 0.5 <= 1) {
        setIsZoomed(false);
      }
    }
  };

  return (
    <>
      {showColoringCanvas ? (
        <ColoringCanvas
          imageUrl={imageUrl}
          onClose={() => setShowColoringCanvas(false)}
        />
      ) : (
        <div className="coloring-popup-overlay" onClick={handleOverlayClick}>
          <div className="coloring-popup-content" ref={popupRef}>
            <div className="coloring-background" />

            <button className="coloring-close-btn" onClick={onClose}>×</button>

            <button className="coloring-fullscreen-btn" onClick={toggleFullscreen}>
              {isFullscreen ? '✖ Quitter le plein écran' : '⛶ Plein écran'}
            </button>

            <div className="coloring-container">
              <h2 className="coloring-title">🎨 Votre coloriage</h2>

              <div className="coloring-zoom-controls">
                <button
                  className="coloring-zoom-btn"
                  onClick={zoomOut}
                  disabled={zoomLevel <= 1}
                  title="Zoom arrière"
                >
                  −
                </button>
                <span style={{ color: '#6B4EFF', fontWeight: 'bold', minWidth: '60px', textAlign: 'center' }}>
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  className="coloring-zoom-btn"
                  onClick={zoomIn}
                  disabled={zoomLevel >= 3}
                  title="Zoom avant"
                >
                  +
                </button>
              </div>

              <div className={`coloring-image-wrapper ${isZoomed ? 'zoomed' : ''}`} onClick={toggleZoom}>
                <img
                  src={imageUrl}
                  alt="Coloriage"
                  className={`coloring-popup-image ${isZoomed ? 'zoomed' : ''}`}
                  style={{ transform: `scale(${zoomLevel})` }}
                />
              </div>
              
              <div className="coloring-popup-actions">
                <button
                  className="coloring-open-btn"
                  onClick={handleOpenColoring}
                >
                  🎨 Colorier maintenant
                </button>
                <button
                  className="coloring-download-btn"
                  onClick={handleDownloadPDF}
                >
                  📄 Télécharger le coloriage
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ColoringPopup;
