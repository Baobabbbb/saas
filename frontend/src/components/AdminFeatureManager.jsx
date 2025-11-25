import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { getFeatures, updateFeature, resetFeatures } from '../services/adminFeatures';
import { getUsers, deleteUser } from '../services/adminUsers';
import './AdminFeatureManager.css';

const FeatureManager = () => {
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);
  const [selectedTab, setSelectedTab] = useState('features');
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState(null);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadUsers = useCallback(async () => {
    try {
      setUsersLoading(true);
      setUsersError(null);
      const usersData = await getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs:', error);
      setUsersError('Erreur lors du chargement des utilisateurs');
      showNotification('Erreur lors du chargement des utilisateurs', 'error');
    } finally {
      setUsersLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedTab === 'users') {
      loadUsers();
    }
  }, [selectedTab, loadUsers]);

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur et toutes ses créations ? Cette action est irréversible.')) {
      return;
    }

    try {
      await deleteUser(userId);
      showNotification('Utilisateur et toutes ses créations supprimés avec succès', 'success');
      // Recharger la liste des utilisateurs
      await loadUsers();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      showNotification('Erreur lors de la suppression de l\'utilisateur', 'error');
    }
  };

  const loadFeatures = async () => {
    try {
      setLoading(true);
      const featuresData = await getFeatures();
      setFeatures(featuresData);
    } catch (error) {
      console.error('Erreur lors du chargement des fonctionnalités:', error);
      showNotification('Erreur lors du chargement des fonctionnalités', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFeature = async (featureKey) => {
    try {
      const currentEnabled = features[featureKey]?.enabled || false;
      const updatedFeatures = await updateFeature(featureKey, !currentEnabled);
      
      if (updatedFeatures) {
        setFeatures(updatedFeatures);
        
        // Déclencher un événement pour mettre à jour Herbbie
        window.dispatchEvent(new CustomEvent('featuresUpdated', { detail: updatedFeatures }));
        
        const status = !currentEnabled ? 'activée' : 'désactivée';
        showNotification(`Fonctionnalité ${features[featureKey]?.name} ${status}`, 'success');
      } else {
        showNotification('Erreur lors de la mise à jour', 'error');
      }
    } catch (error) {
      console.error('Erreur lors de la mise à jour:', error);
      showNotification('Erreur lors de la mise à jour', 'error');
    }
  };

  const handleResetFeatures = async () => {
    try {
      const resetFeaturesData = await resetFeatures();
      if (resetFeaturesData) {
        setFeatures(resetFeaturesData);
        
        // Déclencher un événement pour mettre à jour Herbbie
        window.dispatchEvent(new CustomEvent('featuresUpdated', { detail: resetFeaturesData }));
        
        showNotification('Toutes les fonctionnalités ont été réinitialisées', 'success');
      } else {
        showNotification('Erreur lors de la réinitialisation', 'error');
      }
    } catch (error) {
      console.error('Erreur lors de la réinitialisation:', error);
      showNotification('Erreur lors de la réinitialisation', 'error');
    }
  };

  const getEnabledCount = () => {
    return Object.values(features).filter(feature => feature.enabled).length;
  };

  const getTotalCount = () => {
    return Object.keys(features).length;
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="admin-loading-spinner"></div>
        <span>Chargement des fonctionnalités...</span>
      </div>
    );
  }

  return (
    <div className="feature-manager-container">
      {/* Notification */}
      {notification && (
        <motion.div
          className={`admin-notification ${notification.type} show`}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 100 }}
        >
          {notification.message}
        </motion.div>
      )}

      {/* Onglets de navigation */}
      <div className="admin-tab-bar">
        <button
          className={`admin-tab ${selectedTab === 'features' ? 'active' : ''}`}
          onClick={() => setSelectedTab('features')}
        >
          Fonctionnalités
        </button>
        <button
          className={`admin-tab ${selectedTab === 'users' ? 'active' : ''}`}
          onClick={() => setSelectedTab('users')}
        >
          Utilisateurs
        </button>
      </div>

      {/* Contenu de l'onglet Fonctionnalités */}
      {selectedTab === 'features' && (
        <>
          {/* Header avec statistiques */}
          <div className="feature-manager-header">
        <div className="feature-manager-stats">
          <div className="feature-stat">
            <span className="feature-stat-number">{getEnabledCount()}</span>
            <span className="feature-stat-label">Activées</span>
          </div>
          <div className="feature-stat">
            <span className="feature-stat-number">{getTotalCount()}</span>
            <span className="feature-stat-label">Total</span>
          </div>
          <div className="feature-stat">
            <span className="feature-stat-number">
              {Math.round((getEnabledCount() / getTotalCount()) * 100)}%
            </span>
            <span className="feature-stat-label">Taux d'activation</span>
          </div>
        </div>
        
        <div className="feature-manager-actions">
          <button 
            className="admin-btn admin-btn-secondary"
            onClick={handleResetFeatures}
          >
            🔄 Réinitialiser
          </button>
        </div>
      </div>

      {/* Grille des fonctionnalités */}
      <div className="feature-manager-grid">
        {Object.entries(features).map(([key, feature]) => (
          <motion.div
            key={key}
            className="feature-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="feature-card-header">
              <div className="feature-info">
                <span className="feature-icon">{getFeatureIcon(key)}</span>
                <div className="feature-details">
                  <h3 className="feature-name">{feature.name}</h3>
                  <span className={`feature-status ${feature.enabled ? 'enabled' : 'disabled'}`}>
                    {feature.enabled ? 'Activée' : 'Désactivée'}
                  </span>
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
            
            <div className="feature-card-body">
              <p className="feature-description">
                {getFeatureDescription(key)}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

          {/* Informations supplémentaires */}
          <div className="feature-manager-info">
            <div className="admin-card">
              <div className="admin-card-header">
                <h3>📋 Informations</h3>
              </div>
              <div className="admin-card-body">
                <p>
                  Les fonctionnalités activées sont visibles pour tous les utilisateurs de HERBBIE. 
                  Les modifications sont appliquées immédiatement.
                </p>
                <ul className="feature-info-list">
                  <li>🎬 <strong>Dessin animé</strong> : Génération de vidéos animées</li>
                  <li>💬 <strong>Bande dessinée</strong> : Création de BD avec bulles</li>
                  <li>🎨 <strong>Coloriage</strong> : Pages de coloriage à imprimer</li>
                  <li>📖 <strong>Histoire</strong> : Contes audio avec narration</li>
                  <li>🎵 <strong>Comptine</strong> : Chansons avec musique générée</li>
                </ul>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Contenu de l'onglet Utilisateurs */}
      {selectedTab === 'users' && (
        <div className="admin-users-panel">
          <div className="admin-users-header">
            <h2>👥 Gestion des utilisateurs</h2>
            <p>Liste de tous les utilisateurs enregistrés dans HERBBIE</p>
          </div>

          {usersLoading ? (
            <div className="admin-loading">
              <div className="admin-loading-spinner"></div>
              <span>Chargement des utilisateurs...</span>
            </div>
          ) : usersError ? (
            <div className="admin-error">
              <p>{usersError}</p>
            </div>
          ) : users.length === 0 ? (
            <div className="admin-empty">
              <p>Aucun utilisateur trouvé</p>
            </div>
          ) : (
            <div className="admin-users-table-container">
              <table className="admin-users-table">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Rôle</th>
                    <th>Date d'inscription</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>
                        {user.prenom || user.nom 
                          ? `${user.prenom || ''} ${user.nom || ''}`.trim() 
                          : 'Non renseigné'}
                      </td>
                      <td>{user.email || 'N/A'}</td>
                      <td>
                        <span className={`user-role ${user.role === 'admin' ? 'admin' : user.role === 'free' ? 'free' : 'user'}`}>
                          {user.role === 'admin' ? '👑 Admin' : user.role === 'free' ? '🆓 Gratuit' : '👤 Utilisateur'}
                        </span>
                      </td>
                      <td>
                        {user.created_at 
                          ? new Date(user.created_at).toLocaleDateString('fr-FR', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })
                          : 'N/A'}
                      </td>
                      <td>
                        <button
                          className="delete-user-btn"
                          onClick={() => handleDeleteUser(user.id)}
                          title="Supprimer l'utilisateur et toutes ses créations"
                        >
                          🗑️ Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Fonction pour obtenir les icônes des fonctionnalités
const getFeatureIcon = (featureKey) => {
  const icons = {
    animation: "🎬",
    comic: "💬",
    coloring: "🎨",
    audio: "📖",
    rhyme: "🎵"
  };
  
  return icons[featureKey] || "📋";
};

// Fonction pour obtenir les descriptions des fonctionnalités
const getFeatureDescription = (featureKey) => {
  const descriptions = {
    animation: "Génération de dessins animés personnalisés avec IA",
    comic: "Création de bandes dessinées avec bulles de dialogue",
    coloring: "Pages de coloriage à imprimer pour les enfants",
    audio: "Histoires audio avec narration automatique",
    rhyme: "Comptines musicales avec paroles et mélodies"
  };
  
  return descriptions[featureKey] || "Fonctionnalité de création de contenu";
};

export default FeatureManager; 