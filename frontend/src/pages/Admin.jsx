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
      window.history.replaceState({}, '', '/ilmysv6iepwepoa4tj2k');
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
        background: '#F9F4FF',
        color: '#333333'
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
      background: '#F9F4FF',
      padding: '40px 20px'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ 
          color: '#333333', 
          textAlign: 'center', 
          marginBottom: '40px',
          fontSize: '2.5em',
          fontFamily: "'Baloo 2', cursive",
          fontWeight: '700'
        }}>
          ⚙️ Gestion des Fonctionnalités HERBBIE
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
              window.location.href = '/';
            }}
            style={{ 
              color: '#6B4EFF', 
              textDecoration: 'none',
              padding: '12px 30px',
              background: '#FFFFFF',
              border: '2px solid #6B4EFF',
              borderRadius: '12px',
              display: 'inline-block',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              fontFamily: "'Baloo 2', cursive",
              fontWeight: '600',
              fontSize: '16px'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#6B4EFF';
              e.target.style.color = '#FFFFFF';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#FFFFFF';
              e.target.style.color = '#6B4EFF';
            }}
          >
            ← Retour à HERBBIE
          </a>
          <button
            onClick={async () => {
              await signOut();
              localStorage.removeItem('herbbie_admin_session');
              navigate('/ilmysv6iepwepoa4tj2k');
            }}
            style={{ 
              color: '#FFFFFF', 
              border: 'none',
              padding: '12px 30px',
              background: '#FF85A1',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              fontFamily: "'Baloo 2', cursive"
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#ff6b8a';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#FF85A1';
              e.target.style.transform = 'translateY(0)';
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
