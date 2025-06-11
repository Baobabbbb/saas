import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AnimationViewer from './AnimationViewer';
import './AnimationPopup.css';

const AnimationPopup = ({ animation, isOpen, onClose }) => {
  if (!isOpen || !animation) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="animation-popup-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="animation-popup-content"
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 50 }}
          transition={{ type: "spring", damping: 20, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="animation-popup-background" />
          
          <div className="animation-popup-container">
            <AnimationViewer 
              animation={animation} 
              onClose={onClose}
            />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AnimationPopup;
