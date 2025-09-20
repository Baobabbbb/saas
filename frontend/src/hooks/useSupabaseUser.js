import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

export default function useSupabaseUser() {
  // Essayer de récupérer l'utilisateur depuis le cache localStorage pour affichage ultra-rapide
  const [user, setUser] = useState(() => {
    try {
      const cachedUser = localStorage.getItem('friday_user_cache');
      if (cachedUser) {
        console.log('⚡ FRIDAY: Chargement cache utilisateur pour affichage immédiat');
        return JSON.parse(cachedUser);
      }
    } catch (error) {
      console.log('ℹ️ FRIDAY: Pas de cache utilisateur disponible');
    }
    return null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour gérer l'utilisateur connecté UNIQUEMENT via Supabase
    const getSupabaseUser = async () => {
      try {
        console.log('🔍 FRIDAY: Vérification session Supabase...');
        
        // Récupérer la session actuelle Supabase
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('❌ FRIDAY: Erreur session Supabase:', sessionError.message);
          setUser(null);
          setLoading(false);
          return;
        }

        if (session?.user) {
          console.log('✅ FRIDAY: Session Supabase active:', session.user.email);
          console.log('👤 FRIDAY: Données auth complètes:', {
            id: session.user.id,
            email: session.user.email,
            user_metadata: session.user.user_metadata,
            app_metadata: session.user.app_metadata
          });
          
          // D'abord créer l'utilisateur avec les données auth (chargement immédiat)
          const emailBase = session.user.email.split('@')[0];
          const baseUserData = {
            id: session.user.id,
            email: session.user.email,
            firstName: session.user.user_metadata?.firstName || session.user.user_metadata?.first_name || emailBase,
            lastName: session.user.user_metadata?.lastName || session.user.user_metadata?.last_name || '',
            name: session.user.user_metadata?.name || 
                  session.user.user_metadata?.full_name ||
                  `${session.user.user_metadata?.firstName || session.user.user_metadata?.first_name || emailBase} ${session.user.user_metadata?.lastName || session.user.user_metadata?.last_name || ''}`.trim(),
            user_metadata: session.user.user_metadata
          };
          
          console.log('👤 FRIDAY: Données utilisateur créées:', baseUserData);
          
          // Afficher immédiatement l'utilisateur et le mettre en cache
          setUser(baseUserData);
          setLoading(false);
          localStorage.setItem('friday_user_cache', JSON.stringify(baseUserData));
          
          // FORCER la récupération du profil - approche directe
          console.log('🚀 FRIDAY: DÉMARRAGE FORCÉ récupération profil...');
          fetchProfileData(session.user.id, baseUserData);
          
        } else {
          console.log('ℹ️ FRIDAY: Aucune session Supabase active');
          setUser(null);
        }
      } catch (error) {
        console.error('❌ FRIDAY: Erreur critique récupération utilisateur:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    // Fonction séparée pour récupérer le profil
    const fetchProfileData = async (userId, fallbackUserData) => {
      console.log('🔍 FRIDAY: Recherche profil pour ID:', userId);
      console.log('🔍 FRIDAY: Test simple - récupération de TOUS les profils...');
      
      try {
        // Test 1: récupérer tous les profils pour voir s'il y en a
        const { data: allProfiles, error: allError } = await supabase
          .from('profiles')
          .select('*')
          .limit(3);
        
        console.log('🔍 FRIDAY: Tous les profils:', allProfiles, 'erreur:', allError);
        
        // Test 2: récupérer le profil spécifique
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', userId)
          .single();

        console.log('🔍 FRIDAY: Profil spécifique recherché pour ID:', userId);
        console.log('🔍 FRIDAY: Résultat:', { profile, profileError });

        if (profile) {
          console.log('👤 FRIDAY: Profil trouvé en BDD:', profile);
          // Mettre à jour avec les données du profil
          const enhancedUserData = {
            ...fallbackUserData,
            firstName: profile.prenom || profile.first_name || fallbackUserData.firstName,
            lastName: profile.nom || profile.last_name || fallbackUserData.lastName,
            name: `${profile.prenom || profile.first_name || fallbackUserData.firstName} ${profile.nom || profile.last_name || fallbackUserData.lastName}`.trim(),
            profile: profile
          };
          
          console.log('👤 FRIDAY: Profil enrichi chargé:', enhancedUserData);
          setUser(enhancedUserData);
          localStorage.setItem('friday_user_cache', JSON.stringify(enhancedUserData));
        } else {
          console.log('ℹ️ FRIDAY: Aucun profil trouvé pour cet utilisateur');
        }
      } catch (error) {
        console.error('❌ FRIDAY: Erreur récupération profil:', error);
      }
    };

    // Initialiser
    getSupabaseUser();

    // Écouter les changements d'authentification Supabase
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔄 FRIDAY: Changement auth Supabase:', event, session?.user?.email || 'aucun utilisateur');
      
      if (event === 'SIGNED_IN' && session?.user) {
        console.log('✅ FRIDAY: Utilisateur connecté:', session.user.email);
        
        // Créer immédiatement l'utilisateur avec les données auth
        const baseUserData = {
          id: session.user.id,
          email: session.user.email,
          firstName: session.user.user_metadata?.firstName || session.user.email.split('@')[0],
          lastName: session.user.user_metadata?.lastName || '',
          name: session.user.user_metadata?.name || 
                `${session.user.user_metadata?.firstName || session.user.email.split('@')[0]} ${session.user.user_metadata?.lastName || ''}`.trim(),
          user_metadata: session.user.user_metadata
        };
        
        // Afficher immédiatement et mettre en cache
        setUser(baseUserData);
        setLoading(false);
        localStorage.setItem('friday_user_cache', JSON.stringify(baseUserData));
        
        // Enrichir avec le profil en arrière-plan
        try {
          const { data: profile, error: profileError } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();

          if (profileError && profileError.code !== 'PGRST116') {
            console.warn('⚠️ FRIDAY: Erreur récupération profil lors connexion:', profileError.message);
          }

          if (profile) {
            const enhancedUserData = {
              ...baseUserData,
              firstName: profile.first_name || baseUserData.firstName,
              lastName: profile.last_name || baseUserData.lastName,
              name: profile.full_name || `${profile.first_name || baseUserData.firstName} ${profile.last_name || baseUserData.lastName}`.trim(),
              profile: profile
            };
            setUser(enhancedUserData);
            localStorage.setItem('friday_user_cache', JSON.stringify(enhancedUserData));
          }
        } catch (error) {
          console.error('❌ FRIDAY: Erreur enrichissement profil (utilisateur reste connecté):', error);
        }
        
        // Nettoyer localStorage (migration complète vers Supabase)
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userName');
        localStorage.removeItem('userFirstName');
        localStorage.removeItem('userLastName');
        localStorage.removeItem('friday_supabase_user');
        
      } else if (event === 'SIGNED_OUT') {
        console.log('🚪 FRIDAY: Utilisateur déconnecté');
        setUser(null);
        setLoading(false);
        
        // Nettoyer localStorage
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userName');
        localStorage.removeItem('userFirstName');
        localStorage.removeItem('userLastName');
        localStorage.removeItem('friday_supabase_user');
        localStorage.removeItem('friday_user_cache');
        
      } else if (event === 'TOKEN_REFRESHED') {
        console.log('🔄 FRIDAY: Token Supabase rafraîchi');
        // Garder l'utilisateur actuel
        
      } else {
        console.log('ℹ️ FRIDAY: Événement auth Supabase:', event);
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  return { user, loading };
}