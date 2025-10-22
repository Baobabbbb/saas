import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import Confetti from 'react-confetti';
import './App.css';
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
import ComicsSelector from './components/ComicsSelector';
import ComicsPopup from './components/ComicsPopup';
import useSupabaseUser from './hooks/useSupabaseUser';
import { API_BASE_URL, ANIMATION_API_BASE_URL } from './config/api';

import { addCreation } from './services/creations';
import { downloadColoringAsPDF } from './utils/coloringPdfUtils';
import { checkPaymentPermission, hasFreeAccess, getContentPrice } from './services/payment';
import StripePaymentModal from './components/StripePaymentModal';
import Footer from './components/Footer';
import LegalPages from './components/LegalPages';
import ShootingStars from './components/ShootingStars';

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
  const [contentType, setContentType] = useState('animation'); // 'rhyme', 'audio', 'coloring', 'animation' - Dessin animé sélectionné par défaut
  const [selectedRhyme, setSelectedRhyme] = useState(null);
  const [customRhyme, setCustomRhyme] = useState('');
  
  // Musical rhyme states (nouveau)
  const [generateMusic, setGenerateMusic] = useState(true);
  const [musicStyle, setMusicStyle] = useState(''); // Changé de 'auto' à '' pour éviter la sélection par défaut
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

  // Coloring states
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [customColoringTheme, setCustomColoringTheme] = useState('');
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [coloringResult, setColoringResult] = useState(null);
  const [withColoredModel, setWithColoredModel] = useState(null); // null = aucun choix fait, obligatoire
  
  // Comics states
  const [selectedComicsTheme, setSelectedComicsTheme] = useState(null);
  const [selectedComicsStyle, setSelectedComicsStyle] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [customComicsStory, setCustomComicsStory] = useState('');
  const [characterPhoto, setCharacterPhoto] = useState(null);
  const [comicsResult, setComicsResult] = useState(null);
  const [showComicsPopup, setShowComicsPopup] = useState(false);

  // Réinitialiser les sélections comics quand on change d'onglet
  useEffect(() => {
    if (contentType === 'comic') {
      setSelectedComicsStyle(null);
      setNumPages(null);
    }
  }, [contentType]);

  // Animation states
  const [selectedAnimationTheme, setSelectedAnimationTheme] = useState(null); // Aucun thème par défaut
  const [selectedDuration, setSelectedDuration] = useState(null);
  const [selectedStyle, setSelectedStyle] = useState(null);
  const [customStory, setCustomStory] = useState('');

  // Histoire states
  const [selectedStory, setSelectedStory] = useState(null);
  const [animationResult, setAnimationResult] = useState(null);
  const [showAnimationViewer, setShowAnimationViewer] = useState(false);

  // États pour le système de paiement
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentContentType, setPaymentContentType] = useState(null);
  const [userRole, setUserRole] = useState('user');
  const [isAdmin, setIsAdmin] = useState(false);
  const [buttonText, setButtonText] = useState('Générer');

  // États pour les pages légales
  const [showLegalPages, setShowLegalPages] = useState(false);
  const [legalInitialSection, setLegalInitialSection] = useState('mentions');

  // Utilitaire d'attente
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  // Polling du statut d'une animation jusqu'à complétion
  const waitForAnimationCompletion = async (taskId, { intervalMs = 5000, maxAttempts = 240 } = {}) => {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const res = await fetch(`${ANIMATION_API_BASE_URL}/status/${taskId}`);
        
        if (res.ok) {
          const statusPayload = await res.json();
          
          if (statusPayload?.type === 'result') {
            const data = statusPayload.data;
            
            if (data?.status === 'completed') {
              // Vérifier qu'il y a vraiment du contenu
              if (data?.clips && data.clips.length > 0) {
                return data;
              } else {
              }
            }
            if (data?.status === 'failed') {
              throw new Error(data?.error_message || 'Génération échouée');
            }
          }
        }
      } catch (e) {
        // Continue polling même en cas d'erreur
      }
      
      attempts += 1;
      await delay(intervalMs);
    }
    
    throw new Error('Timeout de génération de l\'animation');
  };

  // Polling du statut d'une BD jusqu'à complétion
  const waitForComicCompletion = async (taskId, { intervalMs = 5000, maxAttempts = 180 } = {}) => {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const res = await fetch(`${API_BASE_URL}/status_comic/${taskId}`);
        
        if (res.ok) {
          const statusPayload = await res.json();
          
          if (statusPayload?.type === 'result') {
            const data = statusPayload.data;
            
            if (data?.status === 'completed' || data?.status === 'success') {
              // BD terminée avec contenu
              if (data?.pages && data.pages.length > 0) {
                return data;
              }
            }
            if (data?.status === 'failed') {
              throw new Error(data?.error || 'Génération échouée');
            }
            // Afficher la progression
            if (data?.progress) {
              console.log(`📚 Génération BD: ${data.progress}%`);
            }
          }
        }
      } catch (e) {
        // Continue polling même en cas d'erreur
      }
      
      attempts += 1;
      await delay(intervalMs);
    }
    
    throw new Error('Timeout de génération de la BD');
  };

  // Upload de photo de personnage pour BD
  const handleCharacterPhotoUpload = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/upload_character_photo/`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error(`Erreur upload : ${response.status}`);
      
      const data = await response.json();
      setCharacterPhoto(data);
      return data;
    } catch (error) {
      console.error('Erreur upload photo personnage:', error);
      throw error;
    }
  };

  // Store the current generated title for use in UI
  const [currentTitle, setCurrentTitle] = useState(null);

  // État compte utilisateur via hook standard (évite l'écran blanc au premier chargement)
  const { user, loading } = useSupabaseUser();
  const [showHistory, setShowHistory] = useState(false);
  const [userHasFreeAccess, setUserHasFreeAccess] = useState(false);

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

  // Vérifier si l'utilisateur a accès gratuit et mettre à jour le bouton
  useEffect(() => {
    const checkFreeAccessStatus = async () => {
      if (user) {
        const freeAccessStatus = await hasFreeAccess(user.id, user.email);
        setUserHasFreeAccess(freeAccessStatus);
        updateButtonText(freeAccessStatus);
      } else {
        setUserHasFreeAccess(false);
        updateButtonText(false);
      }
    };

    checkFreeAccessStatus();
  }, [user, contentType]);

  // S'assurer qu'aucun bouton n'est sélectionné par défaut quand on change de type de contenu
  useEffect(() => {
    // Remettre à zéro toutes les sélections quand on change de type de contenu
    setSelectedRhyme(null);
    setCustomRhyme('');
    setGenerateMusic(true);
    setMusicStyle(''); // Remettre à zéro au lieu de 'auto'
    setCustomMusicStyle('');
    setSelectedAudioStory(null);
    setCustomAudioStory('');
    setSelectedVoice(null);
    setSelectedTheme(null);
    setCustomColoringTheme('');
    setUploadedPhoto(null);
    setWithColoredModel(null); // Remettre à zéro le choix du modèle
    setSelectedComicsTheme(null);
    setSelectedComicsStyle(null);
    setNumPages(null);
    setCustomComicsStory('');
    setCharacterPhoto(null);
    setComicsResult(null);
    setSelectedAnimationTheme(null);
    setSelectedDuration(null);
    setSelectedStyle(null);
    setCustomStory('');
    setSelectedStory(null);
    setGeneratedResult(null);
    setColoringResult(null);
    setAnimationResult(null);
    setCurrentTitle(null);
  }, [contentType]);

  // Initialiser le thème par défaut pour les animations
  useEffect(() => {
    if (contentType === 'animation' && !selectedAnimationTheme) {
      setSelectedAnimationTheme(null); // Aucun thème par défaut
    }
  }, [contentType, selectedAnimationTheme]);

  // S'assurer que le thème est toujours défini
  const currentTheme = selectedAnimationTheme || 'space';

  // Mettre à jour le texte du bouton selon le statut admin et le type de contenu
  const updateButtonText = (adminStatus) => {
    if (adminStatus) {
      setButtonText('Générer Gratuitement');
    } else {
      const priceInfo = getContentPrice(contentType);
      setButtonText(`Acheter pour ${priceInfo.display}`);
    }
  };
  
  // Handle Generation
  const handleGenerate = async () => {
    // Récupérer l'utilisateur connecté
    if (!user) {
      alert('Vous devez être connecté pour générer du contenu');
      return;
    }

    // Si l'utilisateur a accès gratuit (admin ou free), génération directe
    if (userHasFreeAccess) {
      startGeneration();
      return;
    }

    // Si utilisateur normal, vérifier les permissions
    const permissionCheck = await checkPaymentPermission(
      contentType, 
      user.id, 
      user.email
    );
    
    if (!permissionCheck.hasPermission) {
      // Ouvrir directement la modal de paiement
      setPaymentContentType(contentType);
      setShowPaymentModal(true);
      return;
    } else {
      // Permission accordée, génération directe
      startGeneration();
    }
  };

  // Fonction pour démarrer la génération (après vérification permissions)
  const startGeneration = async () => {
    setIsGenerating(true);
    setGeneratedResult(null);
    // setShowConfetti(true);

    if (loading) return;

    try {
      let generatedContent = null;

      if (contentType === 'rhyme') {
        const payload = {
          theme: selectedRhyme === 'custom' ? customRhyme : selectedRhyme,
          custom_request: customRequest,
          language: 'fr'
        };
        // Utiliser l'endpoint correct pour les comptines
        const response = await fetch(`${API_BASE_URL}/generate_rhyme/`, {
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
      };      const response = await fetch(`${API_BASE_URL}/generate_audio_story/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
    } else if (contentType === 'histoire') {
      // Déterminer le contenu de l'histoire
      let storyContent;
      if (selectedStory && selectedStory !== 'custom') {
        // Thème prédéfini - créer une histoire de base
        const storyThemes = {
          'space': 'Une aventure spatiale extraordinaire où un enfant explore les planètes lointaines et rencontre des aliens amicaux.',
          'ocean': 'Une exploration sous-marine magique avec des créatures marines colorées et des trésors cachés au fond de l\'océan.',
          'dinosaur': 'Un voyage dans le temps à l\'époque des dinosaures où un enfant devient ami avec un dinosaure gentil et découvre un monde préhistorique.',
          'fairy': 'Un conte de fées enchanteur avec des fées bienveillantes, des châteaux magiques et des aventures pleines de poussière de fée.',
          'superhero': 'Une histoire de super-héros où un enfant découvre ses pouvoirs extraordinaires et sauve la ville avec courage et bonté.',
          'jungle': 'Une aventure dans la jungle tropicale remplie d\'animaux exotiques, de plantes mystérieuses et de découvertes passionnantes.'
        };
        storyContent = storyThemes[selectedStory] || `Une belle histoire sur le thème ${selectedStory}`;
      } else {
        // Histoire personnalisée
        storyContent = customStory;
      }

      // Validation de l'histoire avant envoi
      if (!storyContent || storyContent.trim().length < 10) {
        throw new Error("L'histoire doit contenir au moins 10 caractères");
      }

      const payload = {
        story_type: selectedStory === 'custom' ? 'custom' : selectedStory,
        content: storyContent,
        custom_request: customRequest
      };

      const response = await fetch(`${API_BASE_URL}/generate_story/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      generatedContent = await response.json();
    } else if (contentType === 'coloring') {
      // Si l'utilisateur a uploadé une photo, utiliser l'endpoint de conversion
      if (uploadedPhoto) {
        // 1. Upload de la photo
        const formData = new FormData();
        formData.append('file', uploadedPhoto);
        
        const uploadResponse = await fetch(`${API_BASE_URL}/upload_photo_for_coloring/`, {
          method: 'POST',
          body: formData
        });
        
        if (!uploadResponse.ok) throw new Error(`Erreur upload : ${uploadResponse.status}`);
        
        const uploadData = await uploadResponse.json();
        
        // 2. Conversion en coloriage avec GPT-4o-mini + gpt-image-1-mini
        const conversionPayload = {
          photo_path: uploadData.file_path,
          with_colored_model: withColoredModel
        };
        
        const conversionResponse = await fetch(`${API_BASE_URL}/convert_photo_to_coloring/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(conversionPayload)
        });
        
        if (!conversionResponse.ok) throw new Error(`Erreur conversion : ${conversionResponse.status}`);
        
        const coloringData = await conversionResponse.json();
        
        setColoringResult(coloringData);
        generatedContent = coloringData;
      } else {
        // Génération classique par thème
        const payload = {
          theme: selectedTheme,
          with_colored_model: withColoredModel
        };
        
        // Si c'est un coloriage personnalisé, ajouter le prompt personnalisé
        if (selectedTheme === 'custom' && customColoringTheme.trim()) {
          payload.custom_prompt = customColoringTheme.trim();
        }
        
        const response = await fetch(`${API_BASE_URL}/generate_coloring/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        
        const coloringData = await response.json();
        
        setColoringResult(coloringData);
        generatedContent = coloringData; // Stocker pour l'historique
      }
    } else if (contentType === 'comic') {
      // Génération de bande dessinée avec système de tâches asynchrones
      const payload = {
        theme: selectedComicsTheme === 'custom' ? customComicsStory : selectedComicsTheme,
        art_style: selectedComicsStyle || 'cartoon', // Style par défaut si aucun sélectionné
        num_pages: numPages || 1 // Nombre de pages par défaut si aucun sélectionné
      };

      // Si histoire personnalisée
      if (selectedComicsTheme === 'custom' && customComicsStory.trim()) {
        payload.custom_prompt = customComicsStory.trim();
      }

      // Si photo de personnage uploadée
      if (characterPhoto && characterPhoto.file_path) {
        payload.character_photo_path = characterPhoto.file_path;
      }

      const response = await fetch(`${API_BASE_URL}/generate_comic/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);

      const initialData = await response.json();
      
      // Attendre la complétion avec polling
      let finalData = initialData;
      const taskId = initialData?.task_id;
      const isCompleted = initialData?.status === 'success' && initialData?.pages && initialData.pages.length > 0;

      if (taskId && !isCompleted) {
        // Rester en état de chargement pendant le polling
        finalData = await waitForComicCompletion(taskId);
      }

      // Ne définir le résultat qu'après complétion
      if (finalData?.pages && finalData.pages.length > 0) {
        setComicsResult(finalData);
        generatedContent = finalData;
      }
    } else if (contentType === 'animation') {
      // Déterminer le contenu de l'histoire
      let story;
      const currentTheme = selectedAnimationTheme || 'space'; // Fallback si null
      if (currentTheme && currentTheme !== 'custom') {
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
        story = themeStories[currentTheme] || `Une belle histoire sur le thème ${currentTheme}`;
      } else {
        // Histoire personnalisée
        story = customStory;
      }
      
      // Validation de l'histoire avant envoi
      if (!story || story.trim().length < 10) {
        throw new Error("L'histoire doit contenir au moins 10 caractères");
      }
      
      // Aligner avec le schéma backend: theme (en anglais), duration (30|60|120|180|240|300), custom_prompt optionnel
      const normalizedThemeMap = {
        'magie': 'magic',
        'aventure': 'adventure',
        'animaux': 'animals',
        'espace': 'space',
        'nature': 'nature',
        'amitié': 'friendship',
        'famille': 'friendship'
      };
      const normalizedTheme = normalizedThemeMap[currentTheme] || currentTheme || 'adventure';

      const payload = {
        theme: normalizedTheme,
        duration: Number(selectedDuration),
        // user_id optionnel: non requis pour la démo
        custom_prompt: story || undefined
      };

      // Utiliser toujours le vrai pipeline zseedance (endpoint generate-quick)
      const endpoint = `${API_BASE_URL}/generate-quick?theme=${encodeURIComponent(normalizedTheme)}&duration=${selectedDuration}&style=${selectedStyle || 'cartoon'}`;
      const fetchOptions = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      };

      const response = await fetch(endpoint, fetchOptions);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur HTTP ${response.status}: ${errorText}`);
      }

      const initialData = await response.json();

      // Ne pas ouvrir le viewer tout de suite; attendre la complétion réelle
      let finalData = initialData;
      const taskId = initialData?.task_id;
      const isCompleted = initialData?.status === 'completed' && (initialData?.final_video_url || (initialData?.clips?.length || 0) > 0);

      if (taskId && !isCompleted) {
        // Rester en état de chargement pendant le polling
        finalData = await waitForAnimationCompletion(taskId);
      }

      // Ne définir le résultat et ouvrir le viewer qu'après complétion avec contenu
      if (finalData?.status === 'completed' && finalData?.clips && finalData.clips.length > 0) {
        setAnimationResult(finalData);
        setShowAnimationViewer(true);
        generatedContent = finalData; // Stocker pour l'historique
      }
    }

    // 🔁 Enregistre le résultat généré pour affichage audio/texte
    setGeneratedResult(generatedContent);
    // setStoryPages(splitTextIntoPages(generatedContent.content)); // Ajoute la pagination
    setCurrentPageIndex(0); // Reviens à la première page

    // 🎵 Démarrer le polling automatique si c'est une comptine avec task_id
    // IMPORTANT : On garde isGenerating = true jusqu'à ce que la musique soit prête
    if (contentType === 'rhyme' && generatedContent.task_id) {
      // NE PAS arrêter isGenerating ici, le polling le fera quand la musique est prête
      pollTaskStatus(generatedContent.task_id);
      return; // Sortir de la fonction pour garder isGenerating = true
    }    // Déterminer le titre avec des noms attractifs pour les enfants
    let title;
    if (contentType === 'rhyme') {
      // Utiliser le titre de l'IA ou générer un titre attractif
      // Utiliser le titre de l'IA pour les comptines (avec ou sans musique)
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
      }    } else if (contentType === 'coloring') {
      // Utiliser le titre généré par l'IA depuis l'API coloriage
      title = generatedContent?.title || generateChildFriendlyTitle('coloriage', selectedTheme);
    } else if (contentType === 'comic') {
      // Utiliser le titre généré par l'IA pour la BD
      title = comicsResult?.title || 'Ma Bande Dessinée 📚';
    } else if (contentType === 'animation') {
      // Utiliser le titre généré par l'IA depuis l'API animation
      title = generatedContent?.title || generateChildFriendlyTitle('animation', currentTheme || 'aventure');
    } else if (contentType === 'histoire') {
      // Utiliser le titre généré par l'IA depuis l'API histoire
      title = generatedContent?.title || generateChildFriendlyTitle('histoire', selectedStory === 'custom' ? 'default' : selectedStory);
    }

    // Stocker le titre pour l'utiliser dans l'UI
    setCurrentTitle(title);

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
      } else if (contentType === 'comic') {
        // Pour les BD, utiliser les données de la BD
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: comicsResult ? `BD de ${comicsResult.total_pages} planche(s) - ${comicsResult.total_pages * 4} cases` : 'Bande dessinée générée',
          theme: selectedComicsTheme,
          pages: comicsResult?.pages || [],
          comic_data: comicsResult || {}
        };
      } else if (contentType === 'animation') {
        // Pour les animations, utiliser les données de l'animation
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent ? `Animation de ${generatedContent.actual_duration}s avec ${generatedContent.total_scenes} scènes` : 'Animation générée',
          theme: currentTheme,
          clips: generatedContent?.clips || [],
          animation_data: generatedContent || {}
        };
      } else if (contentType === 'histoire') {
        // Pour les histoires, utiliser les données de l'histoire
        newCreation = {
          id: Date.now().toString(),
          type: contentType,
          title: title,
          createdAt: new Date().toISOString(),
          content: generatedContent?.content || generatedContent || 'Histoire générée...',
          story_type: selectedStory === 'custom' ? 'custom' : selectedStory
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
        // Erreur silencieuse - historique non critique
      }

    // setTimeout(() => setShowConfetti(false), 3000);
    
    // Arrêter l'animation de chargement pour les autres types de contenu
    // (pour les comptines, c'est géré par pollTaskStatus)
    setIsGenerating(false);
  } catch (error) {
    // Afficher une alerte avec plus d'informations
    alert(`❌ Erreur lors de la génération : ${error.message}\n\n💡 Conseil : Vérifiez que les clés API sont configurées dans le fichier .env du serveur.`);
    setIsGenerating(false);
  }
  
  // NE PAS mettre finally ici car pour les comptines on fait un return avant
  // et le polling gère le setIsGenerating(false)
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
    } else if (contentType === 'coloring') {
      // Valide si thème sélectionné OU photo uploadée
      if (!selectedTheme && !uploadedPhoto) return false;
      // Si thème custom, vérifier le texte personnalisé
      if (selectedTheme === 'custom' && !customColoringTheme.trim()) return false;
      // Le choix du modèle (avec/sans) est obligatoire
      if (withColoredModel === null) return false;
    } else if (contentType === 'comic') {
      // Pour les BD: thème, style et nombre de pages sont tous obligatoires
      if (!selectedComicsTheme) return false;
      if (!selectedComicsStyle) return false;
      if (!numPages) return false;
      if (selectedComicsTheme === 'custom' && !customComicsStory.trim()) return false;
    } else if (contentType === 'animation') {
      // Pour les animations, soit un thème soit une histoire personnalisée
      if (!selectedAnimationTheme && !customStory.trim()) return false;
      if (selectedAnimationTheme === 'custom' && !customStory.trim()) return false;
      // Vérifier que l'histoire personnalisée fait au moins 10 caractères
      if (selectedAnimationTheme === 'custom' && customStory.trim().length < 10) return false;
    } else if (contentType === 'histoire') {
      // Pour les histoires, soit un thème soit une histoire personnalisée
      if (!selectedStory) return false;
      if (selectedStory === 'custom' && !customStory.trim()) return false;
      // Vérifier que l'histoire personnalisée fait au moins 10 caractères
      if (selectedStory === 'custom' && customStory.trim().length < 10) return false;
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

  const backgroundImageUrl = "/assets/fond_etoiles.png";
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

 // Fonction de polling automatique pour vérifier le statut des tâches musicales Suno
  const pollTaskStatus = async (taskId, maxAttempts = 40, interval = 5000) => {
    let attempts = 0;
    
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/check_task_status/${taskId}`);
        const status = await response.json();
        
        if (status.status === 'completed' && status.songs && status.songs.length > 0) {
          // Tâche Suno terminée avec succès
          setGeneratedResult(prev => {
            const updatedResult = {
              ...prev,
              songs: status.songs,
              has_music: true,
              service: 'suno'
            };
            
            // Enregistrer dans l'historique maintenant que la musique est prête
            const title = prev.title || generateChildFriendlyTitle('comptine', selectedRhyme === 'custom' ? 'default' : selectedRhyme) + ' 🎵';
            setCurrentTitle(title);
            
            // Créer l'entrée d'historique
            const newCreation = {
              id: Date.now().toString(),
              type: 'rhyme',
              title: title,
              createdAt: new Date().toISOString(),
              content: prev.content || prev.rhyme || 'Comptine générée',
              songs: status.songs
            };
            
            // Sauvegarder dans l'historique via Supabase
            addCreation({
              type: 'rhyme',
              title: title,
              data: newCreation
            }).catch(historyError => {
              // Erreur silencieuse - historique non critique
            });
            
            return updatedResult;
          });
          setIsGenerating(false); // ✅ ARRÊTER l'animation de chargement
          return true; // Arrêter le polling
        } else if (status.status === 'failed') {
          // Tâche échouée
          setGeneratedResult(prev => ({
            ...prev,
            music_error: status.error,
            has_music: false
          }));
          setIsGenerating(false); // ✅ ARRÊTER l'animation de chargement même en cas d'erreur
          return true; // Arrêter le polling
        } else if (status.status === 'processing') {
          // En cours de traitement
        } else if (attempts >= maxAttempts - 1) {
          // Timeout atteint
          setIsGenerating(false); // ✅ ARRÊTER l'animation de chargement
          alert('⚠️ La génération de musique prend plus de temps que prévu. Veuillez vérifier votre historique dans quelques minutes.');
          return true; // Arrêter le polling
        }
        
        // Continuer le polling
        attempts++;
        setTimeout(checkStatus, interval);
        return false;
        
      } catch (error) {
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, interval);
        }
        return false;
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
      onOpenHistory={() => setShowHistory(true)}
    />

    {/* 🌟 Étoiles filantes pour dynamiser le fond */}
    <ShootingStars />

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
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                style={{ width: '100%' }}
              >
                <MusicalRhymeSelector
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
                  uploadedPhoto={uploadedPhoto}
                  setUploadedPhoto={setUploadedPhoto}
                  withColoredModel={withColoredModel}
                  setWithColoredModel={setWithColoredModel}
                />
              </motion.div>
            ) : contentType === 'comic' ? (
              <motion.div
                key="comics-selector"
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3 }}
              >
                <ComicsSelector
                  selectedTheme={selectedComicsTheme}
                  setSelectedTheme={setSelectedComicsTheme}
                  selectedStyle={selectedComicsStyle}
                  setSelectedStyle={setSelectedComicsStyle}
                  numPages={numPages}
                  setNumPages={setNumPages}
                  customStory={customComicsStory}
                  setCustomStory={setCustomComicsStory}
                  characterPhoto={characterPhoto}
                  setCharacterPhoto={setCharacterPhoto}
                  onCharacterPhotoUpload={handleCharacterPhotoUpload}
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
            ) : contentType === 'histoire' ? (
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
            buttonText={buttonText}
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
      </div>      <p>        {        contentType === 'rhyme'
          ? 'Votre comptine est en cours de création...'
          : contentType === 'audio'
          ? 'Création de l\'histoire en cours...'
          : contentType === 'histoire'
          ? 'Création de votre histoire en cours...'
          : contentType === 'coloring'
          ? 'Création de vos coloriages en cours...'
          : contentType === 'comic'
          ? 'Création de votre bande dessinée en cours...'
          : contentType === 'animation'
          ? 'Création de votre dessin animé en cours...'
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
  ) : comicsResult && contentType === 'comic' ? (
    <motion.div
      className="generated-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="comics-result"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem',
        padding: '1rem'
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem' }}>
          {comicsResult.title || 'Votre Bande Dessinée'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          {comicsResult.total_pages} {comicsResult.total_pages === 1 ? 'planche' : 'planches'} • {comicsResult.total_pages * 4} cases
        </p>
      </div>
      <button
        onClick={() => setShowComicsPopup(true)}
        style={{
          padding: '0.8rem 2rem',
          backgroundColor: '#6B4EFF',
          color: '#fff',
          border: 'none',
          borderRadius: '12px',
          cursor: 'pointer',
          fontWeight: '700',
          fontSize: '1rem',
          boxShadow: '0 4px 12px rgba(245, 240, 255, 0.3)',
          transition: 'all 0.2s ease'
        }}
        onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
        onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
      >
        📚 Lire la bande dessinée
      </button>
    </motion.div>
  ) : generatedResult && contentType === 'rhyme' && generatedResult.songs && generatedResult.songs.length > 0 ? (
    <motion.div
      className="generated-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="rhyme-result"
    >
      <div
        style={{
          height: '300px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '0.8rem',
          padding: '1rem',
          overflowY: 'auto'
        }}
      >
        {/* Audio si disponible - Une seule comptine */}
        {generatedResult.songs && generatedResult.songs.length > 0 && (
          <>
            {generatedResult.songs.map((song, index) => (
              <div key={song.id || index} style={{ 
                background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', 
                padding: '22px', 
                borderRadius: '15px',
                border: '2px solid #dee2e6',
                width: '100%',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '10px', 
                  marginBottom: '14px' 
                }}>
                  <span style={{ fontSize: '24px' }}>🎵</span>
                  <h4 style={{ margin: 0, fontSize: '15px', color: '#333', fontWeight: '600' }}>
                    Votre comptine est prête !
                  </h4>
                </div>
                <audio
                  controls
                  preload="metadata"
                  controlsList="nodownload"
                  style={{
                    width: '100%',
                    height: '60px',
                    outline: 'none'
                  }}
                  src={song.audio_url}
                >
                  Votre navigateur ne supporte pas l'élément audio.
                </audio>
              </div>
            ))}
            
            {/* Bouton Télécharger unique */}
            <button
              onClick={async () => {
                if (generatedResult.songs && generatedResult.songs.length > 0) {
                  const song = generatedResult.songs[0];
                  try {
                    const response = await fetch(song.audio_url);
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    const safeTitle = (currentTitle || 'Comptine').replace(/[^a-z0-9]/gi, '_').toLowerCase();
                    link.download = `${safeTitle}.mp3`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                  } catch (error) {
                    // Fallback si CORS bloque
                    window.open(song.audio_url, '_blank');
                  }
                }
              }}
              style={{
                padding: '0.8rem 2rem',
                backgroundColor: '#6B4EFF',
                color: '#fff',
                border: 'none',
                borderRadius: '10px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                marginTop: '0.8rem',
                boxShadow: '0 4px 12px rgba(245, 240, 255, 0.3)',
                transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
            >
              📥 Télécharger
            </button>
          </>
        )}
      </div>
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
  />*/}  {!generatedResult?.content && !coloringResult && (
    <div className="empty-preview">    <p>
      {        contentType === 'rhyme'
        ? 'Votre comptine apparaîtra ici'
        : contentType === 'audio'
        ? 'Votre histoire apparaîtra ici'
        : contentType === 'histoire'
        ? 'Votre histoire apparaîtra ici'
        : contentType === 'coloring'
        ? 'Votre coloriage apparaîtra ici'
        : contentType === 'comic'
        ? 'Votre bande dessinée apparaîtra ici'
        : contentType === 'animation'
        ? 'Votre dessin animé apparaîtra ici'
        : 'Votre contenu apparaîtra ici'}
    </p>
    </div>
  )}
  {/* 🎵 Audio présent pour autres contenus */}
{contentType !== 'rhyme' && generatedResult?.audio_path && (
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
      src={`${API_BASE_URL}/${generatedResult.audio_path}`}
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
)}    {showColoringPopup && (
      <ColoringPopup
        coloringResult={coloringResult}
        selectedTheme={selectedTheme}
        onClose={() => setShowColoringPopup(false)}
      />
    )}

    {showComicsPopup && (
      <ComicsPopup
        comic={comicsResult}
        onClose={() => setShowComicsPopup(false)}
        baseUrl={API_BASE_URL}
      />
    )}

    {showAnimationViewer && (
      <AnimationViewer
        animationResult={animationResult}
        onClose={() => setShowAnimationViewer(false)}
      />
    )}

    {/* Modal de paiement Stripe */}
    {showPaymentModal && (
      <StripePaymentModal
        contentType={paymentContentType}
        userId={user?.id}
        userEmail={user?.email}
        onSuccess={(result) => {
          setShowPaymentModal(false);
          // Lancer la génération automatiquement après paiement réussi
          setTimeout(() => {
            startGeneration();
          }, 500);
        }}
        onCancel={() => {
          setShowPaymentModal(false);
        }}
      />
    )}
    {/* Footer avec mentions légales et contact */}
    <Footer onLegalClick={(section) => {
      setShowLegalPages(true);
      setLegalInitialSection(section);
    }} />

    {/* Pages légales */}
    <AnimatePresence>
      {showLegalPages && (
        <LegalPages
          onClose={() => setShowLegalPages(false)}
          initialSection={legalInitialSection}
        />
      )}
    </AnimatePresence>
  </div>
);
}

export default App;
