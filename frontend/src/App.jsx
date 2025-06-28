import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import RhymeSelector from './components/RhymeSelector';
import AudioStorySelector from './components/AudioStorySelector';
import AnimationGenerator from './components/AnimationGenerator';
import CustomRequest from './components/CustomRequest';
import GenerateButton from './components/GenerateButton';
import History from './components/History';
import StoryPopup from './components/StoryPopup';
import ColoringSelector from './components/ColoringSelector';
import ColoringViewer from './components/ColoringViewer';
import ColoringPopup from './components/ColoringPopup';
import useSupabaseUser from './hooks/useSupabaseUser';

import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';
import { generateCompleteAnimation } from './services/animation';

// Fonction pour générer des titres attractifs pour les enfants
const generateChildFriendlyTitle = (contentType, theme, content = '') => {
  const titlesLibrary = {
    comptine: {
      animaux: ['Les Amis de la Forêt', 'La Danse des Animaux', 'Mes Amis les Animaux', 'Le Grand Bal des Animaux'],
      nature: ['Les Fleurs Magiques', 'L\'Aventure dans les Bois', 'Les Secrets du Jardin', 'La Fête de la Nature'],
      transport: ['Le Train des Copains', 'L\'Aventure en Voiture', 'Le Voyage Fantastique', 'En Route pour l\'Aventure'],
      couleurs: ['L\'Arc-en-Ciel Magique', 'Le Monde des Couleurs', 'La Danse des Couleurs', 'Mon Joli Tableau'],
      famille: ['Ma Famille d\'Amour', 'Tous Ensemble', 'Les Câlins de Famille', 'Mon Coeur de Famille'],
      default: ['Ma Jolie Comptine', 'Chanson du Bonheur', 'Ma Petite Mélodie', 'Comptine Rigolote']
    },
    histoire: {
      aventure: ['La Grande Aventure', 'Voyage Extraordinaire', 'Mission Secrète', 'L\'Aventure Fantastique'],
      animaux: ['Les Amis de la Forêt', 'L\'Histoire des Petits Animaux', 'Mes Copains Animaux', 'La Famille Animaux'],
      magie: ['Le Monde Magique', 'L\'Aventure Enchantée', 'Le Secret Magique', 'La Fée et ses Amis'],
      amitié: ['Les Meilleurs Amis', 'Une Belle Amitié', 'Copains pour la Vie', 'L\'Amitié Magique'],
      espace: ['Voyage dans les Étoiles', 'L\'Aventure Spatiale', 'Les Amis de l\'Espace', 'Mission sur la Lune'],
      default: ['Mon Belle Histoire', 'Conte Merveilleux', 'Histoire Fantastique', 'Récit d\'Aventure']
    },
    coloriage: {
      animaux: ['Mes Amis Animaux', 'Zoo Rigolo', 'Famille Animaux', 'Copains de la Forêt'],
      licorne: ['Licorne Magique', 'Princesse Licorne', 'Pays des Licornes', 'Licorne Arc-en-Ciel'],
      dinosaures: ['Dino Rigolo', 'Mes Amis Dinosaures', 'Parc des Dinosaures', 'T-Rex et ses Copains'],
      nature: ['Jardin Fleuri', 'Forêt Enchantée', 'Promenade Nature', 'Fleurs et Papillons'],
      espace: ['Voyage Spatial', 'Planètes Rigolotes', 'Astronaute en Mission', 'Étoiles et Fusées'],
      véhicules: ['Mes Voitures', 'Garage Rigolo', 'Course Automobile', 'Train et Avions'],
      default: ['Mon Coloriage', 'Dessin Rigolo', 'Art Créatif', 'Belle Image']
    },
    animation: {
      aventure: ['Super Aventure', 'Mission Héroïque', 'Voyage Fantastique', 'Grande Expédition'],
      magie: ['Monde Magique', 'Sort Enchanteur', 'Fée et Magie', 'Château Magique'],
      animaux: ['Amis Animaux', 'Safari Rigolo', 'Zoo Animé', 'Copains de la Jungle'],
      espace: ['Mission Spatiale', 'Voyage Galactique', 'Planète Mystère', 'Astronaute Héros'],
      default: ['Mon Dessin Animé', 'Film Rigolo', 'Animation Magique', 'Spectacle Animé']
    }
  };

  const categoryTitles = titlesLibrary[contentType] || titlesLibrary.histoire;
  const themeTitles = categoryTitles[theme] || categoryTitles.default || categoryTitles.aventure;
  
  // Choisir un titre au hasard dans la liste
  const randomIndex = Math.floor(Math.random() * themeTitles.length);
  return themeTitles[randomIndex];
};

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
  const [contentType, setContentType] = useState('animation'); // 'rhyme', 'audio', 'animation' or 'coloring'
  const [selectedRhyme, setSelectedRhyme] = useState(null);
  const [customRhyme, setCustomRhyme] = useState('');
  const [selectedAudioStory, setSelectedAudioStory] = useState(null);
  const [customAudioStory, setCustomAudioStory] = useState('');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [customRequest, setCustomRequest] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  // const [showConfetti, setShowConfetti] = useState(false);
  const [generatedResult, setGeneratedResult] = useState(null);
  const [showFullStory, setShowFullStory] = useState(false);
  const [showStoryPopup, setShowStoryPopup] = useState(false);
  const [showColoringPopup, setShowColoringPopup] = useState(false);

  // Animation states (nouvelle méthode)
  const [animationResult, setAnimationResult] = useState(null);
  const [showAnimationPopup, setShowAnimationPopup] = useState(false);
  const [animationSelections, setAnimationSelections] = useState({ style: '', theme: '', duration: '' });
  
  // Coloring states
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [coloringResult, setColoringResult] = useState(null);
  
  // Store the current generated title for use in UI
  const [currentTitle, setCurrentTitle] = useState(null);

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
      setShowHistory(window.location.hash === '#historique');    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);
  
  // Handle Animation Generation
  const handleAnimationGenerate = async (generationData) => {
    setAnimationResult(null);
    
    try {
      console.log('🎬 Démarrage génération animation:', generationData);
      
      const animationData = await generateCompleteAnimation(generationData);
      console.log('✅ Réponse animation reçue:', animationData);
      
      if (animationData.status === 'success') {
        // Construire l'URL complète de la vidéo
        const fullVideoUrl = animationData.video_url.startsWith('http') 
          ? animationData.video_url 
          : `http://127.0.0.1:8000${animationData.video_url}`;
        
        console.log('🎥 DEBUG - URL originale:', animationData.video_url);
        console.log('🎥 DEBUG - URL complète:', fullVideoUrl);
        
        setAnimationResult({
          id: `animation_${Date.now()}`,
          title: generationData.title || 'Animation IA',
          description: `Animation narrative générée par IA (${animationData.scenes_count} scènes)`,
          videoUrl: fullVideoUrl,
          videoPath: animationData.video_path,
          scenesCount: animationData.scenes_count,
          totalDuration: animationData.total_duration,
          generationTime: animationData.generation_time,
          scenesDetails: animationData.scenes_details || [],
          pipelineType: 'complete_animation',
          status: 'completed',
          createdAt: new Date().toISOString(),
          story: generationData.story,
          stylePreferences: generationData.style_preferences
        });
        
        // Afficher la popup de résultat
        setShowAnimationPopup(true);
        
        // Sauvegarder dans l'historique
        try {
          await addCreation({
            type: 'animation',
            title: generationData.title || 'Animation IA',
            data: {
              ...animationData,
              story: generationData.story,
              stylePreferences: generationData.style_preferences
            }
          });
        } catch (historyError) {
          console.error('Erreur historique animation:', historyError);
        }
        
      } else {
        throw new Error(animationData.error || 'Erreur génération animation');
      }
      
    } catch (error) {
      console.error('❌ Erreur génération animation:', error);
      
      // Afficher un résultat d'erreur
      setAnimationResult({
        id: `animation_error_${Date.now()}`,
        title: '⚠️ Erreur Animation IA',
        description: `Erreur: ${error.message}`,
        videoUrl: null,
        status: 'failed',
        error: error.message,
        createdAt: new Date().toISOString()
      });
      
      setShowAnimationPopup(true);
      
      alert(`❌ Erreur génération animation : ${error.message}\n\n💡 Vérifiez que le service d'animation est démarré et configuré.`);
    }
  };

  const handleGenerate = async () => {
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
      };      const response = await fetch('http://127.0.0.1:8000/generate_audio_story/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
    } else if (contentType === 'animation') {
      // Créer les données de génération à partir des sélections
      const defaultStory = "Il était une fois un petit héros qui part dans une grande aventure pleine de surprises et d'amitié. Dans un monde magique rempli de couleurs et de merveilles, notre personnage découvre des lieux fantastiques et rencontre des amis extraordinaires qui l'aideront à grandir et à apprendre de belles leçons.";
      
      const themeNames = {
        'adventure': 'Aventure',
        'magic': 'Magie',
        'animals': 'Animaux',
        'friendship': 'Amitié',
        'space': 'Espace',
        'educational': 'Éducatif'
      };
      
      const styleNames = {
        'cartoon': 'Cartoon',
        'watercolor': 'Aquarelle',
        'anime': 'Anime',
        'fairy_tale': 'Conte'
      };
      
      const themeName = themeNames[animationSelections.theme] || 'Aventure';
      const styleName = styleNames[animationSelections.style] || 'Cartoon';
      const autoTitle = `${themeName} en ${styleName}`;
      
      // Utiliser l'histoire par défaut ou la demande spécifique
      const storyToUse = customRequest.trim() || 
        "Il était une fois un petit héros qui part dans une grande aventure pleine de surprises et d'amitié. Dans un monde magique rempli de couleurs et de merveilles, notre personnage découvre des lieux fantastiques et rencontre des amis extraordinaires qui l'aideront à grandir et à apprendre de belles leçons.";
      
      // Convertir la durée sélectionnée en nombre (durée totale)
      const selectedDurationNum = parseInt(animationSelections.duration) || 30;
      
      const generationData = {
        story: storyToUse,
        style: animationSelections.style,
        theme: animationSelections.theme,
        duration: selectedDurationNum,
        title: autoTitle,
        style_preferences: {
          visual_style: animationSelections.style,
          theme: animationSelections.theme,
          color_palette: 'vibrant',
          target_audience: 'children'
        },
        duration_preferences: {
          total_duration: selectedDurationNum,
          scene_duration: Math.min(5, Math.max(2, selectedDurationNum / 6)), // Durée par scène adaptée
          total_max_duration: selectedDurationNum
        }
      };

      // Appeler la fonction de génération animation
      await handleAnimationGenerate(generationData);
      generatedContent = null; // Géré séparément
    } else if (contentType === 'coloring') {
      const payload = {
        theme: selectedTheme
      };
      
      const response = await fetch('http://127.0.0.1:8000/generate_coloring/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      
      const coloringData = await response.json();
      
      setColoringResult(coloringData);
      generatedContent = coloringData; // Stocker pour l'historique
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    setGeneratedResult(generatedContent);
    // setStoryPages(splitTextIntoPages(generatedContent.content)); // Ajoute la pagination
    setCurrentPageIndex(0); // Reviens à la première page    // Déterminer le titre avec des noms attractifs pour les enfants
    let title;
    if (contentType === 'rhyme') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      if (generatedContent.title && !generatedContent.title.includes('générée')) {
        title = generatedContent.title;
      } else {
        title = generateChildFriendlyTitle('comptine', selectedRhyme === 'custom' ? 'default' : selectedRhyme);
      }
    } else if (contentType === 'audio') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      if (generatedContent.title && !generatedContent.title.includes('générée')) {
        title = generatedContent.title;
      } else {
        title = generateChildFriendlyTitle('histoire', selectedAudioStory === 'custom' ? 'default' : selectedAudioStory);
      }    } else if (contentType === 'animation') {
      // Utiliser le titre généré par l'IA depuis l'API animation
      title = animationResult?.title || generateChildFriendlyTitle('animation', 'animation');
    } else if (contentType === 'coloring') {
      // Utiliser le titre généré par l'IA depuis l'API coloriage
      title = generatedContent?.title || generateChildFriendlyTitle('coloriage', selectedTheme);
    }

    // Stocker le titre pour l'utiliser dans l'UI
    setCurrentTitle(title);

    // Créer une entrée d'historique pour tous les types sauf les animations IA
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
          data: newCreation        });
      } catch (historyError) {
        console.error('Erreur lors de l\'enregistrement dans l\'historique:', historyError);
      }
    }

    // setTimeout(() => setShowConfetti(false), 3000);
  } catch (error) {
    console.error('❌ Erreur de génération :', error);
    
    // Afficher une alerte avec plus d'informations
    alert(`❌ Erreur lors de la génération : ${error.message}\n\n💡 Conseil : Vérifiez que les clés API sont configurées dans le fichier .env du serveur.`);  } finally {
    setIsGenerating(false);
  }
};

