import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import { API_ENDPOINTS, API_BASE_URL } from './config/api';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import RhymeSelector from './components/RhymeSelector';
import AudioStorySelector from './components/AudioStorySelector';
import AnimationSelector from './components/AnimationSelector';
import AnimationViewer from './components/AnimationViewer';
import CustomRequest from './components/CustomRequest';
import GenerateButton from './components/GenerateButton';
import History from './components/History';
import StoryPopup from './components/StoryPopup';
import ColoringSelector from './components/ColoringSelector';
import ColoringViewer from './components/ColoringViewer';
import ColoringPopup from './components/ColoringPopup';
import ComicSelector from './components/ComicSelector';
import ComicViewer from './components/ComicViewer';
import ComicPopup from './components/ComicPopup';
import LegalPages from './components/LegalPages';
import CookieBanner from './components/CookieBanner';
import Footer from './components/Footer';
import useSupabaseUser from './hooks/useSupabaseUser_simple';

import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';
import { downloadComicAsPDF } from './utils/pdfUtils';
import { jsPDF } from 'jspdf';

// Fonction utilitaire pour construire l'URL audio complète
const getAudioUrl = (audioPath) => {
  if (!audioPath) return null;
  // Si c'est déjà une URL complète, la retourner
  if (audioPath.startsWith('http')) return audioPath;
  // Sinon, construire l'URL avec le bon port
  return `http://localhost:8006/${audioPath}`;
};

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
      aventure: ['Mon Dessin Animé', 'Animation Magique', 'Film d\'Aventure', 'Cinéma Fantastique'],
      animaux: ['Mes Amis Animés', 'Zoo en Mouvement', 'Aventures Animales', 'Cirque des Animaux'],
      magie: ['Monde Enchanté', 'Magie en Mouvement', 'Film de Fée', 'Animation Magique'],
      espace: ['Voyage Animé', 'Aventure Spatiale', 'Film de l\'Espace', 'Mission Animation'],
      nature: ['Forêt Animée', 'Jardin en Mouvement', 'Nature Vivante', 'Fleurs Dansantes'],
      default: ['Mon Film IA', 'Dessin Animé IA', 'Animation Créative', 'Film Personnalisé']
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
  const [contentType, setContentType] = useState('animation'); // 'rhyme', 'audio', 'coloring', 'animation'
  const [selectedRhyme, setSelectedRhyme] = useState(null);
  const [customRhyme, setCustomRhyme] = useState('');
  
  // Musical rhyme states (nouveau)
  const [generateMusic, setGenerateMusic] = useState(true);
  const [musicStyle, setMusicStyle] = useState(''); // Aucune sélection par défaut
  const [customMusicStyle, setCustomMusicStyle] = useState('');
  
  const [selectedAudioStory, setSelectedAudioStory] = useState(null);
  const [customAudioStory, setCustomAudioStory] = useState('');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [customRequest, setCustomRequest] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  // const [showConfetti, setShowConfetti] = useState(false);
  // États séparés pour chaque type de contenu
  const [audioResult, setAudioResult] = useState(null);
  const [rhymeResult, setRhymeResult] = useState(null);
  
  // État générique pour la compatibilité (sera remplacé par les états spécifiques)
  const [generatedResult, setGeneratedResult] = useState(null);
  const [forceAudioRender, setForceAudioRender] = useState(0);
  
  // État pour la popup d'histoire (depuis l'historique)
  const [storyPopupData, setStoryPopupData] = useState(null);
  const [showFullStory, setShowFullStory] = useState(false);
  const [showStoryPopup, setShowStoryPopup] = useState(false);
  const [showColoringPopup, setShowColoringPopup] = useState(false);
  const [showComicPopup, setShowComicPopup] = useState(false);

  // Coloring states
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [customColoringTheme, setCustomColoringTheme] = useState('');
  const [coloringResult, setColoringResult] = useState(null);
  
  // Comic states
  const [selectedComicTheme, setSelectedComicTheme] = useState(null);
  const [selectedComicArtStyle, setSelectedComicArtStyle] = useState(null);
  const [selectedComicCharacter, setSelectedComicCharacter] = useState(null);
  const [selectedComicStoryLength, setSelectedComicStoryLength] = useState(null);
  const [comicResult, setComicResult] = useState(null);
  const [customCharacter, setCustomCharacter] = useState('');
  const [customComicTheme, setCustomComicTheme] = useState('');
  
  // Animation states
  const [selectedAnimationTheme, setSelectedAnimationTheme] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);
  const [selectedStyle, setSelectedStyle] = useState(null);
  const [customStory, setCustomStory] = useState('');
  const [animationResult, setAnimationResult] = useState(null);
  const [showAnimationViewer, setShowAnimationViewer] = useState(false);

  // Store the current generated title for use in UI
  const [currentTitle, setCurrentTitle] = useState(null);

  // User account state
  const { user, loading } = useSupabaseUser();
  const [showHistory, setShowHistory] = useState(false);

  // Supprimer les erreurs d'extensions de navigateur
  useEffect(() => {
    // Masquer les erreurs des extensions crypto/solana qui polluent la console
    const originalError = console.error;
    console.error = (...args) => {
      // Filtrer les erreurs d'extensions
      const message = args.join(' ');
      if (message.includes('solanaActionsContentScript') || 
          message.includes('extension') ||
          message.includes('chrome-extension')) {
        return; // Ignorer ces erreurs
      }
      originalError.apply(console, args);
    };
    
    return () => {
      console.error = originalError;
    };
  }, []);
  
  // Legal pages state
  const [showLegalPages, setShowLegalPages] = useState(false);
  const [activeLegalSection, setActiveLegalSection] = useState('mentions');

  // Fonction pour obtenir le bon résultat selon le type de contenu
  const getCurrentResult = () => {
    switch (contentType) {
      case 'audio':
        return audioResult;
      case 'rhyme':
        return rhymeResult;
      case 'coloring':
        return coloringResult;
      case 'comic':
        return comicResult;
      case 'animation':
        return animationResult;
      default:
        return null;
    }
  };

  // 📖 Pagination : découpe le texte en pages
  const storyPages = useMemo(() => {
    const currentResult = getCurrentResult();
    if (contentType === 'audio' && currentResult?.content) {
      return splitTextIntoPages(currentResult.content);
    }
    return [];
  }, [contentType, audioResult, coloringResult, comicResult, animationResult, rhymeResult]);
  
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

  // Fonction pour interroger le statut de l'animation
  const pollAnimationStatus = async (animationId, initialData) => {
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes max (5s * 60)
    
    const poll = async () => {
      try {
        const response = await fetch(API_ENDPOINTS.animationStatus(animationId));
        if (!response.ok) throw new Error('Erreur lors de la vérification du statut');
        
        const statusData = await response.json();
        console.log('🔄 Statut animation:', statusData);
        
        // Mettre à jour les données de l'animation
        const updatedData = {
          ...initialData,
          ...statusData,
          // Mapper les champs pour l'AnimationViewer
          total_duration: statusData.duration || initialData.duration || 30,
          clips: statusData.video_clips || statusData.result?.scenes || [],
          scenes: statusData.scenes || statusData.result?.scenes || [],
          generation_time: statusData.generation_time || 0,
          successful_clips: statusData.successful_clips || 0,
          fallback_clips: statusData.fallback_clips || 0,
          // Extraire l'URL finale du vrai serveur
          final_video_url: statusData.result?.final_video_url || statusData.final_video_url
        };
        
        setAnimationResult(updatedData);
        
        // Si complété ou échoué, arrêter le polling
        if (statusData.status === 'completed' || statusData.status === 'failed' || statusData.status === 'error') {
          console.log('🏁 Animation terminée:', statusData.status);
          return;
        }
        
        // Continuer le polling si pas encore fini
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Vérifier toutes les 5 secondes
        } else {
          console.warn('⌛ Timeout du polling d\'animation');
        }
        
      } catch (error) {
        console.error('❌ Erreur lors du polling:', error);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Réessayer en cas d'erreur
        }
      }
    };
    
    // Démarrer le polling après 2 secondes
    setTimeout(poll, 2000);
  };
  
  // Handle Generation
  const handleGenerate = async () => {
    // Réinitialiser les états quand on lance une nouvelle génération
    setAudioResult(null);
    setRhymeResult(null);
    setColoringResult(null);
    setComicResult(null);
    setAnimationResult(null);
    setGeneratedResult(null);
    // Éviter les appels multiples
    if (isGenerating) {
      return;
    }
    
    setIsGenerating(true);
    setGeneratedResult(null);
    // setShowConfetti(true);
    
    // Nettoyer les données temporaires précédentes
    if (window.tempRhymeData) {
      delete window.tempRhymeData;
    }

    try {
      let generatedContent = null;

      if (contentType === 'rhyme') {
        const payload = {
          rhyme_type: selectedRhyme === 'custom' ? customRhyme : selectedRhyme,
          custom_request: customRequest
        };

        console.log('🎵 Envoi payload comptine:', payload);

        const response = await fetch(API_ENDPOINTS.generateRhyme, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        console.log('🎵 Réponse status:', response.status);
        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        generatedContent = await response.json();
        console.log('🎵 Contenu reçu:', generatedContent);
        
        // Si une tâche musicale a été créée, stocker les données et lancer le polling
        if (generatedContent.music_task_id) {
          console.log('🎵 Tâche musicale créée:', generatedContent.music_task_id);
          
          // Stocker temporairement les données de la comptine
          window.tempRhymeData = {
            title: generatedContent.title,
            content: generatedContent.content,
            type: 'rhyme',
            music_status: 'processing'
          };
          
          // Lancer le polling pour suivre la génération musicale
          pollTaskStatus(generatedContent.music_task_id);
          
          // NE PAS définir generatedResult - laisser l'animation de chargement
          generatedContent = null;
          
          // Sortir de la fonction pour éviter le traitement de l'historique avec generatedContent null
          return;
        }
      } else if (contentType === 'audio') {
      const payload = {
        story_type: selectedAudioStory === 'custom' ? customAudioStory : selectedAudioStory,
        voice: selectedVoice,
        custom_request: customRequest
      };
      
      const response = await fetch(API_ENDPOINTS.generateAudioStory, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur HTTP : ${response.status} - ${errorText}`);
      }
      
      generatedContent = await response.json();
    } else if (contentType === 'coloring') {
      const finalTheme = selectedTheme === 'custom' ? customColoringTheme : selectedTheme;
      const payload = {
        theme: finalTheme
      };
      
      const response = await fetch(API_ENDPOINTS.generateColoring, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      
      const coloringData = await response.json();
      
      // Générer un titre pour le coloriage
      const coloringTitle = generateChildFriendlyTitle('coloriage', finalTheme);
      
      // Ajouter le titre aux données
      const coloringDataWithTitle = {
        ...coloringData,
        title: coloringTitle
      };
      
      setColoringResult(coloringDataWithTitle);
      generatedContent = coloringDataWithTitle; // Stocker pour l'historique
    } else if (contentType === 'comic') {
      console.log('🎯 Démarrage génération BD...');
      
      // Construire la liste des personnages selon la sélection
      let characters = [];
      if (selectedComicCharacter && selectedComicCharacter !== 'custom') {
        characters = [selectedComicCharacter];
      }
      
      // Construire la requête personnalisée avec le personnage custom si applicable
      let finalCustomRequest = selectedComicTheme === 'custom' ? customComicTheme : null;
      
      // Ajouter le personnage personnalisé si applicable
      if (selectedComicCharacter === 'custom' && customCharacter) {
        const characterDesc = `Personnage principal: ${customCharacter}`;
        if (finalCustomRequest) {
          finalCustomRequest = `${finalCustomRequest}. ${characterDesc}`;
        } else {
          finalCustomRequest = characterDesc;
        }
      }
      
      // Ajouter les demandes spécifiques si elles sont renseignées (optionnelles)
      if (customRequest && customRequest.trim()) {
        const specificRequests = `Demandes spécifiques: ${customRequest.trim()}`;
        if (finalCustomRequest) {
          finalCustomRequest = `${finalCustomRequest}. ${specificRequests}`;
        } else {
          finalCustomRequest = specificRequests;
        }
      }
      
      const payload = {
        theme: selectedComicTheme === 'custom' ? 'custom' : selectedComicTheme,
        story_length: selectedComicStoryLength, // Utiliser la longueur sélectionnée
        art_style: selectedComicArtStyle,
        characters: characters.length > 0 ? characters : [],
        custom_request: finalCustomRequest,
        setting: null // Peut être ajouté plus tard
      };
      
      console.log('📦 Payload BD corrigé:', payload);
      console.log('🌐 URL API:', API_ENDPOINTS.generateComic);
      
      const response = await fetch(API_ENDPOINTS.generateComic, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      console.log('📡 Réponse reçue:', response.status, response.ok);

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      
      const comicData = await response.json();
      
      console.log('✅ Données BD reçues:', comicData);
      setComicResult(comicData);
      generatedContent = comicData; // Stocker pour l'historique
    } else if (contentType === 'animation') {
      // Déterminer le contenu de l'histoire
      let story;
      if (selectedAnimationTheme && selectedAnimationTheme !== 'custom') {
        // Thème prédéfini - créer une histoire de base
        const themeStories = {
          'magie': 'Une histoire magique avec des créatures fantastiques dans un monde enchanté',
          'aventure': 'Une grande aventure pleine de découvertes et de rebondissements',
          'animaux': 'Une histoire mettant en scène des animaux adorables et leurs aventures',
          'espace': 'Un voyage extraordinaire à travers les étoiles et les planètes',
          'nature': 'Une exploration merveilleuse de la nature et de ses secrets',
          'amitié': 'Une belle histoire d\'amitié et de solidarité',
          'famille': 'Une histoire touchante sur les liens familiaux'
        };
        story = themeStories[selectedAnimationTheme] || `Une belle histoire sur le thème ${selectedAnimationTheme}`;
      } else {
        // Histoire personnalisée
        story = customStory;
      }
      
      // Validation de l'histoire avant envoi
      if (!story || story.trim().length < 10) {
        throw new Error("L'histoire doit contenir au moins 10 caractères");
      }
      
      const payload = {
        theme: selectedAnimationTheme,
        duration: selectedDuration,
        custom_prompt: story  // Utiliser custom_prompt au lieu de story
      };
      
      const response = await fetch(API_ENDPOINTS.generateAnimation, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json; charset=utf-8',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Erreur API Animation:', response.status, errorText);
        throw new Error(`Erreur HTTP ${response.status}: ${errorText}`);
      }
      
      const animationData = await response.json();
      console.log('🎬 Animation démarrée:', animationData);
      
      // Démarrer le suivi du statut de l'animation
      if (animationData.animation_id) {
        pollAnimationStatus(animationData.animation_id, animationData);
      }
      
      setAnimationResult(animationData);
      // Ne pas ouvrir la popup automatiquement, rester sur la page principale
      generatedContent = animationData; // Stocker pour l'historique
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    console.log('🔁 Setting generatedResult:', generatedContent);
    
    // Déterminer le titre AVANT tout traitement
    let title;
    if (contentType === 'rhyme') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      if (generatedContent.title && !generatedContent.title.includes('générée')) {
        title = generatedContent.title + ' 🎵';
      } else {
        title = generateChildFriendlyTitle('comptine', selectedRhyme === 'custom' ? 'default' : selectedRhyme) + ' 🎵';
      }
    } else if (contentType === 'audio') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      if (generatedContent.title && !generatedContent.title.includes('générée')) {
        title = generatedContent.title;
      } else {
        title = generateChildFriendlyTitle('histoire', selectedAudioStory === 'custom' ? 'default' : selectedAudioStory);
      }
    } else if (contentType === 'coloring') {
      // Utiliser le titre généré par l'IA depuis l'API coloriage
      title = generatedContent?.title || generateChildFriendlyTitle('coloriage', selectedTheme);
    } else if (contentType === 'animation') {
      // Utiliser le titre généré par l'IA depuis l'API animation
      title = generatedContent?.title || generateChildFriendlyTitle('animation', selectedAnimationTheme || 'aventure');
    }

    // Stocker le titre pour l'utiliser dans l'UI
    setCurrentTitle(title);
    
    // Pour tous les types de contenu, affichage immédiat
    // Forcer la préservation des propriétés audio
    const resultWithAudio = {
      ...generatedContent,
      audio_path: generatedContent?.audio_path || null,
      audio_url: generatedContent?.audio_url || null,
      audio_generated: generatedContent?.audio_generated || false
    };
    
    // Stocker dans le bon état selon le type de contenu
    switch (contentType) {
      case 'audio':
        setAudioResult(resultWithAudio);
        break;
      case 'rhyme':
        setRhymeResult(resultWithAudio);
        break;
      case 'coloring':
        setColoringResult(resultWithAudio);
        break;
      case 'comic':
        setComicResult(resultWithAudio);
        break;
      case 'animation':
        setAnimationResult(resultWithAudio);
        break;
    }
    
    // Garder l'état générique pour la compatibilité
    setGeneratedResult(resultWithAudio);
    
    // Forcer le re-rendu des composants audio
    if (resultWithAudio?.audio_path || resultWithAudio?.audio_url) {
      setForceAudioRender(prev => prev + 1);
    }
    
    console.log('🔁 ContentType:', contentType);

    // Créer une entrée d'historique
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
      } else if (contentType === 'animation') {
        // Pour les animations, utiliser les données de l'animation
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent ? `Animation de ${generatedContent.actual_duration}s avec ${generatedContent.total_scenes} scènes` : 'Animation générée',
          theme: selectedAnimationTheme,
          clips: generatedContent?.clips || [],
          animation_data: generatedContent || {}
        };
      } else if (contentType === 'comic') {
        // Pour les BD, utiliser les données de la BD
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent ? `BD de ${generatedContent.total_pages} pages en style ${generatedContent.art_style}` : 'BD générée',
          theme: selectedComicTheme,
          pages: generatedContent?.pages || [],
          comic_data: generatedContent || {}
        };
      } else {
        // Pour les autres types (rhyme, audio)
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent?.content || generatedContent || 'Contenu généré...',
          audio_path: generatedContent?.audio_path || null,
          audio_generated: generatedContent?.audio_generated || false
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

    // setTimeout(() => setShowConfetti(false), 3000);
  } catch (error) {
    console.error('❌ Erreur de génération :', error);
    
    // Afficher une alerte avec plus d'informations
    alert(`❌ Erreur lors de la génération : ${error.message}\n\n💡 Conseil : Vérifiez que les clés API sont configurées dans le fichier .env du serveur.`);
    
  } finally {
    // L'état isGenerating pour les comptines sera géré dans pollTaskStatus
    // Pour les autres types de contenu, arrêter l'animation de chargement
    if (contentType !== 'rhyme') {
      setIsGenerating(false);
    }
  }
};

const handleSelectCreation = (creation) => {
    // Si c'est une demande pour afficher l'histoire
    if (creation.action === 'showStory') {
      const storyData = {
        title: creation.title,
        content: creation.content || creation.data?.content || '',
        type: creation.type,
        audio_path: creation.audio_path || creation.data?.audio_path || null,
        audio_url: creation.audio_url || creation.data?.audio_url || null,
        audio_generated: creation.audio_generated || creation.data?.audio_generated || false
      };
      
      // Stocker dans le bon état selon le type
      if (creation.type === 'audio') {
        setAudioResult(storyData);
      } else if (creation.type === 'rhyme') {
        setRhymeResult(storyData);
      }
      
      // Garder l'état générique pour la compatibilité
      setGeneratedResult(storyData);
      // Stocker les données pour la popup
      setStoryPopupData(storyData);
      setShowStoryPopup(true);
      // On ne ferme PAS l'historique, juste on affiche la popup
    } else if (creation.action === 'showColoring') {
      // Pour les coloriages, on affiche dans la popup de coloriage
      const coloringData = {
        success: true,
        theme: creation.theme || creation.data?.theme || 'coloriage',
        images: creation.images || creation.data?.images || [],
        total_images: (creation.images || creation.data?.images || []).length,
        metadata: creation.metadata || creation.data?.metadata || {}
      };
      setColoringResult(coloringData);
      setShowColoringPopup(true);
      // On ne ferme PAS l'historique, juste on affiche la popup
    } else if (creation.action === 'showComic') {
      // Pour les BD, on affiche dans la popup de BD
      const comicData = {
        success: true,
        theme: creation.theme || creation.data?.theme || 'aventure',
        pages: creation.pages || creation.data?.pages || [],
        total_pages: (creation.pages || creation.data?.pages || []).length,
        art_style: creation.data?.art_style || 'cartoon',
        comic_data: creation.data || {}
      };
      setComicResult(comicData);
      setShowComicPopup(true);
    } else if (creation.action === 'showAnimation') {
      // Pour les animations, on affiche dans la popup d'animation
      const animationData = {
        success: true,
        theme: creation.theme || creation.data?.theme || 'aventure',
        clips: creation.clips || creation.data?.clips || [],
        total_scenes: (creation.clips || creation.data?.clips || []).length,
        actual_duration: creation.data?.actual_duration || 5,
        animation_data: creation.data || {}
      };
      setAnimationResult(animationData);
      setShowAnimationViewer(true);
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
  };
  
  // Legal pages handlers
  const handleLegalClick = (section = 'mentions') => {
    setActiveLegalSection(section);
    setShowLegalPages(true);
  };

  const handleCloseLegal = () => {
    setShowLegalPages(false);
  };
  
  const isFormValid = () => {
    if (contentType === 'rhyme') {
      if (!selectedRhyme) return false;
      if (selectedRhyme === 'custom' && !customRhyme.trim()) return false;
    } else if (contentType === 'audio') {
      if (!selectedAudioStory) return false;
      if (selectedAudioStory === 'custom' && !customAudioStory.trim()) return false;
      // La voix est optionnelle
    } else if (contentType === 'coloring') {
      if (!selectedTheme) return false;
      if (selectedTheme === 'custom' && !customColoringTheme.trim()) return false;
    } else if (contentType === 'comic') {
      if (!selectedComicTheme) return false;
      if (selectedComicTheme === 'custom' && !customComicTheme.trim()) return false;
      if (!selectedComicArtStyle) return false;
      if (!selectedComicCharacter) return false;
      if (selectedComicCharacter === 'custom' && !customCharacter.trim()) return false;
      if (!selectedComicStoryLength) return false;
    } else if (contentType === 'animation') {
      // Pour les animations, au minimum un thème doit être sélectionné
      if (!selectedAnimationTheme) return false;
      if (selectedAnimationTheme === 'custom' && !customStory.trim()) return false;
      // Vérifier que l'histoire personnalisée fait au moins 10 caractères
      if (selectedAnimationTheme === 'custom' && customStory.trim().length < 10) return false;
      // Durée, style et mode de génération sont optionnels mais recommandés
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
      // Note: crossOrigin est toujours nécessaire pour les images externes
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

 // Fonction de polling automatique pour vérifier le statut des tâches musicales (sans timeout)
  const pollTaskStatus = async (taskId, interval = 10000) => {
    let attempts = 0;
    
    const checkStatus = async () => {
      try {
        attempts++;
        console.log(`🎵 Polling ${attempts} pour task ${taskId}`);
        const response = await fetch(API_ENDPOINTS.checkTaskStatus(taskId));
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const status = await response.json();
        console.log(`🎵 Statut reçu:`, {
          status: status.status,
          task_status: status.task_status,
          audio_url: status.audio_url,
          audio_path: status.audio_path
        });
        
        if (status.status === 'completed' || status.task_status === 'completed') {
          // Tâche terminée avec succès
          const audioUrl = status.audio_url || status.audio_path;
          if (audioUrl) {
            console.log('🎵✅ Audio prêt!', audioUrl);
            
            // Récupérer les données de comptine stockées temporairement
            const tempData = window.tempRhymeData;
            if (tempData) {
              // Afficher SEULEMENT l'audio pour les comptines (pas les paroles)
              const completeRhyme = {
                title: tempData.title,
                type: 'rhyme',
                audio_url: audioUrl,
                audio_path: audioUrl,
                audio_generated: true,
                music_status: 'completed',
                // Ne PAS inclure 'content' pour forcer l'affichage audio uniquement
              };
              setGeneratedResult(completeRhyme);
              setIsGenerating(false); // Arrêter l'état de génération
              console.log('🎵✅ Comptine audio-only affichée:', completeRhyme);
              console.log('🎵✅ Audio URL:', audioUrl);
            } else {
              // Fallback : mise à jour simple
              setGeneratedResult({
                type: 'rhyme',
                audio_url: audioUrl,
                audio_path: audioUrl,
                audio_generated: true,
                music_status: 'completed',
                title: 'Comptine musicale'
              });
              setIsGenerating(false);
            }
          } else {
            console.warn('⚠️ Tâche terminée mais pas d\'URL audio');
            const tempData = window.tempRhymeData;
            if (tempData) {
              const completeRhyme = {
                ...tempData,
                audio_generated: false,
                music_status: 'completed_no_audio'
              };
              setGeneratedResult(completeRhyme);
              setIsGenerating(false);
              // Ne pas supprimer tempRhymeData pour conserver le titre
            } else {
              setGeneratedResult(prev => ({
                ...prev,
                music_status: 'completed_no_audio'
              }));
              setIsGenerating(false);
            }
          }
          return; // Arrêter le polling
        } else if (status.status === 'failed' || status.task_status === 'failed') {
          // Tâche échouée - ARRÊTER LA GÉNÉRATION AVEC ERREUR
          console.error('❌ Génération musicale échouée:', status);
          const errorMessage = status.error || 'La création de l\'audio a échoué. Veuillez réessayer.';
          
          // Arrêter la génération et afficher l'erreur
          setIsGenerating(false);
          setGeneratedResult(null); // Pas d'affichage de contenu
          
          // Afficher l'erreur à l'utilisateur
          alert(`❌ Erreur : ${errorMessage}`);
          
          console.log('🎵❌ Génération audio échouée, arrêt complet');
          return; // Arrêter le polling
        }
        
        // Continuer le polling sans limite de temps
        setTimeout(checkStatus, interval);
        
      } catch (error) {
        console.error('❌ Erreur lors du polling:', error);
        // En cas d'erreur, on continue quand même le polling
        setTimeout(checkStatus, interval);
      }
    };
    
    await checkStatus();
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
                  customColoringTheme={customColoringTheme}
                  setCustomColoringTheme={setCustomColoringTheme}
                />
              </motion.div>
            ) : contentType === 'comic' ? (
              <motion.div
                key="comic-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <ComicSelector
                  selectedTheme={selectedComicTheme}
                  setSelectedTheme={setSelectedComicTheme}
                  selectedArtStyle={selectedComicArtStyle}
                  setSelectedArtStyle={setSelectedComicArtStyle}
                  selectedCharacter={selectedComicCharacter}
                  setSelectedCharacter={setSelectedComicCharacter}
                  selectedStoryLength={selectedComicStoryLength}
                  setSelectedStoryLength={setSelectedComicStoryLength}
                  customRequest={customRequest}
                  setCustomRequest={setCustomRequest}
                  customCharacter={customCharacter}
                  setCustomCharacter={setCustomCharacter}
                  customComicTheme={customComicTheme}
                  setCustomComicTheme={setCustomComicTheme}
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
              >
                <AnimationSelector
                  selectedTheme={selectedAnimationTheme}
                  setSelectedTheme={setSelectedAnimationTheme}
                  selectedDuration={selectedDuration}
                  setSelectedDuration={setSelectedDuration}
                  selectedStyle={selectedStyle}
                  setSelectedStyle={setSelectedStyle}
                  customStory={customStory}
                  setCustomStory={setCustomStory}
                />
              </motion.div>
            ) : null}
          </AnimatePresence>          <CustomRequest
            customRequest={customRequest}
            setCustomRequest={setCustomRequest}
            stepNumber={contentType === 'coloring' ? 4 : 3}
          />                <GenerateButton 
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
              <div className={`preview ${!getCurrentResult() ? 'empty' : ''}`}>
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
          ? 'Votre comptine est en cours de création…'
          : contentType === 'audio'
          ? 'Création de l\'histoire en cours...'
          : contentType === 'coloring'
          ? 'Création de votre coloriage en cours…'
          : contentType === 'animation'
          ? 'Création de votre dessin animé en cours...'
          : contentType === 'comic'
          ? 'Création de votre bande dessinée en cours...'
          : 'Génération en cours...'}
      </p></motion.div>
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
        className="rhyme-button"
      >
        🎨 Ouvrir le coloriage
      </button>

      <button
        onClick={() => {
          if (coloringResult?.images) {
            // Utiliser le titre du coloriage généré
            const titleForDownload = coloringResult.title || (selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages');
            downloadColoringAsPDF(coloringResult.images, titleForDownload);
          }
        }}
        className="rhyme-button"
      >
        📄 Télécharger le coloriage
      </button>
    </motion.div>
  ) : comicResult && contentType === 'comic' ? (
    <motion.div
      className="generated-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="comic-result"
      style={{
        height: '300px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem'
      }}
    >
      <button
        onClick={() => setShowComicPopup(true)}
        className="rhyme-button"
      >
        📚 Ouvrir la BD
      </button>
      
      <button
        onClick={() => {
          if (comicResult?.pages) {
            // Utiliser le titre généré par l'IA, sinon fallback
            const titleForDownload = comicResult.comic_metadata?.title || comicResult.title || currentTitle || 'ma_bande_dessinee';
            // Créer les URLs complètes pour les images
            const pdfPages = comicResult.pages.map(p => `${API_BASE_URL}${p.image_url || p}`);
            // Nettoyer le titre pour le nom de fichier
            const safeTitle = titleForDownload
              .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
              .toLowerCase().replace(/\s+/g, "_")
              .replace(/[^a-z0-9_]/g, "");
            downloadComicAsPDF(pdfPages, safeTitle);
          }
        }}
        className="rhyme-button"
      >
        📄 Télécharger la BD
      </button>
    </motion.div>
  ) : animationResult && contentType === 'animation' && animationResult.status === 'completed' ? (
    <motion.div
      className="generated-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="animation-result"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem'
      }}
    >
      <div style={{
        textAlign: 'center',
        marginBottom: '1rem'
      }}>
        <h3 style={{ color: '#4c1d95', marginBottom: '0.5rem' }}>🎬 Votre dessin animé est prêt !</h3>
        <p style={{ color: '#666', fontSize: '0.9rem' }}>
          Animation de {animationResult.duration || animationResult.total_duration || 30}s générée avec succès
        </p>
      </div>

      <button
        onClick={() => setShowAnimationViewer(true)}
        className="rhyme-button"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          color: 'white'
        }}
      >
        🎬 Ouvrir le dessin animé
      </button>

      <button
        onClick={() => {
          const videoUrl = animationResult.final_video_url || animationResult.result?.final_video_url;
          if (videoUrl) {
            // Créer un lien temporaire pour télécharger
            const link = document.createElement('a');
            link.href = videoUrl;
            link.download = `animation_${animationResult.theme || 'video'}_${Date.now()}.mp4`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }
        }}
        className="rhyme-button"
        style={{
          background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
          border: 'none',
          color: 'white'
        }}
      >
        💾 Télécharger le dessin animé
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
  />*/}  {!getCurrentResult() && (
    <div className="empty-preview">    <p>
      {contentType === 'rhyme'
        ? 'Votre comptine apparaîtra ici'
        : contentType === 'audio'
        ? 'Votre histoire apparaîtra ici'
        : contentType === 'coloring'
        ? 'Votre coloriage apparaîtra ici'
        : contentType === 'comic'
        ? 'Votre bande dessinée apparaîtra ici'
        : 'Votre dessin animé apparaîtra ici'}
    </p>
    </div>
  )}
  
  {/* 🎵 Affichage des comptines */}
              {contentType === 'rhyme' && getCurrentResult() && (
    <div
      style={{
        minHeight: '300px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1.5rem',
        padding: '2rem',
        backgroundColor: '#f8f9ff',
        borderRadius: '16px',
        border: '2px solid #e0e7ff'
      }}
    >
      {/* Contenu de la comptine */}
      <div style={{
        width: '100%',
        maxWidth: '500px',
        textAlign: 'center',
        lineHeight: '1.8',
        fontSize: '1.1rem',
        color: '#4c1d95',
        fontWeight: '500',
        whiteSpace: 'pre-line'
      }}>
        {/* Affichage UNIQUEMENT si audio disponible */}
                      {(getCurrentResult().audio_path || getCurrentResult().audio_url) ? (
          // Audio uniquement - PAS DE FALLBACK
          <div style={{
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <h3 style={{ color: '#4c1d95', marginBottom: '1rem' }}>
                              🎵 {getCurrentResult().title || 'Votre comptine musicale'}
            </h3>
            <audio
              controls
              style={{ width: '100%', maxWidth: '400px' }}
              src={getAudioUrl(getCurrentResult().audio_path || getCurrentResult().audio_url)}
              download={(getCurrentResult().audio_path || getCurrentResult().audio_url)?.split('/').pop()}
            />
            <p style={{ color: '#6b7280', fontSize: '0.9rem', textAlign: 'center' }}>
              🎶 Votre comptine musicale est prête ! Appuyez sur play pour l'écouter.
            </p>
          </div>
        ) : (
          // Si pas d'audio, afficher message d'erreur
          <div style={{
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem',
            padding: '2rem',
            color: '#dc2626',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#dc2626', marginBottom: '1rem' }}>
              ❌ Erreur de génération
            </h3>
            <p>
              La création de l'audio a échoué. Veuillez réessayer en cliquant sur "Créer ma comptine".
            </p>
          </div>
        )}
      </div>

      {/* Boutons d'action uniquement si audio présent */}
      {(getCurrentResult().audio_path || getCurrentResult().audio_url) && getCurrentResult().audio_generated && (
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          <button
            onClick={() => {
              const audioUrl = getCurrentResult().audio_path || getCurrentResult().audio_url;
              const fileName = audioUrl.split('/').pop() || 'comptine.mp3';
              const a = document.createElement('a');
              a.href = audioUrl;
              a.download = fileName;
              a.click();
            }}
            className="rhyme-button"
          >
            🎵 Télécharger l'audio
          </button>
        </div>
      )}
    </div>
  )}
  
  {/* 🎵 Audio présent pour autres contenus */}

{contentType === 'audio' && getCurrentResult()?.audio_path && getCurrentResult()?.audio_generated && (
  <div
    style={{
      minHeight: '150px',

      display: 'flex',
      flexDirection: 'column',
        justifyContent: 'center', // 👈 centre l’audio verticalement aussi
      alignItems: 'center'
    }}
  >
    <audio
      key={`audio-${getCurrentResult()?.audio_path}`}
      preload="metadata"
      controls
      style={{ width: '80%', minWidth: '320px' }} // 👈 limite la largeur pour l’esthétique
      src={getAudioUrl(getCurrentResult().audio_path || getCurrentResult().audio_url)}
      download={(getCurrentResult().audio_path || getCurrentResult().audio_url)?.split('/').pop()}
    />

  </div>
)}

{contentType === 'audio' && getCurrentResult()?.content && (
  <div
    style={{
      height: '200px', // 👈 hauteur réduite pour remonter les boutons
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem',
      marginBottom: '10%'
    }}
  >
    <button
      onClick={() => setShowStoryPopup(true)}
      className="rhyme-button"
    >
      📖 Ouvrir l'histoire
    </button>

    <button
      onClick={() => downloadPDF(getCurrentResult().title, getCurrentResult().content)}
      className="rhyme-button"
    >
      📄 Télécharger l'histoire
    </button>

    {/* Bouton audio seulement si audio disponible */}
    {(getCurrentResult().audio_path || getCurrentResult().audio_url) && (
    <button
      onClick={async () => {
                 try {
           const audioUrl = getAudioUrl(getCurrentResult().audio_path);
           
           // Utiliser EXACTEMENT la même logique que le PDF
           let finalTitle = getCurrentResult().title || 'Histoire';
           if (getCurrentResult().content && getCurrentResult().content.startsWith("**") && getCurrentResult().content.includes("**", 2)) {
             finalTitle = getCurrentResult().content.split("**")[1].trim();
           }
           
           // Appliquer la même transformation que le PDF
           const safeTitle = finalTitle
             .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
             .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
          
          // Fetch le fichier audio pour forcer le téléchargement
          const response = await fetch(audioUrl);
          const blob = await response.blob();
          
                  // Créer un URL pour le blob (méthode moderne)
        const blobUrl = URL.createObjectURL(blob);
          
          // Créer le lien de téléchargement
          const link = document.createElement('a');
          link.href = blobUrl;
                     link.download = `${safeTitle}.mp3`;
          link.style.display = 'none';
          
          // Ajouter au DOM, cliquer et nettoyer
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
                  // Nettoyer l'URL blob (méthode moderne)
        URL.revokeObjectURL(blobUrl);
        } catch (error) {
          console.error('Erreur lors du téléchargement audio:', error);
          alert('Erreur lors du téléchargement. Veuillez réessayer.');
        }
      }}
      className="rhyme-button"
    >
      🎵 Télécharger l'audio
    </button>
    )}
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

    {/* Footer avec liens légaux */}
    <Footer onLegalClick={handleLegalClick} />

    <AnimatePresence>
      {showHistory && (
        <motion.div
          className="history-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          onClick={handleCloseHistory}
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
                title={storyPopupData?.title || getCurrentResult()?.title || 'Histoire'}
            content={storyPopupData?.content || getCurrentResult()?.content || ''}
    onClose={() => {
      setShowStoryPopup(false);
      setStoryPopupData(null);
    }}
  />
)}

    {showColoringPopup && (
      <ColoringPopup
        coloringResult={coloringResult}
        selectedTheme={selectedTheme}
        customColoringTheme={customColoringTheme}
        onClose={() => setShowColoringPopup(false)}
      />
    )}

    {showComicPopup && (
      <ComicPopup
        comicResult={comicResult}
        selectedComicTheme={selectedComicTheme}
        onClose={() => setShowComicPopup(false)}
      />
    )}

    {showAnimationViewer && (
      <AnimationViewer
        animationResult={animationResult}
        selectedAnimationTheme={selectedAnimationTheme}
        onClose={() => setShowAnimationViewer(false)}
      />
    )}
    
    {/* Legal Pages Modal */}
    <AnimatePresence>
      {showLegalPages && (
        <LegalPages 
          onClose={handleCloseLegal} 
          initialSection={activeLegalSection}
        />
      )}
    </AnimatePresence>
    
    {/* Cookie Banner */}
    <CookieBanner onLegalClick={handleLegalClick} />
  </div>
);
}

export default App;
