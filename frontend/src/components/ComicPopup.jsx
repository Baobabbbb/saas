import React, { useRef, useState } from 'react';
import './StoryPopup.css'; // réutilise le style
import ComicViewer from './ComicViewer';

const ComicPopup = ({ comic, onClose }) => {
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
    if (e.target.classList.contains('story-popup-overlay')) {
      onClose();
    }
  };

  return (
    <div className="story-popup-overlay" onClick={handleOverlayClick}>
      <div className="story-popup-content" ref={popupRef}>
        <div className="story-background" />

        <button className="story-close-btn" onClick={onClose}>×</button>

        <button className="story-fullscreen-btn" onClick={toggleFullscreen}>
          {isFullscreen ? '✖ Quitter le plein écran' : '⛶ Plein écran'}
        </button>

        <div className="story-scroll">
          <ComicViewer comic={comic} />
        </div>
      </div>
    </div>
  );
};

export default ComicPopup;
