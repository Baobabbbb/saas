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

  // Nettoyer la session au chargement SAUF si autoAuth est présent
  useEffect(() => {
    if (!autoAuth) {
      // Pas d'auto-auth = accès direct, donc nettoyer toute session existante
      localStorage.removeItem('herbbie_admin_session');
      console.log('🧹 Session admin nettoyée (accès direct)');
    }
  }, []); // Exécuté une seule fois au montage

  // Si paramètre auth=auto (venant du bouton Herbbie), auto-authentifier
  useEffect(() => {
    if (autoAuth === 'auto' && !user) {
      // Créer une session admin automatique TEMPORAIRE (valide 5 minutes)
      const adminSession = {
        user: { email: 'admin@herbbie.com', id: 'auto-admin' },
        isAdmin: true,
        session: { expires_at: Date.now() + (5 * 60 * 1000) } // 5 minutes seulement
      };
      localStorage.setItem('herbbie_admin_session', JSON.stringify(adminSession));
      
      // Retirer le paramètre auth de l'URL et recharger
      navigate('/admin', { replace: true });
      window.location.reload();
    }
  }, [autoAuth, user, navigate]);

  // Nettoyer la session quand on quitte la page
  useEffect(() => {
    const handleBeforeUnload = () => {
      localStorage.removeItem('herbbie_admin_session');
      console.log('🧹 Session admin nettoyée (fermeture de page)');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  if (loading) {
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

  // Si pas connecté et pas d'auto-auth, afficher le formulaire de connexion
  if (!user || !isAdmin) {
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
