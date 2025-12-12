import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { addHerbbieSuffix } from '../utils/coloringPdfUtils';
import './ComicsPopup.css';

const ComicsPopup = ({ comic, onClose, baseUrl }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!comic || !comic.pages || comic.pages.length === 0) {
    return null;
  }

  // Fonction helper pour obtenir l'URL d'image correcte
  // Gère les URLs Supabase Storage complètes (https://) et les chemins relatifs
  const getImageUrl = (imagePath) => {
    if (!imagePath) return null;
    
    // Si c'est déjà une URL complète (Supabase Storage), l'utiliser directement
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath;
    }
    
    // Sinon, construire l'URL avec baseUrl (ancien format local)
    return `${baseUrl}${imagePath}`;
  };

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

  const downloadPage = async () => {
    const imageUrl = getImageUrl(currentPageData.image_url);
    if (!imageUrl) return;
    
    try {
      // Récupérer l'image via fetch pour créer un blob
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error('Erreur lors du téléchargement');
      
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.download = addHerbbieSuffix(`${safeTitle}_page_${currentPage + 1}`, 'png');
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
    const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.download = addHerbbieSuffix(`${safeTitle}_page_${currentPage + 1}`, 'png');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    }
  };

  const downloadAllPages = async () => {
    for (let index = 0; index < comic.pages.length; index++) {
      const page = comic.pages[index];
        const imageUrl = getImageUrl(page.image_url);
      if (!imageUrl) continue;
      
      try {
        // Récupérer l'image via fetch pour créer un blob
        const response = await fetch(imageUrl);
        if (!response.ok) throw new Error('Erreur lors du téléchargement');
        
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = blobUrl;
        const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        link.download = addHerbbieSuffix(`${safeTitle}_page_${index + 1}`, 'png');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Nettoyer l'URL blob après un court délai
        setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
      } catch (error) {
        console.error(`Erreur lors du téléchargement de la page ${index + 1}:`, error);
        // Fallback: essayer le téléchargement direct
        const link = document.createElement('a');
        link.href = imageUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        const safeTitle = (comic.title || 'bande_dessinee').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        link.download = addHerbbieSuffix(`${safeTitle}_page_${index + 1}`, 'png');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      
      // Délai entre chaque téléchargement
      if (index < comic.pages.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
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
          {/* Bouton de fermeture */}
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>

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
                  src={getImageUrl(currentPageData.image_url)}
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
            <button className="action-btn" onClick={toggleFullscreen}>
              <span className="btn-icon">{isFullscreen ? '🔲' : '🔳'}</span>
              {isFullscreen ? 'Réduire' : 'Plein écran'}
            </button>

            <button className="action-btn" onClick={downloadPage}>
              <span className="btn-icon">💾</span>
              Télécharger cette planche
            </button>

            {totalPages > 1 && (
              <button className="action-btn" onClick={downloadAllPages}>
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
                      src={getImageUrl(page.image_url)}
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

