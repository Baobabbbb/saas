import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import './AnimationViewer.css';

const AnimationViewer = ({ animation, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const videoRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const updateTime = () => setCurrentTime(video.currentTime);
    const updateDuration = () => setDuration(video.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    video.addEventListener('timeupdate', updateTime);
    video.addEventListener('loadedmetadata', updateDuration);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', updateTime);
      video.removeEventListener('loadedmetadata', updateDuration);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    video.currentTime = percent * duration;
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const toggleFullscreen = () => {
    const container = containerRef.current;
    if (!container) return;

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen();
      } else if (container.webkitRequestFullscreen) {
        container.webkitRequestFullscreen();
      } else if (container.msRequestFullscreen) {
        container.msRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const downloadAnimation = () => {
    const link = document.createElement('a');
    link.href = animation.videoUrl;
    link.download = `${animation.title || 'animation'}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (!animation) return null;

  return (
    <motion.div 
      className={`animation-viewer ${isFullscreen ? 'fullscreen' : ''}`}
      ref={containerRef}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      <div className="animation-header">
        <div className="animation-info">
          <h2 className="animation-title">{animation.title}</h2>
          <p className="animation-description">{animation.description}</p>
        </div>
        
        <div className="animation-controls-top">
          <button 
            className="control-btn fullscreen-btn"
            onClick={toggleFullscreen}
            title={isFullscreen ? "Quitter le plein écran" : "Plein écran"}
          >
            {isFullscreen ? '⤓' : '⤢'}
          </button>
          
          <button 
            className="control-btn download-btn"
            onClick={downloadAnimation}
            title="Télécharger l'animation"
          >
            📥
          </button>
          
          {onClose && (
            <button 
              className="control-btn close-btn"
              onClick={onClose}
              title="Fermer"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="video-container">
        <video
          ref={videoRef}
          className="animation-video"
          src={animation.videoUrl}
          poster={animation.thumbnailUrl}
          controls={false}
          loop
        />
        
        <div className="video-overlay">
          <button 
            className="play-pause-btn"
            onClick={togglePlay}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>
        </div>
      </div>

      <div className="animation-controls">
        <div className="progress-container">
          <div 
            className="progress-bar"
            onClick={handleSeek}
          >
            <div 
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="time-display">
            <span>{formatTime(currentTime)}</span>
            <span>/</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="control-row">
          <button 
            className="control-btn play-btn"
            onClick={togglePlay}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>

          <div className="volume-control">
            <span className="volume-icon">🔊</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              className="volume-slider"
            />
          </div>

          <div className="animation-metadata">
            <span className="metadata-item">
              <span className="metadata-label">Style:</span>
              <span className="metadata-value">{animation.style}</span>
            </span>
            <span className="metadata-item">
              <span className="metadata-label">Durée:</span>
              <span className="metadata-value">{animation.duration}s</span>
            </span>
          </div>
        </div>
      </div>

      <div className="animation-actions">
        <motion.button
          className="action-btn primary"
          onClick={downloadAnimation}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          📥 Télécharger l'animation
        </motion.button>
        
        <motion.button
          className="action-btn secondary"
          onClick={() => {
            if (navigator.share && animation.videoUrl) {
              navigator.share({
                title: animation.title,
                text: animation.description,
                url: animation.videoUrl
              });
            }
          }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🔗 Partager
        </motion.button>
      </div>
    </motion.div>
  );
};

export default AnimationViewer;
