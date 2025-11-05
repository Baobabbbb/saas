import React, { useState, useEffect } from 'react';
import { getFeatures, updateFeature } from '../services/features';
import './FeatureManager.css';

const FeatureManager = () => {
  const [features, setFeatures] = useState({});

  useEffect(() => {
    setFeatures(getFeatures());
  }, []);

  const handleToggleFeature = (featureKey) => {
    const currentEnabled = features[featureKey]?.enabled || false;
    const updatedFeatures = updateFeature(featureKey, !currentEnabled);
    setFeatures(updatedFeatures);
  };

  return (
    <div className="feature-manager">
      <h3>Gestion des fonctionnalités</h3>
      <p className="feature-manager-description">
        Activez ou désactivez les fonctionnalités disponibles sur le site
      </p>
      
      <div className="features-grid">
        {Object.entries(features).map(([key, feature]) => (
          <div key={key} className="feature-item">
            <div className="feature-info">
              <span className="feature-icon">{feature.icon}</span>
              <div className="feature-details">
                <h4>{feature.name}</h4>
                <p className={`feature-status ${feature.enabled ? 'enabled' : 'disabled'}`}>
                  {feature.enabled ? 'Activé' : 'Désactivé'}
                </p>
              </div>
            </div>
            
            <label className="feature-toggle">
              <input
                type="checkbox"
                checked={feature.enabled}
                onChange={() => handleToggleFeature(key)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeatureManager;
