import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
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
          
          // D'abord créer l'utilisateur avec les données auth (chargement immédiat)
          const baseUserData = {
            id: session.user.id,
            email: session.user.email,
            firstName: session.user.user_metadata?.firstName || session.user.email.split('@')[0],
            lastName: session.user.user_metadata?.lastName || '',
            name: session.user.user_metadata?.name || 
                  `${session.user.user_metadata?.firstName || session.user.email.split('@')[0]} ${session.user.user_metadata?.lastName || ''}`.trim(),
            user_metadata: session.user.user_metadata
          };
          
          // Afficher immédiatement l'utilisateur
          setUser(baseUserData);
          setLoading(false);
          
          // Puis récupérer les données du profil en arrière-plan
          try {
            const { data: profile, error: profileError } = await supabase
              .from('profiles')
              .select('*')
              .eq('id', session.user.id)
              .single();

            if (profileError && profileError.code !== 'PGRST116') { // PGRST116 = pas de résultat
              console.warn('⚠️ FRIDAY: Erreur récupération profil:', profileError.message);
            }

            if (profile) {
              // Mettre à jour avec les données du profil
              const enhancedUserData = {
                ...baseUserData,
                firstName: profile.first_name || baseUserData.firstName,
                lastName: profile.last_name || baseUserData.lastName,
                name: profile.full_name || `${profile.first_name || baseUserData.firstName} ${profile.last_name || baseUserData.lastName}`.trim(),
                profile: profile
              };
              
              console.log('👤 FRIDAY: Profil enrichi chargé:', enhancedUserData);
              setUser(enhancedUserData);
            }
          } catch (error) {
            console.error('❌ FRIDAY: Erreur chargement profil (fallback sur auth):', error);
            // L'utilisateur reste avec les données auth
          }
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
        
        // Afficher immédiatement
        setUser(baseUserData);
        setLoading(false);
        
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