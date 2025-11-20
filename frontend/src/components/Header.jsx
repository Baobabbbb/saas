import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './Header.css';
import UserAccount from './UserAccount';
import { supabase } from '../supabaseClient';

const Header = ({ isLoggedIn, onLogin, onLogout, onRegister, onOpenHistory, userId, onOpenSubscription, refreshBonusTrigger }) => {
  const [showWelcomeBonus, setShowWelcomeBonus] = useState(false);

  useEffect(() => {
    const checkWelcomeBonus = async () => {
      if (isLoggedIn && userId) {
        try {
          // Vérifier si l'utilisateur a déjà créé du contenu
          const { data: creations, error: creationsError } = await supabase
            .from('creations')
            .select('id')
            .eq('user_id', userId)
            .limit(1);

          if (creationsError) {
            console.error('Erreur vérification créations:', creationsError);
            setShowWelcomeBonus(false);
            return;
          }

          // Si aucune création, afficher le bonus
          const hasCreations = creations && creations.length > 0;
          setShowWelcomeBonus(!hasCreations);
        } catch (error) {
          console.error('Erreur vérification bonus bienvenue:', error);
          setShowWelcomeBonus(false);
        }
      } else {
        // Si pas connecté, afficher le bonus pour inciter à l'inscription
        setShowWelcomeBonus(true);
      }
    };

    checkWelcomeBonus();
  }, [isLoggedIn, userId, refreshBonusTrigger]);

  return (
    <header className="header">
      <div className="header-content">
        <motion.div 
          className="logo"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            type: "spring", 
            stiffness: 260, 
            damping: 20,
            delay: 0.1
          }}
        >
          {/*<motion.img 
            src="/cloud-logo.svg" 
            alt="BDKids logo" 
            animate={{ 
              y: [0, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 3,
              ease: "easeInOut",
              times: [0, 0.5, 1],
              repeat: Infinity,
              repeatDelay: 0.5
            }}
          />*/}
          <h1>HERBBIE</h1>
        </motion.div>
          <motion.h2 
          className="tagline"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          Offrez à vos enfants des créations ludiques et imaginatives personnalisées !
        </motion.h2>

        {showWelcomeBonus && (
          <motion.p
            className="welcome-bonus-message"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.5 }}
          >
            🎁 Un coloriage ou une histoire gratuit après inscription !
          </motion.p>
        )}

        <motion.p
          className="animation-coming-soon"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
        >
          La création de dessins animés sera bientôt disponible.
        </motion.p>
      </div>
      
      <div className="user-account-container">
        <UserAccount
          isLoggedIn={isLoggedIn}
          onLogin={onLogin}
          onLogout={onLogout}
          onRegister={onRegister}
          onOpenHistory={onOpenHistory}
          onOpenSubscription={onOpenSubscription}
        />
      </div>
    </header>
  );
};

export default Header;
