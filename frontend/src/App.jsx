import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import RhymeSelector from './components/RhymeSelector';
import AudioStorySelector from './components/AudioStorySelector';
import AnimationSelector from './components/AnimationSelector';
import CustomRequest from './components/CustomRequest';
import GenerateButton from './components/GenerateButton';
import History from './components/History';
import AnimationViewer from './components/AnimationViewer';
import AnimationPopup from './components/AnimationPopup';
import StoryPopup from './components/StoryPopup';
import ColoringSelector from './components/ColoringSelector';
import ColoringViewer from './components/ColoringViewer';
import ColoringPopup from './components/ColoringPopup';
import useSupabaseUser from './hooks/useSupabaseUser';
import veo3Service from './services/veo3';
import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';

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

function App() {  const [contentType, setContentType] = useState('animation'); // 'rhyme', 'audio', or 'animation'
  const [selectedRhyme, setSelectedRhyme] = useState(null);
  const [customRhyme, setCustomRhyme] = useState('');
  const [selectedAudioStory, setSelectedAudioStory] = useState(null);
  const [customAudioStory, setCustomAudioStory] = useState('');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [customRequest, setCustomRequest] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  {/*const [showConfetti, setShowConfetti] = useState(false);*/}  const [generatedResult, setGeneratedResult] = useState(null);
  const [showFullStory, setShowFullStory] = useState(false);
  const [showStoryPopup, setShowStoryPopup] = useState(false);
  const [showColoringPopup, setShowColoringPopup] = useState(false);

  // Animation states
  const [selectedAnimationStyle, setSelectedAnimationStyle] = useState(null);
  const [selectedAnimationTheme, setSelectedAnimationTheme] = useState(null);
  const [animationDuration, setAnimationDuration] = useState(8); // Fal-ai/Veo3 ne supporte que 8s
  const [animationPrompt, setAnimationPrompt] = useState('');
  const [animationOrientation, setAnimationOrientation] = useState(null); // 'landscape' or 'portrait'
  const [uploadedAnimationImage, setUploadedAnimationImage] = useState(null);  const [animationResult, setAnimationResult] = useState(null);
  const [showAnimationPopup, setShowAnimationPopup] = useState(false);
  const [animationGenerationStatus, setAnimationGenerationStatus] = useState(null);
  // Coloring states
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [coloringResult, setColoringResult] = useState(null);

  // User account state
  const { user, loading } = useSupabaseUser();
  const [showHistory, setShowHistory] = useState(false);

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
  }, []);  const handleGenerate = async () => {
    setIsGenerating(true);
    setGeneratedResult(null);
    // setShowConfetti(true);

    if (loading) return;

    try {
      let generatedContent = null;

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
      } else if (contentType === 'audio') {
      const payload = {
        story_type: selectedAudioStory === 'custom' ? customAudioStory : selectedAudioStory,
        voice: selectedVoice,
        custom_request: customRequest
      };

      const response = await fetch('http://127.0.0.1:8000/generate_audio_story/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
      } else if (contentType === 'animation') {
      // Validation des données d'animation
      const animationData = {
        style: selectedAnimationStyle,
        theme: selectedAnimationTheme,
        orientation: animationOrientation,
        prompt: animationPrompt,
        title: `Dessin animé ${selectedAnimationTheme}`,
        description: `Animation ${selectedAnimationStyle} sur le thème ${selectedAnimationTheme} (${animationOrientation})`
      };

      const validation = veo3Service.validateAnimationData(animationData);
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
      }        // Optimiser le prompt pour Veo3
        const optimizedPrompt = veo3Service.createOptimizedPrompt(
          selectedAnimationStyle,
          selectedAnimationTheme,
          animationPrompt
        );

        animationData.prompt = optimizedPrompt;
      
      // Générer l'animation avec Veo3 via fal-ai
      try {
        const animationResponse = await veo3Service.generateAnimation(animationData);
        
        // Utiliser directement la réponse du backend
        setAnimationResult({
          id: animationResponse.id,
          title: animationResponse.title || animationData.title,
          description: animationResponse.description || animationData.description,
          videoUrl: animationResponse.video_url,
          thumbnailUrl: animationResponse.thumbnail_url || null,
          style: selectedAnimationStyle,
          theme: selectedAnimationTheme,
          duration: 8,
          status: animationResponse.status || 'completed',
          createdAt: animationResponse.created_at || new Date().toISOString()
        });
        
        setAnimationGenerationStatus({ status: 'completed' });
      } catch (error) {
        console.error('Erreur génération animation:', error);
        // En cas d'erreur (quota épuisé), afficher un message explicite
        setAnimationResult({
          id: `error_${Date.now()}`,
          title: `⚠️ ${animationData.title}`,
          description: `Erreur: ${error.message}`,
          videoUrl: null,
          thumbnailUrl: null,
          style: selectedAnimationStyle,
          theme: selectedAnimationTheme,
          duration: 8,
          status: 'failed',
          error: error.message,
          createdAt: new Date().toISOString()        });
        setAnimationGenerationStatus({ status: 'failed', error: error.message });
      }

      // Pour les animations, on n'utilise pas generatedContent
      generatedContent = null;
    } else if (contentType === 'coloring') {const payload = {
        theme: selectedTheme
      };

      const response = await fetch('http://127.0.0.1:8000/generate_coloring/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);      const coloringData = await response.json();
      
      setColoringResult(coloringData);
      generatedContent = coloringData; // Stocker pour l'historique
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    setGeneratedResult(generatedContent);
    // setStoryPages(splitTextIntoPages(generatedContent.content)); // Ajoute la pagination
    setCurrentPageIndex(0); // Reviens à la première page    // Déterminer le titre
    let title;
    if (contentType === 'rhyme') {
      title = generatedContent.title || `Comptine générée`;
    } else if (contentType === 'audio') {
      title = generatedContent.title || `Conte généré`;
    } else if (contentType === 'animation') {
      title = animationResult?.title || `Dessin animé ${selectedAnimationTheme}`;
    } else if (contentType === 'coloring') {
      title = `Coloriages ${selectedTheme}`;
    }

    // Créer une entrée d'historique pour tous les types sauf les animations
    if (contentType !== 'animation') {
      let newCreation;
        if (contentType === 'coloring') {
        // Pour les coloriages, utiliser les données du coloriage
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent ? `${generatedContent.total_images} coloriage(s) généré(s)` : 'Coloriage généré',
          theme: selectedTheme,
          images: generatedContent?.images || [],
          metadata: generatedContent?.metadata || {}
        };
      } else {
        // Pour les autres types (rhyme, audio)
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent?.content || generatedContent || 'Contenu généré...',
          audio_path: generatedContent?.audio_path || null
        };
      }
      
      // Enregistrer dans l'historique via Supabase
      try {
        await addCreation({
          type: contentType,
          title: title,
          data: newCreation
        });
      } catch (historyError) {
        console.error('Erreur lors de l\'enregistrement dans l\'historique:', historyError);
      }
    }

    // setTimeout(() => setShowConfetti(false), 3000);  } catch (error) {
    console.error('❌ Erreur de génération :', error);
    
    // Afficher une alerte avec plus d'informations
    alert(`❌ Erreur lors de la génération : ${error.message}\n\n💡 Conseil : Vérifiez que les clés API sont configurées dans le fichier .env du serveur.`);
  } finally {
    setIsGenerating(false);
  }
};  const handleSelectCreation = (creation) => {
    // Si c'est une demande pour afficher l'histoire
    if (creation.action === 'showStory') {
      setGeneratedResult({
        title: creation.title,
        content: creation.content || creation.data?.content || '',
        type: creation.type
      });
      setShowStoryPopup(true);
      // On ne ferme PAS l'historique, juste on affiche la popup
    } else if (creation.action === 'showColoring') {
      // Pour les coloriages, on affiche dans la popup de coloriage
      setColoringResult({
        success: true,
        theme: creation.theme || creation.data?.theme || 'coloriage',
        images: creation.images || creation.data?.images || [],
        total_images: (creation.images || creation.data?.images || []).length,
        metadata: creation.metadata || creation.data?.metadata || {}
      });
      setShowColoringPopup(true);
      // On ne ferme PAS l'historique, juste on affiche la popup
    } else {
      // Pour les autres actions, on ferme l'historique
      setShowHistory(false);
      window.location.hash = '';
    }
  };

  const handleCloseHistory = () => {
    setShowHistory(false);
    window.location.hash = '';
  };

  const handleDeleteCreation = (idToDelete) => {
  };  const isFormValid = () => {
    if (contentType === 'rhyme') {
      if (!selectedRhyme) return false;
      if (selectedRhyme === 'custom' && !customRhyme.trim()) return false;
    } else if (contentType === 'audio') {
      if (!selectedAudioStory) return false;
      if (selectedAudioStory === 'custom' && !customAudioStory.trim()) return false;
      // La voix est optionnelle
    } else if (contentType === 'animation') {
      if (!selectedAnimationStyle) return false;
      if (!selectedAnimationTheme) return false;
      if (!animationOrientation) return false;
      if (selectedAnimationTheme === 'custom' && !animationPrompt.trim()) return false;
    } else if (contentType === 'coloring') {
      if (!selectedTheme) return false;
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
      isLoggedIn={!!user}
    />

    <main className="main-content">
      <div className="content-wrapper">
        <motion.div
          className="creation-panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >          <ContentTypeSelector
            contentType={contentType}
            setContentType={setContentType}
          />          <AnimatePresence mode="wait">
            {contentType === 'rhyme' ? (
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
            ) : contentType === 'audio' ? (
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
            ) : contentType === 'animation' ? (
              <motion.div
                key="animation-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >                <AnimationSelector
                  selectedAnimationStyle={selectedAnimationStyle}
                  setSelectedAnimationStyle={setSelectedAnimationStyle}
                  selectedAnimationTheme={selectedAnimationTheme}
                  setSelectedAnimationTheme={setSelectedAnimationTheme}
                  customPrompt={animationPrompt}
                  setCustomPrompt={setAnimationPrompt}
                  duration={animationDuration}
                  setDuration={setAnimationDuration}
                  orientation={animationOrientation}
                  setOrientation={setAnimationOrientation}
                  uploadedAnimationImage={uploadedAnimationImage}
                  setUploadedAnimationImage={setUploadedAnimationImage}
                />              </motion.div>
            ) : contentType === 'coloring' ? (
              <motion.div
                key="coloring-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >                <ColoringSelector
                  selectedTheme={selectedTheme}
                  setSelectedTheme={setSelectedTheme}
                />
              </motion.div>
            ) : null}
          </AnimatePresence><CustomRequest
            customRequest={customRequest}
            setCustomRequest={setCustomRequest}
            stepNumber={contentType === 'animation' ? 5 : contentType === 'coloring' ? 4 : 3}
          />          <GenerateButton
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
              <div className={`preview ${!generatedResult ? 'empty' : ''}`}>
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
      </div>      <p>        {contentType === 'rhyme'
          ? 'Création de la comptine en cours...'
          : contentType === 'audio'
          ? 'Création de l\'histoire en cours...'
          : contentType === 'animation'
          ? animationGenerationStatus?.status === 'processing'
            ? `Génération du dessin animé en cours... (${animationGenerationStatus.estimatedTime} min estimées)`
            : 'Préparation de l\'animation...'
          : contentType === 'coloring'
          ? 'Création de vos coloriages en cours...'
          : 'Génération en cours...'}
      </p></motion.div>
  ) : animationResult && contentType === 'animation' ? (
  <div
    style={{
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem'
    }}
  >
    <div className="animation-preview-container">
      <AnimationViewer animation={animationResult} />
    </div>
    
    <button
      onClick={() => setShowAnimationPopup(true)}
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
      🎬 Voir en grand
    </button>  </div>  ) : coloringResult && contentType === 'coloring' ? (
    <motion.div
      className="generated-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="coloring-result"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem'
      }}
    >
      <button
        onClick={() => setShowColoringPopup(true)}
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
        🎨 Ouvrir le coloriage
      </button>

      <button
        onClick={() => {
          if (coloringResult?.images) {
            const title = selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages';
            downloadColoringAsPDF(coloringResult.images, title);
          }
        }}
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
        📄 Télécharger le coloriage
      </button>
    </motion.div>
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
  />*/}  {!generatedResult?.content && !animationResult && !coloringResult && (
    <div className="empty-preview">    <p>
      {contentType === 'rhyme'
        ? 'Votre comptine apparaîtra ici'
        : contentType === 'audio'
        ? 'Votre histoire apparaîtra ici'
        : contentType === 'animation'
        ? 'Votre dessin animé apparaîtra ici'
        : contentType === 'coloring'
        ? 'Vos coloriages apparaîtront ici'
        : 'Votre création apparaîtra ici'}
    </p>
    </div>
  )}
  {/* 🎵 Audio présent */}
{generatedResult?.audio_path && (
  <div
    style={{
      height: '300px', // 👈 même hauteur que le bloc boutons
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center', // 👈 centre l’audio verticalement aussi
      alignItems: 'center'
    }}
  >
    <audio
      controls
      style={{ width: '100%', maxWidth: '360px' }} // 👈 limite la largeur pour l’esthétique
      src={`http://localhost:8000/${generatedResult.audio_path}`}
      download={generatedResult.audio_path.split('/').pop()}
    />
  </div>
)}

{contentType === 'audio' && generatedResult?.content && (
  <div
    style={{
      height: '300px', // 👈 même hauteur
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem'
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
      📄 Télécharger l'histoire
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
            onClose={handleCloseHistory}
            onSelect={handleSelectCreation}
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
)}    {showColoringPopup && (
      <ColoringPopup
        coloringResult={coloringResult}
        selectedTheme={selectedTheme}
        onClose={() => setShowColoringPopup(false)}
      />
    )}
    {showAnimationPopup && (
      <AnimationPopup 
        animation={animationResult}
        isOpen={showAnimationPopup}
        onClose={() => setShowAnimationPopup(false)}
      />
    )}
  </div>
);
}

export default App;
