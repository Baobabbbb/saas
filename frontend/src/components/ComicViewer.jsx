import React from 'react';
import './ComicViewer.css';

const ComicViewer = ({ comic }) => {
  if (!comic || !comic.pages) return null;

  return (
    <div className="comic-viewer">
      <h2 className="comic-title">{comic.title}</h2>
      <div className="comic-pages">
        {comic.pages.map((page, index) => (
          <div className="comic-page" key={index}>
            <img src={page.image_url} alt={`Page ${index + 1}`} className="comic-image" />
            <p className="comic-text">{page.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComicViewer;
