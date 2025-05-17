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
import StoryPopup from './components/StoryPopup';

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

const getSafeFilename = (title) => {
  return title
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // supprime accents
    .toLowerCase().replace(/\s+/g, "_") // espaces → _
    .replace(/[^a-z0-9_]/g, ""); // caractères spéciaux supprimés
};

function App() {
  const [contentType, setContentType] = useState('story'); // 'story', 'rhyme', or 'audio'
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
  const [showFullStory, setShowFullStory] = useState(false);
  const [showStoryPopup, setShowStoryPopup] = useState(false);

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
    setStoryPages(splitTextIntoPages(generatedContent.content)); // Ajoute la pagination
    setCurrentPageIndex(0); // Reviens à la première page

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

const downloadPDF = async (title, content) => {
  if (!content || typeof content !== "string") {
    console.error("❌ Contenu invalide ou manquant pour le PDF.");
    return;
  }

  const doc = new jsPDF({
    orientation: "p",
    unit: "mm",
    format: "a4"
  });

  const marginTop = 40;
  const pageWidth = 210;
  const pageHeight = 297;
  const lineHeight = 12;
  const maxLinesPerPage = Math.floor((pageHeight - marginTop * 2) / lineHeight);
  const fontSize = 13;

  // 🏷️ Titre réel (extrait du markdown **titre**)
  let finalTitle = title;
  if (content.startsWith("**") && content.includes("**", 2)) {
    finalTitle = content.split("**")[1].trim();
    content = content.replace(`**${finalTitle}**`, "").trim();
  }

  // 🌠 Chargement de l’image de fond
  const loadImage = (url) =>
    new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = url;
      img.onload = () => resolve(img);
    });

  const backgroundImageUrl = "/assets/bg-stars.png";
  const backgroundImage = await loadImage(backgroundImageUrl);

  // ✂️ Texte découpé
  const lines = doc.splitTextToSize(content, 150); // max 150mm
  let currentLine = 0;

  for (let page = 0; currentLine < lines.length; page++) {
    if (page > 0) doc.addPage();

    doc.addImage(backgroundImage, "PNG", 0, 0, pageWidth, pageHeight, undefined, "FAST");

    // 🎨 Titre (uniquement page 1)
    if (page === 0) {
      doc.setFont("courier", "bold");
      doc.setFontSize(22);
      doc.setTextColor(110, 50, 230); // Violet
      doc.text(finalTitle, pageWidth / 2, marginTop - 20, { align: "center" });
    }

    // ✍️ Texte principal (gras et bleu nuit)
    doc.setFont("courier", "bold");
    doc.setFontSize(fontSize);
    doc.setTextColor(25, 25, 112); // Bleu nuit

    for (let i = 0; i < maxLinesPerPage && currentLine < lines.length; i++, currentLine++) {
      const y = marginTop + i * lineHeight;
      doc.text(lines[currentLine], pageWidth / 2, y, { align: "center" });
    }

    // 📄 Pagination
    doc.setFontSize(11);
    doc.setTextColor(106, 90, 205); // Violet doux
    doc.text(`Page ${page + 1}`, pageWidth - 15, 290, { align: "right" });
  }

  // 📁 Nom de fichier propre
  const safeTitle = finalTitle
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");

  doc.save(`${safeTitle}.pdf`);
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
    style={{ width: '100%', marginBottom: '0.25rem' }} // 🔧 Réduit l’espace sous l’audio
    src={`http://localhost:8000/${generatedResult.audio_path}`}
    download={generatedResult.audio_path.split('/').pop()}
  />
)}

{contentType === 'audio' && generatedResult?.content && (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem' // 🔧 Légèrement réduit l’espacement entre les deux boutons
    }}
  >
    <button
      onClick={() => setShowStoryPopup(true)}
      style={{
        padding: '0.6rem 1.4rem',
        backgroundColor: '#6B4EFF',
        color: '#fff',
        border: 'none',
        borderRadius: '0.5rem',
        cursor: 'pointer',
        fontWeight: '600'
      }}
    >
      📖 Ouvrir l’histoire
    </button>

    <button
      onClick={() => downloadPDF(generatedResult.title, generatedResult.content)}
      style={{
        padding: '0.6rem 1.4rem',
        backgroundColor: '#6B4EFF',
        color: '#fff',
        border: 'none',
        borderRadius: '0.5rem',
        cursor: 'pointer',
        fontWeight: '600'
      }}
    >
      📄 Télécharger en PDF
    </button>
  </div>
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
    
    {showStoryPopup && (
  <StoryPopup
    title={generatedResult.title}
    content={generatedResult.content}
    onClose={() => setShowStoryPopup(false)}
  />
)}
  </div>
);
}

export default App;
