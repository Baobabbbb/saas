import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ComicPopup.css';
import ComicViewer from './ComicViewer';

const ComicPopup = ({ comicResult, onClose }) => {
  if (!comicResult) return null;

  return (
    <motion.div
      className="comic-popup-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="comic-popup-content"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="comic-popup-header">
          <h2>📚 {comicResult.comic_metadata?.title || comicResult.title}</h2>
          <button 
            className="comic-popup-close"
            onClick={onClose}
            aria-label="Fermer"
          >
            ✕
          </button>
        </div>
        
        <div className="comic-popup-body">
          <ComicViewer comic={comicResult} />
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ComicPopup;
