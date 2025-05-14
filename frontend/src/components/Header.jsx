import React from 'react';
import { motion } from 'framer-motion';
import './Header.css';
import UserAccount from './UserAccount';

const Header = ({ isLoggedIn, onLogin, onLogout, onRegister }) => {
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
          <h1>FRIDAY</h1>
        </motion.div>
        
        <motion.h2 
          className="tagline"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          Créez des histoires et des comptines magiques pour vos enfants !
        </motion.h2>
      </div>
      
      <div className="user-account-container">
        <UserAccount 
          isLoggedIn={isLoggedIn}
          onLogin={onLogin}
          onLogout={onLogout}
          onRegister={onRegister}
        />
      </div>
    </header>
  );
};

export default Header;