const handleSelectCreation = (creation) => {
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
      // Vérifier que les sélections de style, thème ET durée sont faites
      return animationSelections.style && animationSelections.theme && animationSelections.duration;
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
                key="animation-generator"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <AnimationGenerator
                  onSelectionChange={setAnimationSelections}
                />
              </motion.div>
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
          </AnimatePresence>          <CustomRequest
            customRequest={customRequest}
            setCustomRequest={setCustomRequest}
            stepNumber={contentType === 'animation' ? 4 : contentType === 'coloring' ? 4 : 3}
          /><GenerateButton
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
          ? 'Pipeline IA au travail... Analyse narrative et génération multi-scènes...'
          : contentType === 'coloring'
          ? 'Création de vos coloriages en cours...'
          : 'Génération en cours...'}
      </p></motion.div>
  ) : animationResult && contentType === 'animation' ? (
    <motion.div
      className="animation-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="animation-result"
      style={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem',
        padding: '1rem'
      }}
    >
      <div className="animation-info" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '1rem',
        borderRadius: '12px',
        textAlign: 'center',
        width: '100%'
      }}>
        <h3 style={{ margin: '0 0 0.5rem 0' }}>🎬 {animationResult.title}</h3>
        <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>{animationResult.description}</p>
        {animationResult.status === 'completed' && (
          <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>
            📊 {animationResult.scenesCount} scènes • ⏱️ {animationResult.totalDuration}s • 🤖 {animationResult.generationTime}s
          </div>
        )}
      </div>
      
      {animationResult.videoUrl ? (
        <div className="animation-video-preview" style={{ width: '100%', maxWidth: '400px' }}>
          <video 
            controls 
            style={{ width: '100%', borderRadius: '8px' }}
            poster="/placeholder-video.png"
          >
            <source src={animationResult.videoUrl} type="video/mp4" />
            Votre navigateur ne supporte pas la vidéo.
          </video>
        </div>
      ) : animationResult.status === 'failed' ? (
        <div style={{
          background: '#fed7d7',
          color: '#c53030',
          padding: '1rem',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          ⚠️ {animationResult.error || 'Erreur de génération'}
        </div>
      ) : (
        <div style={{
          background: '#bee3f8',
          color: '#2c5282',
          padding: '1rem',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          🎭 Animation en cours de génération...
        </div>
      )}
      
      <button
        onClick={() => setShowAnimationPopup(true)}
        style={{
          padding: '0.8rem 1.6rem',
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: '25px',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '1rem'
        }}
      >
        🎬 Voir les détails
      </button>
    </motion.div>
  ) : coloringResult && contentType === 'coloring' ? (
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
      </button>      <button
        onClick={() => {
          if (coloringResult?.images) {
            // Utiliser le titre généré par l'IA, sinon fallback sur le thème
            const titleForDownload = currentTitle || (selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages');
            downloadColoringAsPDF(coloringResult.images, titleForDownload);
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
      <motion.div
        className="animation-popup-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={() => setShowAnimationPopup(false)}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}
      >
        <motion.div
          className="animation-popup"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'white',
            borderRadius: '20px',
            padding: '30px',
            maxWidth: '90vw',
            maxHeight: '90vh',
            overflow: 'auto',
            position: 'relative'
          }}
        >
          <button
            onClick={() => setShowAnimationPopup(false)}
            style={{
              position: 'absolute',
              top: '15px',
              right: '15px',
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ×
          </button>
          
          <div className="animation-popup-content">
            {animationResult && (
              <>
                <h2 style={{ marginBottom: '20px', color: '#2d3748' }}>
                  🎬 {animationResult.title}
                </h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <p style={{ color: '#718096', marginBottom: '10px' }}>
                    {animationResult.description}
                  </p>
                  
                  {animationResult.status === 'completed' && (
                    <div style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      padding: '15px',
                      borderRadius: '12px',
                      marginBottom: '20px'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', fontSize: '0.9rem' }}>
                        <div>📊 <strong>{animationResult.scenesCount}</strong> scènes</div>
                        <div>⏱️ <strong>{animationResult.totalDuration}s</strong> durée</div>
                        <div>🤖 <strong>{animationResult.generationTime}s</strong> génération</div>
                        <div>🎭 <strong>Pipeline IA</strong> complète</div>
                      </div>
                    </div>
                  )}
                </div>
                
                {animationResult.videoUrl ? (
                  <div style={{ marginBottom: '20px' }}>
                    <video 
                      controls 
                      style={{ 
                        width: '100%', 
                        maxWidth: '600px', 
                        borderRadius: '12px',
                        boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)'
                      }}
                    >
                      <source src={animationResult.videoUrl} type="video/mp4" />
                      Votre navigateur ne supporte pas la vidéo.
                    </video>
                  </div>
                ) : animationResult.status === 'failed' ? (
                  <div style={{
                    background: '#fed7d7',
                    color: '#c53030',
                    padding: '20px',
                    borderRadius: '12px',
                    marginBottom: '20px',
                    textAlign: 'center'
                  }}>
                    <h3>Erreur de génération</h3>
                    <p>{animationResult.error}</p>
                  </div>
                ) : null}
                
                {animationResult.scenesDetails && animationResult.scenesDetails.length > 0 && (
                  <div style={{ marginBottom: '20px' }}>
                    <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>🎭 Détails des scènes</h3>
                    <div style={{ display: 'grid', gap: '10px' }}>
                      {animationResult.scenesDetails.map((scene, index) => (
                        <div key={index} style={{
                          background: '#f7fafc',
                          padding: '12px',
                          borderRadius: '8px',
                          borderLeft: '4px solid #667eea'
                        }}>
                          <div style={{ fontWeight: '600', marginBottom: '5px' }}>
                            Scène {scene.scene_number || (index + 1)} ({scene.duration || '3'}s)
                          </div>
                          <div style={{ fontSize: '0.9rem', color: '#4a5568' }}>
                            {scene.description}
                          </div>
                          {scene.action && (
                            <div style={{ fontSize: '0.8rem', color: '#718096', marginTop: '5px' }}>
                              Action: {scene.action}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {animationResult.story && (
                  <div style={{ marginBottom: '20px' }}>
                    <h3 style={{ marginBottom: '10px', color: '#2d3748' }}>📖 Histoire originale</h3>
                    <div style={{
                      background: '#f0fff4',
                      padding: '15px',
                      borderRadius: '8px',
                      fontStyle: 'italic',
                      color: '#2d3748',
                      lineHeight: '1.6'
                    }}>
                      {animationResult.story}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    )}
  </div>
);
}

export default App;
