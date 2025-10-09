import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import AdminLogin from '../components/AdminLogin';
import AdminFeatureManager from '../components/AdminFeatureManager';

const AdminContent = () => {
  const { user, isAdmin, loading, signOut } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const autoAuth = searchParams.get('auth');
  const [autoAuthGranted, setAutoAuthGranted] = React.useState(false);

  // Gestion de l'auto-authentification
  useEffect(() => {
    // Si paramètre auth=auto, accorder l'accès automatiquement
    if (autoAuth === 'auto') {
      setAutoAuthGranted(true);
      
      // Retirer le paramètre auth de l'URL SANS redéclencher le useEffect
      window.history.replaceState({}, '', '/admin');
    } 
    // Si pas d'auto-auth ET pas déjà accordé, nettoyer
    else if (!autoAuth && !autoAuthGranted) {
      localStorage.removeItem('herbbie_admin_session');
    }
  }, [autoAuth]);

  // Changer le titre de l'onglet pour l'administration
  useEffect(() => {
    const originalTitle = document.title;
    document.title = 'HERBBIE - Administration';

    return () => {
      // Restaurer le titre original en quittant la page
      document.title = originalTitle;
    };
  }, []);

  // Nettoyer l'auto-auth quand on quitte la page
  useEffect(() => {
    const handleBeforeUnload = () => {
      setAutoAuthGranted(false);
      localStorage.removeItem('herbbie_admin_session');
      // Restaurer le titre original
      document.title = 'HERBBIE';
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  if (loading && !autoAuthGranted) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <div>Chargement...</div>
      </div>
    );
  }

  // Si auto-auth accordé, bypasser la vérification normale
  // OU si connecté normalement avec user et isAdmin
  const hasAccess = autoAuthGranted || (user && isAdmin);

  // Si pas d'accès, afficher le formulaire de connexion
  if (!hasAccess) {
    return <AdminLogin />;
  }

  // Si connecté, afficher le panneau d'administration
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
          textAlign: 'center',
          display: 'flex',
          gap: '15px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <a 
            href="/" 
            onClick={(e) => {
              e.preventDefault();
              // Nettoyer la session avant de partir
              localStorage.removeItem('herbbie_admin_session');
              window.location.href = '/';
            }}
            style={{ 
              color: 'white', 
              textDecoration: 'none',
              padding: '12px 30px',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '25px',
              display: 'inline-block',
              transition: 'all 0.3s ease',
              cursor: 'pointer'
            }}
          >
            ← Retour à Herbbie
          </a>
          <button
            onClick={async () => {
              await signOut();
              // Nettoyer complètement la session
              localStorage.removeItem('herbbie_admin_session');
              navigate('/admin');
            }}
            style={{ 
              color: 'white', 
              border: 'none',
              padding: '12px 30px',
              background: 'rgba(255,0,0,0.3)',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500',
              transition: 'all 0.3s ease'
            }}
          >
            🚪 Déconnexion
          </button>
        </div>
      </div>
    </div>
  );
};

const Admin = () => {
  return (
    <AuthProvider>
      <AdminContent />
    </AuthProvider>
  );
};

export default Admin;
