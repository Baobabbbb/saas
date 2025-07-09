import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
import { API_ENDPOINTS, API_BASE_URL } from './config/api';
import Header from './components/Header';
import ContentTypeSelector from './components/ContentTypeSelector';
import RhymeSelector from './components/RhymeSelector';
import MusicalRhymeSelector from './components/MusicalRhymeSelector';
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
import SeedanceSelector from './components/SeedanceSelector';
import SeedanceViewer from './components/SeedanceViewer';
import LegalPages from './components/LegalPages';
import CookieBanner from './components/CookieBanner';
import Footer from './components/Footer';
import useSupabaseUser from './hooks/useSupabaseUser';

import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';
import { downloadComicAsPDF } from './utils/pdfUtils';

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
  const [generatedResult, setGeneratedResult] = useState(null);
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

  // SEEDANCE states
  const [selectedSeedanceTheme, setSelectedSeedanceTheme] = useState(null);
  const [selectedSeedanceDuration, setSelectedSeedanceDuration] = useState(null);
  const [selectedSeedanceAgeTarget, setSelectedSeedanceAgeTarget] = useState(null);
  const [customSeedanceStory, setCustomSeedanceStory] = useState('');
  const [seedanceResult, setSeedanceResult] = useState(null);
  const [showSeedanceViewer, setShowSeedanceViewer] = useState(false);

  // Store the current generated title for use in UI
  const [currentTitle, setCurrentTitle] = useState(null);

  // User account state
  const { user, loading } = useSupabaseUser();
  const [showHistory, setShowHistory] = useState(false);
  
  // Legal pages state
  const [showLegalPages, setShowLegalPages] = useState(false);
  const [activeLegalSection, setActiveLegalSection] = useState('mentions');

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
  
  // Handle Generation
  const handleGenerate = async () => {
    console.log('🚀 Fonction handleGenerate appelée, contentType:', contentType);
    setIsGenerating(true);
    setGeneratedResult(null);
    // setShowConfetti(true);
    
    // Nettoyer les données temporaires précédentes
    if (window.tempRhymeData) {
      delete window.tempRhymeData;
    }

    if (loading) return;

    try {
      let generatedContent = null;
      console.log('📋 Début de génération pour type:', contentType);

      if (contentType === 'rhyme') {
        const payload = {
          rhyme_type: selectedRhyme === 'custom' ? customRhyme : selectedRhyme,
          custom_request: customRequest,
          generate_music: true, // Always generate music for rhymes
          custom_style: musicStyle === 'custom' ? customMusicStyle : null,
          language: 'fr'
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
      } else if (contentType === 'audio') {
      const payload = {
        story_type: selectedAudioStory === 'custom' ? customAudioStory : selectedAudioStory,
        voice: selectedVoice,
        custom_request: customRequest
      };      const response = await fetch(API_ENDPOINTS.generateAudioStory, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
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
      
      setColoringResult(coloringData);
      generatedContent = coloringData; // Stocker pour l'historique
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
        story: story,
        duration: selectedDuration,
        style: selectedStyle,
        theme: selectedAnimationTheme,
        mode: 'production'  // Toujours en mode production
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
      
      setAnimationResult(animationData);
      setShowAnimationViewer(true); // Afficher immédiatement le viewer
      generatedContent = animationData; // Stocker pour l'historique
    } else if (contentType === 'seedance') {
      // Génération SEEDANCE avec l'API dédiée
      const payload = {
        story: customSeedanceStory,
        theme: selectedSeedanceTheme,
        age_target: selectedSeedanceAgeTarget,
        duration: selectedSeedanceDuration
      };
      
      console.log('🚀 Payload SEEDANCE:', payload);
      
      const response = await fetch(`${API_BASE_URL}/api/seedance/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json; charset=utf-8',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Erreur API SEEDANCE:', response.status, errorText);
        throw new Error(`Erreur HTTP ${response.status}: ${errorText}`);
      }
      
      const seedanceData = await response.json();
      
      setSeedanceResult(seedanceData);
      setShowSeedanceViewer(true); // Afficher immédiatement le viewer
      generatedContent = seedanceData; // Stocker pour l'historique
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    console.log('🔁 Setting generatedResult:', generatedContent);
    
    // Déterminer le titre AVANT tout traitement
    let title;
    if (contentType === 'rhyme') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      if (generatedContent.title && !generatedContent.title.includes('générée')) {
        title = generatedContent.title + (generatedContent.has_music ? ' 🎵' : '');
      } else {
        title = generateChildFriendlyTitle('comptine', selectedRhyme === 'custom' ? 'default' : selectedRhyme) + (generatedContent.has_music ? ' 🎵' : '');
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
    } else if (contentType === 'seedance') {
      // Utiliser le titre généré par l'IA depuis l'API SEEDANCE
      title = generatedContent?.title || `Animation SEEDANCE ${selectedSeedanceTheme || 'éducative'}`;
    }

    // Stocker le titre pour l'utiliser dans l'UI
    setCurrentTitle(title);
    
    // 🎵 Pour les comptines musicales, ne pas afficher le résultat tout de suite
    if (contentType === 'rhyme' && generatedContent.task_id && generateMusic) {
      console.log('🎵 Comptine musicale en cours - attente de la musique avant affichage');
      console.log('🎵 Démarrage du polling automatique pour task_id:', generatedContent.task_id);
      // Stocker temporairement les données avec le titre calculé pour le polling
      window.tempRhymeData = {
        ...generatedContent,
        title: title // S'assurer que le titre formaté est inclus
      };
      pollTaskStatus(generatedContent.task_id);
      // NE PAS setGeneratedResult maintenant - ce sera fait dans le polling
    } else {
      // Pour les autres types de contenu, affichage immédiat
      setGeneratedResult(generatedContent);
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
      } else if (contentType === 'seedance') {
        // Pour les animations SEEDANCE, utiliser les données de l'animation
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent ? `Animation SEEDANCE de ${generatedContent.total_duration}s avec ${generatedContent.scenes_count} scènes` : 'Animation SEEDANCE générée',
          theme: selectedSeedanceTheme,
          scenes: generatedContent?.scenes || [],
          seedance_data: generatedContent || {}
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

    // setTimeout(() => setShowConfetti(false), 3000);
  } catch (error) {
    console.error('❌ Erreur de génération :', error);
    
    // Afficher une alerte avec plus d'informations
    alert(`❌ Erreur lors de la génération : ${error.message}\n\n💡 Conseil : Vérifiez que les clés API sont configurées dans le fichier .env du serveur.`);
    
    // Pour les comptines musicales, arrêter l'animation même en cas d'erreur
    if (contentType === 'rhyme' && generateMusic) {
      setIsGenerating(false);
    }
  } finally {
    // Ne pas arrêter l'animation pour les comptines musicales qui continuent en polling
    if (!(contentType === 'rhyme' && generateMusic)) {
      setIsGenerating(false);
    }
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
    console.log('🔍 Validation du formulaire pour contentType:', contentType);
    
    if (contentType === 'rhyme') {
      if (!selectedRhyme) return false;
      if (selectedRhyme === 'custom' && !customRhyme.trim()) return false;
      // Style musical obligatoire pour toutes les comptines
      if (!musicStyle) return false;
      // Validation supplémentaire pour le style musical personnalisé
      if (musicStyle === 'custom' && !customMusicStyle.trim()) return false;
    } else if (contentType === 'audio') {
      if (!selectedAudioStory) return false;
      if (selectedAudioStory === 'custom' && !customAudioStory.trim()) return false;
      // La voix est optionnelle
    } else if (contentType === 'coloring') {
      if (!selectedTheme) return false;
      if (selectedTheme === 'custom' && !customColoringTheme.trim()) {
        console.log('❌ Thème de coloriage personnalisé manquant');
        return false;
      }
    } else if (contentType === 'comic') {
      console.log('🎯 Debug validation BD:', {
        selectedComicTheme,
        selectedComicArtStyle,
        selectedComicCharacter,
        selectedComicStoryLength,
        customRequest: customRequest?.slice(0, 20) + '...',
        customCharacter: customCharacter?.slice(0, 20) + '...'
      });
      
      if (!selectedComicTheme) {
        console.log('❌ Thème BD manquant');
        return false;
      }
      if (selectedComicTheme === 'custom' && !customComicTheme.trim()) {
        console.log('❌ Thème personnalisé manquant');
        return false;
      }
      if (!selectedComicArtStyle) {
        console.log('❌ Style artistique manquant');
        return false;
      }
      if (!selectedComicCharacter) {
        console.log('❌ Personnage manquant');
        return false;
      }
      if (selectedComicCharacter === 'custom' && !customCharacter.trim()) {
        console.log('❌ Personnage personnalisé manquant');
        return false;
      }
      if (!selectedComicStoryLength) {
        console.log('❌ Longueur d\'histoire manquante');
        return false;
      }
      console.log('✅ Validation BD réussie');
    } else if (contentType === 'animation') {
      // Pour les animations, au minimum un thème doit être sélectionné
      if (!selectedAnimationTheme) return false;
      if (selectedAnimationTheme === 'custom' && !customStory.trim()) return false;
      // Vérifier que l'histoire personnalisée fait au moins 10 caractères
      if (selectedAnimationTheme === 'custom' && customStory.trim().length < 10) return false;
      // Durée, style et mode de génération sont optionnels mais recommandés
    } else if (contentType === 'seedance') {
      // Pour SEEDANCE, vérifier tous les champs obligatoires
      if (!customSeedanceStory.trim()) return false;
      if (customSeedanceStory.trim().length < 50) return false; // Minimum 50 caractères
      if (!selectedSeedanceTheme) return false;
      if (!selectedSeedanceAgeTarget) return false;
      if (!selectedSeedanceDuration) return false;
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
              // Afficher la comptine complète (paroles + audio)
              const completeRhyme = {
                ...tempData,
                audio_url: audioUrl,
                audio_path: audioUrl,
                music_status: 'completed'
              };
              setGeneratedResult(completeRhyme);
              setIsGenerating(false); // Arrêter l'état de génération
              // Ne pas supprimer tempRhymeData tout de suite pour le téléchargement
              console.log('🎵✅ Comptine complète affichée:', completeRhyme);
              console.log('🎵✅ Titre sauvegardé pour téléchargement:', tempData.title);
              console.log('🎵✅ completeRhyme.title final:', completeRhyme.title);
            } else {
              // Fallback : mise à jour simple
              setGeneratedResult(prev => ({
                ...prev,
                audio_url: audioUrl,
                audio_path: audioUrl,
                music_status: 'completed'
              }));
              setIsGenerating(false);
            }
          } else {
            console.warn('⚠️ Tâche terminée mais pas d\'URL audio');
            const tempData = window.tempRhymeData;
            if (tempData) {
              const completeRhyme = {
                ...tempData,
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
          // Tâche échouée
          console.error('❌ Génération musicale échouée:', status);
          const tempData = window.tempRhymeData;
          if (tempData) {
            // Afficher quand même les paroles même si la musique a échoué
            const rhymeWithError = {
              ...tempData,
              music_status: 'failed',
              music_error: status.error || 'Erreur de génération musicale'
            };
            setGeneratedResult(rhymeWithError);
            setIsGenerating(false);
            // Ne pas supprimer tempRhymeData pour conserver le titre
            console.log('🎵❌ Comptine affichée sans musique (erreur):', rhymeWithError);
          } else {
            setGeneratedResult(prev => ({
              ...prev,
              music_status: 'failed',
              music_error: status.error || 'Erreur de génération musicale'
            }));
            setIsGenerating(false);
          }
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
                <MusicalRhymeSelector
                  selectedRhyme={selectedRhyme}
                  setSelectedRhyme={setSelectedRhyme}
                  customRhyme={customRhyme}
                  setCustomRhyme={setCustomRhyme}
                  generateMusic={generateMusic}
                  setGenerateMusic={setGenerateMusic}
                  musicStyle={musicStyle}
                  setMusicStyle={setMusicStyle}
                  customMusicStyle={customMusicStyle}
                  setCustomMusicStyle={setCustomMusicStyle}
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
            ) : contentType === 'seedance' ? (
              <motion.div
                key="seedance-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <SeedanceSelector
                  selectedTheme={selectedSeedanceTheme}
                  setSelectedTheme={setSelectedSeedanceTheme}
                  selectedDuration={selectedSeedanceDuration}
                  setSelectedDuration={setSelectedSeedanceDuration}
                  selectedAgeTarget={selectedSeedanceAgeTarget}
                  setSelectedAgeTarget={setSelectedSeedanceAgeTarget}
                  customStory={customSeedanceStory}
                  setCustomStory={setCustomSeedanceStory}
                />
              </motion.div>
            ) : null}
          </AnimatePresence>          <CustomRequest
            customRequest={customRequest}
            setCustomRequest={setCustomRequest}
            stepNumber={contentType === 'coloring' ? 4 : 3}
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
          ? 'Création de votre comptine en cours…'
          : contentType === 'audio'
          ? 'Création de l\'histoire en cours...'
          : contentType === 'coloring'
          ? 'Création de votre coloriage en cours…'
          : contentType === 'animation'
          ? 'Création de votre dessin animé en cours...'
          : contentType === 'seedance'
          ? 'Création de votre animation SEEDANCE en cours...'
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
            // Utiliser le titre généré par l'IA, sinon fallback sur le thème
            const titleForDownload = currentTitle || (selectedTheme ? `coloriages_${selectedTheme}` : 'coloriages');
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
  />*/}  {!generatedResult && !coloringResult && !comicResult && (
    <div className="empty-preview">    <p>
      {contentType === 'rhyme'
        ? 'Votre comptine apparaîtra ici'
        : contentType === 'audio'
        ? 'Votre histoire apparaîtra ici'
        : contentType === 'coloring'
        ? 'Votre coloriage apparaîtra ici'
        : contentType === 'comic'
        ? 'Votre bande dessinée apparaîtra ici'
        : contentType === 'seedance'
        ? 'Votre animation SEEDANCE apparaîtra ici'
        : 'Votre dessin animé apparaîtra ici'}
    </p>
    </div>
  )}
  
  {/* 🎵 Affichage des comptines */}
  {contentType === 'rhyme' && generatedResult && (
    <div
      style={{
        height: '300px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem',
        padding: '1rem'
      }}
    >
      {/* Audio si disponible */}
      {(generatedResult.audio_path || generatedResult.audio_url) && (
        <audio
          controls
          style={{ width: '100%', maxWidth: '280px' }}
          src={generatedResult.audio_path || generatedResult.audio_url}
        />
      )}

      {/* Boutons d'action dans le style des cartes */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button
          onClick={() => {
            const audioUrl = generatedResult.audio_path || generatedResult.audio_url;
            if (!audioUrl) {
              alert('Audio non disponible pour le téléchargement');
              return;
            }
            
            // Essayer d'obtenir le titre depuis plusieurs sources avec priorité
            let title = 
              generatedResult.title || 
              currentTitle || 
              (window.tempRhymeData && window.tempRhymeData.title) ||
              'Ma_Comptine';
            
            console.log('🎵 Téléchargement - DEBUG COMPLET:');
            console.log('  - generatedResult:', generatedResult);
            console.log('  - generatedResult.title:', generatedResult.title);
            console.log('  - currentTitle:', currentTitle);
            console.log('  - window.tempRhymeData:', window.tempRhymeData);
            console.log('  - Titre final choisi:', title);
            
            // Vérifier que le titre n'est pas vide ou "undefined"
            if (!title || title === 'undefined' || title.trim() === '') {
              title = 'Ma_Comptine_Personnalisee';
              console.log('🎵 Titre vide détecté, utilisation du fallback:', title);
            }
            
            // Enlever les émojis et nettoyer le titre pour le nom de fichier
            const cleanTitle = title
              .replace(/[🎵🎶🎼🎤🎧🎹🥁🎺🎸🎻]/g, '') // Enlever les émojis musicaux
              .trim()
              .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Retirer les accents
              .toLowerCase()
              .replace(/\s+/g, "_") // Remplacer les espaces par des underscores
              .replace(/[^a-z0-9_]/g, ""); // Garder uniquement lettres, chiffres et underscores
            
            // Vérifier que le nom nettoyé n'est pas vide
            const finalFileName = cleanTitle || 'ma_comptine_personnalisee';
            
            console.log('🎵 Téléchargement - Nom de fichier final:', `${finalFileName}.mp3`);
            
            // Utiliser la route proxy du backend pour le téléchargement
            try {
              console.log('🎵 Début du téléchargement via proxy backend');
              const downloadUrl = API_ENDPOINTS.downloadAudio(finalFileName, audioUrl);
              
              const link = document.createElement('a');
              link.href = downloadUrl;
              link.download = `${finalFileName}.mp3`;
              link.style.display = 'none';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              
              console.log('🎵✅ Téléchargement initié avec le nom:', `${finalFileName}.mp3`);
            } catch (error) {
              console.error('❌ Erreur lors du téléchargement:', error);
              alert('Erreur lors du téléchargement du fichier.');
            }
          }}
          className="rhyme-button"
        >
          💾 Télécharger la comptine
        </button>
      </div>
      
      {/* Statut de génération musicale */}
      {generatedResult.task_id && !generatedResult.audio_path && (
        <div style={{
          padding: '0.5rem 1rem',
          backgroundColor: generatedResult.music_status === 'failed' || generatedResult.music_status === 'error' ? '#ffe5eb' : '#fff5e0',
          color: generatedResult.music_status === 'failed' || generatedResult.music_status === 'error' ? '#FF85A1' : '#FFD166',
          border: `2px solid ${generatedResult.music_status === 'failed' || generatedResult.music_status === 'error' ? '#FF85A1' : '#FFD166'}`,
          borderRadius: '16px',
          fontWeight: '600',
          textAlign: 'center',
          fontSize: '0.8rem',
          maxWidth: '280px'
        }}>
          {generatedResult.music_status === 'failed' || generatedResult.music_status === 'error' ? (
            `❌ Génération échouée`
          ) : generatedResult.music_status === 'completed_no_audio' ? (
            '⚠️ Audio non disponible'
          ) : (
            '🎵 Génération en cours...'
          )}
        </div>
      )}
    </div>
  )}
  
  {/* 🎵 Audio présent pour autres contenus */}
{contentType !== 'rhyme' && (generatedResult?.audio_path || generatedResult?.audio_url) && (
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
      src={generatedResult.audio_path || generatedResult.audio_url}
      download={(generatedResult.audio_path || generatedResult.audio_url)?.split('/').pop()}
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
      className="rhyme-button"
    >
      📖 Ouvrir l'histoire
    </button>

    <button
      onClick={() => downloadPDF(generatedResult.title, generatedResult.content)}
      className="rhyme-button"
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
    title={generatedResult.title}
    content={generatedResult.content}
    onClose={() => setShowStoryPopup(false)}
  />
)}

    {showColoringPopup && (
      <ColoringPopup
        coloringResult={coloringResult}
        selectedTheme={selectedTheme}
        onClose={() => setShowColoringPopup(false)}
      />
    )}

    {showComicPopup && (
      <ComicPopup
        comicResult={comicResult}
        onClose={() => setShowComicPopup(false)}
      />
    )}

    {showAnimationViewer && (
      <AnimationViewer
        animationResult={animationResult}
        onClose={() => setShowAnimationViewer(false)}
      />
    )}

    {showSeedanceViewer && (
      <SeedanceViewer
        seedanceResult={seedanceResult}
        onClose={() => setShowSeedanceViewer(false)}
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
