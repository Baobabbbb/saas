import React, { useState } from 'react';
import './ComicViewer.css';

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
      <h2 className="comic-title">{comic.title}</h2>

      <div className="comic-page">
        <img src={page.image_url} alt={`Page ${currentPageIndex + 1}`} className="comic-image" />
        <p className="comic-text">{page.text}</p>
      </div>

      <div className="comic-navigation">
        <button onClick={goToPrevious} disabled={currentPageIndex === 0}>⬅️</button>
        <span>Page {currentPageIndex + 1} / {comic.pages.length}</span>
        <button onClick={goToNext} disabled={currentPageIndex === comic.pages.length - 1}>➡️</button>
      </div>

      <div className="comic-download">
        <a href="/static/final_page.png" download>
          📥 Télécharger la BD complète
        </a>
      </div>
    </div>
  );
};

export default ComicViewer;
