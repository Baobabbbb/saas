import React from 'react';
import { motion } from 'framer-motion';
import './AdminPanel.css';

const AdminPanel = ({ onClose }) => {
  return (
    <motion.div 
      className="admin-panel-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div 
        className="admin-panel"
        initial={{ opacity: 0, scale: 0.9, y: 50 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 50 }}
        transition={{ duration: 0.3 }}
      >
        <div className="admin-panel-header">
          <h2>Panneau Administrateur</h2>
          <button 
            className="admin-panel-close"
            onClick={onClose}
          >
            ✕
          </button>
        </div>
        
        <div className="admin-panel-content">
          <div className="admin-welcome">
            <p>Bienvenue dans le panneau administrateur !</p>
            <p>Les fonctionnalités seront ajoutées prochainement.</p>
          </div>
          
          <div className="admin-sections">
            <div className="admin-section-placeholder">
              <h3>📊 Gestion des utilisateurs</h3>
              <p>Fonctionnalité à venir...</p>
            </div>
            
            <div className="admin-section-placeholder">
              <h3>🎨 Gestion du contenu</h3>
              <p>Fonctionnalité à venir...</p>
            </div>
            
            <div className="admin-section-placeholder">
              <h3>📈 Analytics</h3>
              <p>Fonctionnalité à venir...</p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AdminPanel;
