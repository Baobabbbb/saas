import React from 'react';
import { motion } from 'framer-motion';
import './Header.css';
import UserAccount from './UserAccount';
import TokenDisplay from './subscription/TokenDisplay';

const Header = ({ isLoggedIn, onLogin, onLogout, onRegister, onOpenHistory, userId, onOpenSubscription }) => {
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
      </div>
      
      <div className="user-account-container">
        {isLoggedIn && userId && (
          <div className="flex items-center space-x-4 mr-4">
            <TokenDisplay userId={userId} compact={true} />
            <button
              onClick={onOpenSubscription}
              className="bg-violet-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-violet-700 transition-colors duration-200 text-sm"
            >
              🎫 Abonnement
            </button>
          </div>
        )}
        <UserAccount
          isLoggedIn={isLoggedIn}
          onLogin={onLogin}
          onLogout={onLogout}
          onRegister={onRegister}
          onOpenHistory={onOpenHistory}
        />
      </div>
    </header>
  );
};

export default Header;
