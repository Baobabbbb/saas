import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import RhymeSelector from './components/RhymeSelector';
import MusicalRhymeSelector from './components/MusicalRhymeSelector';
import AudioStorySelector from './components/AudioStorySelector';
import StorySelector from './components/StorySelector';
import AnimationSelector from './components/AnimationSelector';
import AnimationViewer from './components/AnimationViewer';
import CustomRequest from './components/CustomRequest';
import GenerateButton from './components/GenerateButton';
import History from './components/History';
import StoryPopup from './components/StoryPopup';
import ColoringSelector from './components/ColoringSelector';
import ColoringViewer from './components/ColoringViewer';
import ColoringPopup from './components/ColoringPopup';

import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';

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
      animaux: ['Aventure Animale', 'Danse des Animaux', 'Copains Animaux', 'Zoo Magique'],
      space: ['Voyage Spatial', 'Étoiles et Planètes', 'Astronaute en Mission', 'Galaxie Magique'],
      fantasy: ['Monde Enchanté', 'Château des Rêves', 'Aventure Magique', 'Pays des Merveilles'],
      default: ['Animation Rigolote', 'Monde Magique', 'Aventure Fantastique', 'Spectacle Animé']
    },
    audio: {
      default: ['Conte Audio', 'Histoire Parlée', 'Aventure Sonore', 'Récit Musical']
    }
  };

  const contentTitles = titlesLibrary[contentType] || titlesLibrary.default;
  const themeTitles = contentTitles[theme] || contentTitles.default;
  return themeTitles[Math.floor(Math.random() * themeTitles.length)];
};

function App() {
  // États de base sans hooks personnalisés pour éviter les erreurs
  const [contentType, setContentType] = useState('comptine');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedRhyme, setSelectedRhyme] = useState('');
  const [selectedMusicalRhyme, setSelectedMusicalRhyme] = useState('');
  const [selectedAudioStory, setSelectedAudioStory] = useState('');
  const [selectedAnimation, setSelectedAnimation] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('Thomas');
  const [customRequest, setCustomRequest] = useState('');
  const [generatedResult, setGeneratedResult] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [showColoringPopup, setShowColoringPopup] = useState(false);
  const [selectedColoring, setSelectedColoring] = useState(null);
  const [currentTitle, setCurrentTitle] = useState(null);

  // Utilisateur simple (sans hook personnalisé)
  const user = null; // Temporairement désactivé pour éviter les erreurs
  const [showHistory, setShowHistory] = useState(false);

  // 📖 Pagination : découpe le texte en pages
  const storyPages = React.useMemo(() => {
    if (contentType === 'audio' && generatedResult?.content) {
      return splitTextIntoPages(generatedResult.content);
    }
    return [];
  }, [generatedResult, contentType]);

  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  // Fonction pour diviser le texte en pages
  function splitTextIntoPages(text, wordsPerPage = 50) {
    if (!text) return [];
    const words = text.split(' ');
    const pages = [];
    for (let i = 0; i < words.length; i += wordsPerPage) {
      pages.push(words.slice(i, i + wordsPerPage).join(' '));
    }
    return pages;
  }

  // Fonction de génération principale
  const handleGenerate = async () => {
    if (!selectedTheme) {
      alert('Veuillez sélectionner un thème');
      return;
    }

    setIsGenerating(true);
    setGeneratedResult(null);
    setShowPopup(false);
    setShowColoringPopup(false);

    try {
      let generatedContent = null;
      let contentTitle = generateChildFriendlyTitle(contentType, selectedTheme);

      if (contentType === 'comptine') {
        const payload = {
          theme: selectedTheme,
          style: selectedRhyme,
          musical_style: selectedMusicalRhyme,
          custom_request: customRequest
        };

        const response = await fetch('http://localhost:8006/generate_rhyme/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
      } else if (contentType === 'histoire') {
        const payload = {
          theme: selectedTheme,
          custom_request: customRequest
        };

        const response = await fetch('http://localhost:8006/generate_story/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
      } else if (contentType === 'coloring') {
        const payload = {
          theme: selectedTheme,
          custom_request: customRequest
        };

        const response = await fetch('http://localhost:8006/generate_coloring/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
      } else if (contentType === 'animation') {
        const payload = {
          theme: selectedTheme,
          custom_request: customRequest
        };

        const response = await fetch('http://localhost:8006/generate_animation/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
      }

      if (generatedContent) {
        setGeneratedResult(generatedContent);
        setCurrentTitle(contentTitle);

        // Sauvegarder dans l'historique
        if (contentType !== 'coloring') {
          await addCreation({
            type: contentType,
            theme: selectedTheme,
            content: generatedContent.content || generatedContent,
            title: contentTitle
          });
        }

        if (contentType === 'coloring') {
          setSelectedColoring(generatedContent);
          setShowColoringPopup(true);
        } else {
          setShowPopup(true);
        }
      }

    } catch (error) {
      console.error('Erreur lors de la génération:', error);
      alert('Erreur lors de la génération. Vérifiez que le serveur backend est démarré.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="App">
      <Header isLoggedIn={!!user} />

      <AnimatePresence mode="wait">
        <motion.div
          key={contentType}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          className="app-content"
        >
          <ContentTypeSelector
            contentType={contentType}
            setContentType={setContentType}
          />

          {contentType === 'comptine' && (
            <RhymeSelector
              selectedRhyme={selectedRhyme}
              setSelectedRhyme={setSelectedRhyme}
              selectedMusicalRhyme={selectedMusicalRhyme}
              setSelectedMusicalRhyme={setSelectedMusicalRhyme}
              selectedTheme={selectedTheme}
              setSelectedTheme={setSelectedTheme}
              customRequest={customRequest}
              setCustomRequest={setCustomRequest}
            />
          )}

          {contentType === 'histoire' && (
            <StorySelector
              selectedTheme={selectedTheme}
              setSelectedTheme={setSelectedTheme}
              customRequest={customRequest}
              setCustomRequest={setCustomRequest}
            />
          )}

          {contentType === 'coloring' && (
            <ColoringSelector
              selectedTheme={selectedTheme}
              setSelectedTheme={setSelectedTheme}
              customRequest={customRequest}
              setCustomRequest={setCustomRequest}
            />
          )}

          {contentType === 'animation' && (
            <AnimationSelector
              selectedTheme={selectedTheme}
              setSelectedTheme={setSelectedTheme}
              customRequest={customRequest}
              setCustomRequest={setCustomRequest}
            />
          )}

          {contentType === 'audio' && (
            <AudioStorySelector
              selectedAudioStory={selectedAudioStory}
              setSelectedAudioStory={setSelectedAudioStory}
              selectedVoice={selectedVoice}
              setSelectedVoice={setSelectedVoice}
              customRequest={customRequest}
              setCustomRequest={setCustomRequest}
            />
          )}

          <GenerateButton
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            contentType={contentType}
          />

          <History
            showHistory={showHistory}
            setShowHistory={setShowHistory}
            user={user}
          />
        </motion.div>
      </AnimatePresence>

      {generatedResult && contentType !== 'coloring' && (
        <StoryPopup
          content={generatedResult}
          contentType={contentType}
          title={currentTitle}
          showPopup={showPopup}
          setShowPopup={setShowPopup}
          storyPages={storyPages}
          currentPageIndex={currentPageIndex}
          setCurrentPageIndex={setCurrentPageIndex}
        />
      )}

      {selectedColoring && (
        <ColoringPopup
          coloring={selectedColoring}
          showPopup={showColoringPopup}
          setShowPopup={setShowColoringPopup}
        />
      )}
    </div>
  );
}

export default App;
