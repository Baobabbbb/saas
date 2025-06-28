import React from 'react';
import { motion } from 'framer-motion';
import './CustomRequest.css';

const CustomRequest = ({ customRequest, setCustomRequest }) => {
  return (
    <div className="custom-request">
      <h3>5. Demandes spécifiques (optionnel)</h3>
      
      <div className="request-form">
        <div className="input-group">
          <label htmlFor="customRequest">Avez-vous des demandes particulières ?</label>
          <motion.textarea
            id="customRequest"
            value={customRequest}
            onChange={(e) => setCustomRequest(e.target.value)}
            placeholder="Ex: En anglais, avec un chien bleu, inclure un message sur l'amitié..."
            rows={3}
            whileFocus={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
        </div>
      </div>
    </div>
  );
};

export default CustomRequest;
