import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ComicViewer.css';
import { downloadComicAsPDF } from '../utils/pdfUtils';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

// 🔤 Nettoie le titre pour créer un nom de fichier propre
const getSafeFilename = (title) => {
  return title
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "");
};

const ComicViewer = ({ comic }) => {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  if (!comic || !comic.pages || comic.pages.length === 0) return null;

  const page = comic.pages[currentPageIndex];

  const goToPrevious = () => {
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  const goToNext = () => {
    setCurrentPageIndex((prev) => Math.min(prev + 1, comic.pages.length - 1));
  };
  return (
    <div className="comic-viewer">
      <h2 className="comic-title">{comic.comic_metadata?.title || comic.title}</h2>

      <div className="comic-pages">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPageIndex}
            className="comic-page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}          >
            <img
              src={`${BACKEND_URL}${page.image_url || page}`}
              alt={`Page ${currentPageIndex + 1}`}
              className="comic-image"
            />
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
        <span>Page {currentPageIndex + 1} / {comic.pages.length}</span>
        <button
          onClick={goToNext}
          disabled={currentPageIndex === comic.pages.length - 1}
          aria-label="Page suivante"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M8 5L13 10L8 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <div className="comic-download">        <button className='download-pdf-button-b'
          onClick={() => {
            const pdfPages = comic.pages.map(p => `${BACKEND_URL}${p.image_url || p}`);
            downloadComicAsPDF(pdfPages, getSafeFilename(comic.comic_metadata?.title || comic.title));
          }}
        >
          📄 Télécharger la BD
        </button>
      </div>
    </div>
  );
};

export default ComicViewer;
