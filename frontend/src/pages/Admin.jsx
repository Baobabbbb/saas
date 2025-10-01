import React from 'react';
import AdminFeatureManager from '../components/AdminFeatureManager';

const Admin = () => {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ 
          color: 'white', 
          textAlign: 'center', 
          marginBottom: '40px',
          fontSize: '2.5em'
        }}>
          ⚙️ Gestion des Fonctionnalités Herbbie
        </h1>
        
        <AdminFeatureManager />
        
        <div style={{ 
          marginTop: '40px', 
          textAlign: 'center' 
        }}>
          <a 
            href="/" 
            style={{ 
              color: 'white', 
              textDecoration: 'none',
              padding: '12px 30px',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '25px',
              display: 'inline-block',
              transition: 'all 0.3s ease'
            }}
          >
            ← Retour à Herbbie
          </a>
        </div>
      </div>
    </div>
  );
};

export default Admin;
