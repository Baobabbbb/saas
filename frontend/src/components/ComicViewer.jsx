import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ComicViewer.css';
import { downloadComicAsPDF } from '../utils/pdfUtils';
import { API_BASE_URL } from '../config/api';

const BACKEND_URL = API_BASE_URL;

// 🔤 Nettoie le titre pour créer un nom de fichier propre
const getSafeFilename = (title) => {
  return title
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "");
};

const ComicViewer = ({ comic }) => {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [imagesPerPage, setImagesPerPage] = useState(4);

  if (!comic || !comic.pages || comic.pages.length === 0) return null;

  // Organiser les images en pages selon le choix utilisateur
  const organizeImagesIntoPages = (images, perPage) => {
    const pages = [];
    for (let i = 0; i < images.length; i += perPage) {
      pages.push(images.slice(i, i + perPage));
    }
    return pages;
  };

  const organizedPages = organizeImagesIntoPages(comic.pages, imagesPerPage);
  const currentPage = organizedPages[currentPageIndex];

  const goToPrevious = () => {
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  const goToNext = () => {
    setCurrentPageIndex((prev) => Math.min(prev + 1, organizedPages.length - 1));
  };

  const handleImagesPerPageChange = (newPerPage) => {
    setImagesPerPage(newPerPage);
    setCurrentPageIndex(0); // Retour au début lors du changement
  };
  return (
    <div className="comic-viewer">
      <h2 className="comic-title">{comic.comic_metadata?.title || comic.title}</h2>
      
      {organizedPages.length > 1 && (
        <div className="comic-info">
          <p>📖 {comic.pages.length} images organisées en {organizedPages.length} pages de lecture</p>
        </div>
      )}

      <div className="comic-controls">
        <label htmlFor="images-per-page">Images par page : </label>
        <select 
          id="images-per-page"
          value={imagesPerPage} 
          onChange={(e) => handleImagesPerPageChange(Number(e.target.value))}
          className="images-per-page-select"
        >
          <option value={1}>1 image (pleine page)</option>
          <option value={2}>2 images</option>
          <option value={4}>4 images (grille)</option>
          <option value={6}>6 images</option>
          <option value={comic.pages.length}>Toutes ({comic.pages.length})</option>
        </select>
      </div>

      <div className="comic-pages">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPageIndex}
            className="comic-page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className={`comic-panels-grid panels-${currentPage.length}`}>
              {currentPage.map((panel, panelIndex) => (
                <div key={panelIndex} className="comic-panel">
                  <img
                    src={`${BACKEND_URL}${panel.image_url || panel}`}
                    alt={`Page ${currentPageIndex + 1}, Case ${panelIndex + 1}`}
                    className="comic-panel-image"
                  />
                </div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="comic-navigation">
        <button
          onClick={goToPrevious}
          disabled={currentPageIndex === 0}
          aria-label="Page précédente"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 5L7 10L12 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <span>Page {currentPageIndex + 1} / {organizedPages.length}</span>
        <button
          onClick={goToNext}
          disabled={currentPageIndex === organizedPages.length - 1}
          aria-label="Page suivante"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M8 5L13 10L8 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <div className="comic-download">
        <button className='download-pdf-button-b'
          onClick={() => {
            // Pour le PDF, on garde toutes les images individuelles
            const pdfPages = comic.pages.map(p => `${BACKEND_URL}${p.image_url || p}`);
            downloadComicAsPDF(pdfPages, getSafeFilename(comic.comic_metadata?.title || comic.title));
          }}
        >
          📄 Télécharger la BD ({comic.pages.length} images)
        </button>
      </div>
    </div>
  );
};

export default ComicViewer;
