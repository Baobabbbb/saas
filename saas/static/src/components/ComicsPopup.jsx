import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ComicsPopup.css';

const ComicsPopup = ({ comic, onClose, baseUrl }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!comic || !comic.pages || comic.pages.length === 0) {
    return null;
  }

  const currentPageData = comic.pages[currentPage];
  const totalPages = comic.pages.length;

  const goToNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const downloadPage = () => {
    const imageUrl = `${baseUrl}${currentPageData.image_url}`;
    const link = document.createElement('a');
    link.href = imageUrl;
    const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
    link.download = `${safeTitle}_page_${currentPage + 1}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadAllPages = () => {
    comic.pages.forEach((page, index) => {
      setTimeout(() => {
        const imageUrl = `${baseUrl}${page.image_url}`;
        const link = document.createElement('a');
        link.href = imageUrl;
        const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        link.download = `${safeTitle}_page_${index + 1}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }, index * 500); // Délai entre chaque téléchargement
    });
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <AnimatePresence>
      <motion.div
        className="comics-popup-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className={`comics-popup-container ${isFullscreen ? 'fullscreen' : ''}`}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* En-tête */}
          <div className="comics-popup-header">
            <div className="comic-title-section">
              <h2 className="comic-title">{comic.title}</h2>
              <p className="comic-synopsis">{comic.synopsis}</p>
              <div className="comic-meta">
                <span className="meta-item">
                  <span className="meta-icon">🎨</span>
                  {comic.art_style}
                </span>
                <span className="meta-item">
                  <span className="meta-icon">📄</span>
                  {totalPages} {totalPages === 1 ? 'planche' : 'planches'}
                </span>
                <span className="meta-item">
                  <span className="meta-icon">🎯</span>
                  {totalPages * 4} cases
                </span>
              </div>
            </div>
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          </div>

          {/* Visionneuse de planche */}
          <div className="comics-viewer">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPage}
                className="page-display"
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.3 }}
              >
                <img
                  src={`${baseUrl}${currentPageData.image_url}`}
                  alt={`Planche ${currentPage + 1}`}
                  className="page-image"
                  onClick={toggleFullscreen}
                />
                <div className="page-info">
                  Planche {currentPage + 1} / {totalPages}
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Boutons de navigation */}
            {totalPages > 1 && (
              <div className="page-navigation">
                <button
                  className="nav-btn prev-btn"
                  onClick={goToPrevPage}
                  disabled={currentPage === 0}
                >
                  ← Précédent
                </button>
                
                <div className="page-dots">
                  {comic.pages.map((_, index) => (
                    <button
                      key={index}
                      className={`page-dot ${index === currentPage ? 'active' : ''}`}
                      onClick={() => setCurrentPage(index)}
                      aria-label={`Aller à la planche ${index + 1}`}
                    />
                  ))}
                </div>

                <button
                  className="nav-btn next-btn"
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages - 1}
                >
                  Suivant →
                </button>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="comics-actions">
            <button className="action-btn secondary-btn" onClick={toggleFullscreen}>
              <span className="btn-icon">{isFullscreen ? '🔲' : '🔳'}</span>
              {isFullscreen ? 'Réduire' : 'Plein écran'}
            </button>

            <button className="action-btn primary-btn" onClick={downloadPage}>
              <span className="btn-icon">💾</span>
              Télécharger cette planche
            </button>

            {totalPages > 1 && (
              <button className="action-btn primary-btn" onClick={downloadAllPages}>
                <span className="btn-icon">📥</span>
                Télécharger toutes les planches
              </button>
            )}
          </div>

          {/* Miniatures (si plusieurs pages) */}
          {totalPages > 1 && (
            <div className="thumbnails-section">
              <h4>Toutes les planches</h4>
              <div className="thumbnails-grid">
                {comic.pages.map((page, index) => (
                  <motion.div
                    key={index}
                    className={`thumbnail ${index === currentPage ? 'active' : ''}`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setCurrentPage(index)}
                  >
                    <img
                      src={`${baseUrl}${page.image_url}`}
                      alt={`Miniature planche ${index + 1}`}
                    />
                    <div className="thumbnail-label">
                      Planche {index + 1}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ComicsPopup;

