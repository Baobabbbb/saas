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
  const imagesPerPage = 4; // Fixé à 4 images par page

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

  return (
    <div className="comic-viewer">
      <h2 className="comic-title">{comic.comic_metadata?.title || comic.title}</h2>
      
      {organizedPages.length > 1 && (
        <div className="comic-info">
          <p>📖 {comic.pages.length} images organisées en {organizedPages.length} pages de lecture (4 images par page)</p>
          {comic.pages.some(p => p.dialogues && p.dialogues.length > 0) && (
            <p>💬 Cette BD contient des bulles de dialogue interactives - survolez les images pour les voir !</p>
          )}
        </div>
      )}

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
              {currentPage.map((panel, panelIndex) => {
                const hasDialogues = panel.dialogues && panel.dialogues.length > 0;
                const dialogueText = hasDialogues ? 
                  panel.dialogues.map(d => `${d.character}: "${d.text}"`).join(' | ') : 
                  null;
                
                return (
                  <div 
                    key={panelIndex} 
                    className={`comic-panel ${hasDialogues ? 'comic-panel-with-dialogue' : ''}`}
                  >
                    <img
                      src={`${BACKEND_URL}${panel.image_url || panel}`}
                      alt={`Page ${currentPageIndex + 1}, Case ${panelIndex + 1}`}
                      className={`comic-panel-image ${hasDialogues ? 'comic-panel-image-with-dialogue' : ''}`}
                      title={hasDialogues ? `Bulles de dialogue : ${dialogueText}` : `Page ${currentPageIndex + 1}, Case ${panelIndex + 1}`}
                    />
                    
                    {hasDialogues && (
                      <>
                        <div className="comic-panel-dialogue-info">
                          {panel.dialogues.length} bulle{panel.dialogues.length > 1 ? 's' : ''}
                        </div>
                        <div className="comic-panel-dialogue-tooltip">
                          {panel.dialogues.map((dialogue, idx) => (
                            <div key={idx} style={{ marginBottom: idx < panel.dialogues.length - 1 ? '4px' : '0' }}>
                              <strong>{dialogue.character}:</strong> "{dialogue.text}"
                              {dialogue.type !== 'speech' && (
                                <em style={{ fontSize: '0.7rem', color: '#ccc' }}>
                                  ({dialogue.type === 'thought' ? 'pensée' : 
                                    dialogue.type === 'shout' ? 'cri' : 
                                    dialogue.type === 'whisper' ? 'chuchotement' : dialogue.type})
                                </em>
                              )}
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {organizedPages.length > 1 && (
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
      )}

      <div className="comic-download">
        <button className='download-pdf-button-b'
          onClick={() => {
            // Pour le PDF, on garde toutes les images individuelles
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
