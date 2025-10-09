import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";
import { syncUserProfile } from "../services/profileService";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour récupérer utilisateur et profil
    const loadUserData = async () => {
      try {
        // 1. Récupérer la session
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session?.user) {
          setUser(null);
          setLoading(false);
          return;
        }
        
        // 2. Synchroniser le profil (email et last_login)
        try {
          await syncUserProfile(session.user);
        } catch (syncError) {
          console.warn('Erreur sync profil (non critique):', syncError);
          // Ne pas bloquer le chargement si la sync échoue
        }

        // 3. Créer utilisateur de base
        const emailName = session.user.email.split('@')[0];
        const baseUser = {
          id: session.user.id,
          email: session.user.email,
          firstName: emailName,
          lastName: '',
          name: emailName
        };

        // 4. Récupération profil
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single();

        if (profile) {
          const enrichedUser = {
            ...baseUser,
            firstName: profile.prenom || baseUser.firstName,
            lastName: profile.nom || '',
            name: `${profile.prenom || baseUser.firstName} ${profile.nom || ''}`.trim(),
            profile: profile
          };
          setUser(enrichedUser);
        } else {
          setUser(baseUser);
        }

      } catch (error) {
        console.error('Erreur chargement utilisateur:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();

    // Écouter les changements d'authentification
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN') {
        loadUserData();
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
        setLoading(false);
      }
    });

    return () => subscription?.unsubscribe();
  }, []);

  return { user, loading };
}