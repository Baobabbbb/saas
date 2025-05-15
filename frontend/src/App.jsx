import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import StyleSelector from './components/StyleSelector';
import HeroCreator from './components/HeroCreator';
import StorySelector from './components/StorySelector';
import RhymeSelector from './components/RhymeSelector';
import AudioStorySelector from './components/AudioStorySelector';
import CustomRequest from './components/CustomRequest';
import GenerateButton from './components/GenerateButton';
import History from './components/History';
import ComicViewer from './components/ComicViewer';
import jsPDF from 'jspdf';

function splitTextIntoPages(text, maxChars = 600) {
  const sentences = text.split(/(?<=[.?!])\s+/);
  const pages = [];
  let currentPage = '';

  for (const sentence of sentences) {
    if ((currentPage + sentence).length > maxChars) {
      pages.push(currentPage.trim());
      currentPage = sentence + ' ';
    } else {
      currentPage += sentence + ' ';
    }
  }

  if (currentPage.trim()) {
    pages.push(currentPage.trim());
  }

  return pages;
}

function App() {
  const [contentType, setContentType] = useState('rhyme'); // 'story', 'rhyme', or 'audio'
  const [selectedStyle, setSelectedStyle] = useState(null);
  const [heroName, setHeroName] = useState('');
  const [selectedStory, setSelectedStory] = useState(null);
  const [customStory, setCustomStory] = useState('');
  const [selectedRhyme, setSelectedRhyme] = useState(null);
  const [customRhyme, setCustomRhyme] = useState('');
  const [selectedAudioStory, setSelectedAudioStory] = useState(null);
  const [customAudioStory, setCustomAudioStory] = useState('');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [customRequest, setCustomRequest] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  {/*const [showConfetti, setShowConfetti] = useState(false);*/}
  const [comicResult, setComicResult] = useState(null);
  const [generatedResult, setGeneratedResult] = useState(null);

  // User account state
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [creations, setCreations] = useState([]);

  // 📖 Pagination : découpe le texte en pages
  const storyPages = useMemo(() => {
    if (contentType === 'audio' && generatedResult?.content) {
      return splitTextIntoPages(generatedResult.content);
    }
    return [];
  }, [generatedResult, contentType]);

  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  // Check if user is logged in on component mount
  useEffect(() => {
    const userToken = localStorage.getItem('userToken');
    if (userToken) {
      setIsLoggedIn(true);
      // Load user creations from localStorage
      loadCreations();
    }

    // Check if URL has #historique hash
    if (window.location.hash === '#historique') {
      setShowHistory(true);
    }

    // Listen for hash changes
    const handleHashChange = () => {
      setShowHistory(window.location.hash === '#historique');
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const loadCreations = () => {
    const savedCreations = localStorage.getItem('userCreations');
    if (savedCreations) {
      setCreations(JSON.parse(savedCreations));
    }
  };

  const handleLogin = (credentials) => {
    const userName = credentials.email.split('@')[0];
    localStorage.setItem('userToken', 'demo-token-123');
    localStorage.setItem('userName', userName);
    setIsLoggedIn(true);

    if (!localStorage.getItem('userCreations')) {
      const demoCreations = [
        {
          id: '1',
          type: 'story',
          title: 'Les aventures de Lulu',
          createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          content: 'Il était une fois un petit lapin nommé Lulu...'
        },
        {
          id: '2',
          type: 'rhyme',
          title: 'La comptine des étoiles',
          createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          content: 'Brille, brille, petite étoile...'
        },
        {
          id: '3',
          type: 'audio',
          title: 'Le conte du petit dragon',
          createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          content: 'Un petit dragon qui cherchait des amis...'
        }
      ];
      localStorage.setItem('userCreations', JSON.stringify(demoCreations));
      setCreations(demoCreations);
    } else {
      loadCreations();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userName');
    setIsLoggedIn(false);
    setShowHistory(false);
    window.location.hash = '';
  };

  const handleRegister = (userData) => {
    localStorage.setItem('userToken', 'demo-token-123');
    localStorage.setItem('userName', userData.name);
    setIsLoggedIn(true);

    if (!localStorage.getItem('userCreations')) {
      localStorage.setItem('userCreations', JSON.stringify([]));
    }
    loadCreations();
  };

  const handleGenerate = async () => {
  setIsGenerating(true);
  // setShowConfetti(true);

  try {
    let generatedContent = null;

    if (contentType === 'story') {
      const payload = {
        style: selectedStyle,
        hero_name: heroName,
        story_type: selectedStory === 'custom' ? customStory : selectedStory,
        custom_request: customRequest
      };

      const response = await fetch('http://127.0.0.1:8000/generate_comic/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
      setComicResult(generatedContent); // pour l’affichage BD
    }

    if (contentType === 'rhyme') {
      const payload = {
        rhyme_type: selectedRhyme === 'custom' ? customRhyme : selectedRhyme,
        custom_request: customRequest
      };

      const response = await fetch('http://127.0.0.1:8000/generate_rhyme/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
    }

    if (contentType === 'audio') {
      const payload = {
        story_type: selectedAudioStory === 'custom' ? customAudioStory : selectedAudioStory,
        voice: selectedVoice,
        custom_request: customRequest
      };

      const response = await fetch('http://127.0.0.1:8000/generate_audio_story/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    setGeneratedResult(generatedContent);

    // Déterminer le titre
    let title;
    if (contentType === 'story') {
      title = generatedContent.title || `L'histoire de ${heroName}`;
    } else if (contentType === 'rhyme') {
      title = generatedContent.title || `Comptine générée`;
    } else if (contentType === 'audio') {
      title = generatedContent.title || `Conte généré`;
    }

    const newCreation = {
      id: Date.now().toString(),
      type: contentType,
      title: title,
      createdAt: new Date().toISOString(),
      content: generatedContent?.content || generatedContent || 'Contenu généré...',
      audio_path: generatedContent?.audio_path || null
    };

    if (isLoggedIn) {
      const updatedCreations = [...creations, newCreation];
      setCreations(updatedCreations);
      localStorage.setItem('userCreations', JSON.stringify(updatedCreations));
    }

    // setTimeout(() => setShowConfetti(false), 3000);
  } catch (error) {
    console.error('❌ Erreur de génération :', error);
  } finally {
    setIsGenerating(false);
  }
};

  const handleSelectCreation = (creation) => {
    setShowHistory(false);
    window.location.hash = '';
  };

  const handleCloseHistory = () => {
    setShowHistory(false);
    window.location.hash = '';
  };

  const handleDeleteCreation = (idToDelete) => {
    const updated = creations.filter(c => c.id !== idToDelete);
    setCreations(updated);
    localStorage.setItem('userCreations', JSON.stringify(updated));
  };

  const isFormValid = () => {
    if (contentType === 'story') {
      if (!selectedStyle) return false;
      if (!heroName) return false;
      if (!selectedStory) return false;
      if (selectedStory === 'custom' && !customStory.trim()) return false;
    } else if (contentType === 'rhyme') {
      if (!selectedRhyme) return false;
      if (selectedRhyme === 'custom' && !customRhyme.trim()) return false;
    } else if (contentType === 'audio') {
      if (!selectedAudioStory) return false;
      if (selectedAudioStory === 'custom' && !customAudioStory.trim()) return false;
      // if (!selectedVoice) return false;
    }
    return true;
  };

  // Animation variants for content sections
  const contentVariants = {
    hidden: { opacity: 0, height: 0, marginBottom: 0 },
    visible: { opacity: 1, height: 'auto', marginBottom: '1rem' },
    exit: { opacity: 0, height: 0, marginBottom: 0 }
  };

// Base64 Fredoka One – tronquée pour lisibilité, à remplacer par la vraie si besoin
const fredokaFont = `
AAEAAAAPAIAAAwBwRkZUTVJNzvsAAAD4AAAAYGNtYXAVP88fAAABHAAAAExnYXNwAAAAEAAAAXgAAABUZ2x5Zp0qb7cAAAGQAAABsGhlYWQG1QYgAAACbAAAADZoaGVhA5wCtAAAAoQAAAAkaG10eAYAAAAAAAKwAAAALGxvY2EDpAAQAAAC0AAAAAxtYXhwAAkAHAAAtgAAAAgbmFtZVeY8OoAAALQAAABinBvc3QAAwAAAADEAAAACnByZXB5cmB4AAAEZAAAACAAAwAAAAAAAAABAAAAAQAAAAAAAAABAAAACwBiAAMAAQAAABwBiAAAAAEAAgAAAAEAAQAAAEAAOAAEAAAAAAAEAAQAAAEAAAAABAACAAAAAAAgAAAAAAAAAAQAAAAAAAAAAAAAAAAAAUAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
`.replace(/\s+/g, '');

// Fonction d'export PDF avec style enfantin et fond étoilé
const downloadPDF = (title, text) => {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'pt',
    format: 'a4'
  });

  // Charger et définir Fredoka
  doc.addFileToVFS('Fredoka.ttf', fredokaFont);
  doc.addFont('Fredoka.ttf', 'Fredoka', 'normal');
  doc.setFont('Fredoka');
  doc.setFontSize(18);
  doc.setTextColor(80, 60, 140);

  // Image de fond (accessible depuis le dossier public)
  const backgroundImageUrl = '/assets/bg-stars.png';

  // Charger l’image de fond de façon asynchrone
  const img = new Image();
  img.crossOrigin = 'Anonymous';
  img.src = backgroundImageUrl;

  img.onload = () => {
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const lines = doc.splitTextToSize(text, pageWidth - 80);
    const linesPerPage = 40;
    let currentY = 100;

    let currentPage = 1;

    for (let i = 0; i < lines.length; i += linesPerPage) {
      if (i !== 0) {
        doc.addPage();
        currentY = 100;
      }

      // Dessiner le fond étoilé
      doc.addImage(img, 'PNG', 0, 0, pageWidth, pageHeight);

      // Titre uniquement sur la première page
      if (currentPage === 1) {
        doc.setFontSize(22);
        doc.text(`L’histoire de ${title}`, pageWidth / 2, 60, { align: 'center' });
        doc.setFontSize(14);
      }

      const pageLines = lines.slice(i, i + linesPerPage);
      doc.text(pageLines, 40, currentY, { maxWidth: pageWidth - 80, lineHeightFactor: 1.5 });

      currentPage++;
    }

    const filename = `histoire_${title.toLowerCase().replace(/\s+/g, '_')}.pdf`;
    doc.save(filename);
  };

  img.onerror = () => {
    console.error("❌ Impossible de charger l’image de fond du PDF.");
  };
};

 return (
  <div className="app-container">
    {/*{showConfetti && (
      <Confetti
        recycle={false}
        numberOfPieces={200}
        colors={['#6B4EFF', '#FF85A1', '#FFD166', '#A0E7E5']}
      />
    )}*/}

    <Header
      isLoggedIn={isLoggedIn}
      onLogin={handleLogin}
      onLogout={handleLogout}
      onRegister={handleRegister}
    />

    <main className="main-content">
      <div className="content-wrapper">
        <motion.div
          className="creation-panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ContentTypeSelector
            contentType={contentType}
            setContentType={setContentType}
          />

          <AnimatePresence mode="wait">
            {contentType === 'story' && (
              <motion.div
                key="style-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <StyleSelector
                  selectedStyle={selectedStyle}
                  setSelectedStyle={setSelectedStyle}
                />
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">
            {contentType === 'story' && (
              <motion.div
                key="hero-creator"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <HeroCreator
                  heroName={heroName}
                  setHeroName={setHeroName}
                />
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">
            {contentType === 'story' ? (
              <motion.div
                key="story-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <StorySelector
                  selectedStory={selectedStory}
                  setSelectedStory={setSelectedStory}
                  customStory={customStory}
                  setCustomStory={setCustomStory}
                />
              </motion.div>
            ) : contentType === 'rhyme' ? (
              <motion.div
                key="rhyme-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <RhymeSelector
                  selectedRhyme={selectedRhyme}
                  setSelectedRhyme={setSelectedRhyme}
                  customRhyme={customRhyme}
                  setCustomRhyme={setCustomRhyme}
                />
              </motion.div>
            ) : (
              <motion.div
                key="audio-story-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <AudioStorySelector
                  selectedAudioStory={selectedAudioStory}
                  setSelectedAudioStory={setSelectedAudioStory}
                  customAudioStory={customAudioStory}
                  setCustomAudioStory={setCustomAudioStory}
                  selectedVoice={selectedVoice}
                  setSelectedVoice={setSelectedVoice}
                />
              </motion.div>
            )}
          </AnimatePresence>

          <CustomRequest
            customRequest={customRequest}
            setCustomRequest={setCustomRequest}
            stepNumber={contentType === 'story' ? 5 : 3}
          />

          <GenerateButton
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            isDisabled={!isFormValid()}
            contentType={contentType}
          />
        </motion.div>

        <div className="preview-column">
          <motion.div
            className="preview-panel"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="preview-container">
              <div className={`comic-preview ${!comicResult && !generatedResult ? 'empty' : ''}`}>
                <AnimatePresence mode="wait">
  {isGenerating ? (
    <motion.div
      className="generating-animation"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="generating"
    >
      <div className="loading-dots">
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
      <p>
        {contentType === 'story'
          ? 'Création de la BD en cours...'
          : contentType === 'rhyme'
          ? 'Création de la comptine en cours...'
          : 'Création de l\'histoire en cours...'}
      </p>
    </motion.div>
  ) : comicResult && contentType === 'story' ? (
    <ComicViewer comic={comicResult} />
  ) : (
    
    <motion.div
  className="preview-placeholder"
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  key="placeholder"
>
  {/*<img
    src="/cloud-logo.svg"
    alt="BDKids logo"
    className="preview-logo"
  />*/}

  {!generatedResult?.content && (
    <div className="empty-preview">
    <p>
      {contentType === 'story'
        ? 'Votre bande dessinée apparaîtra ici'
        : contentType === 'rhyme'
        ? 'Votre comptine apparaîtra ici'
        : 'Votre histoire apparaîtra ici'}
    </p>
    </div>
  )}

  {/* 📖 Histoire paginée */}
  {contentType === 'audio' && storyPages.length > 0 && (
    <div className="book-page">
      <div className="page-text">
        {storyPages[currentPageIndex]}
      </div>
      <div className="page-navigation">
  {/* Flèche gauche */}
  <button
    onClick={() => setCurrentPageIndex((prev) => Math.max(prev - 1, 0))}
    disabled={currentPageIndex === 0}
  >
    ◀
  </button>

  {/* Pagination + bouton PDF */}
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <span>Page {currentPageIndex + 1} / {storyPages.length}</span>
  </div>

  {/* Flèche droite */}
  <button
    onClick={() => setCurrentPageIndex((prev) => Math.min(prev + 1, storyPages.length - 1))}
    disabled={currentPageIndex === storyPages.length - 1}
  >
    ▶
  </button>
</div>
    </div>
  )}

  {/* 📄 Texte plein (non paginé) si besoin (ex: debug autre type) */}
  {generatedResult?.content && contentType !== 'rhyme' && contentType !== 'audio' && (
    <div
      style={{
      whiteSpace: 'pre-wrap',
      textAlign: 'left',
      marginTop: '1rem',
      padding: '1.5rem',
      background: '#fff',
      borderRadius: '1rem',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
      fontSize: '1rem',
      lineHeight: '1.6',
      width: '100%',
      maxWidth: '640px',
  }}
    >
      {generatedResult.content}
    </div>
  )}

  {/* 🎵 Audio présent */}
  {generatedResult?.audio_path && (
    <audio
      controls
      style={{ marginTop: '1rem', width: '100%' }}
      src={`http://localhost:8000/${generatedResult.audio_path}`}
    />
  )}

  {/* 📄 Bouton PDF pour histoires */}
  {contentType === 'audio' && generatedResult?.content && (
    <button
      onClick={() => downloadPDF(selectedAudioStory, generatedResult.content)}
      style={{
        marginTop: '1rem',
        padding: '0.5rem 1rem',
        backgroundColor: '#6B4EFF',
        color: '#fff',
        border: 'none',
        borderRadius: '0.5rem',
        cursor: 'pointer'
      }}
    >
      📄 Télécharger en PDF
    </button>
  )}
</motion.div>

  )}
</AnimatePresence>

              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>

    <AnimatePresence>
      {showHistory && (
        <motion.div
          className="history-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <History
            creations={creations}
            onClose={handleCloseHistory}
            onSelect={handleSelectCreation}
            onDelete={handleDeleteCreation}
          />
        </motion.div>
      )}
    </AnimatePresence>
  </div>
);
}

export default App;
