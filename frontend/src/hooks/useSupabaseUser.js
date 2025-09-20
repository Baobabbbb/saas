import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction SIMPLE pour récupérer utilisateur et profil
    const loadUserData = async () => {
      console.log('🚀 FRIDAY: Démarrage chargement utilisateur...');
      
      try {
        // 1. Récupérer la session
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session?.user) {
          console.log('ℹ️ FRIDAY: Pas de session active');
          setUser(null);
          setLoading(false);
          return;
        }

        console.log('✅ FRIDAY: Session active:', session.user.email);
        
        // 2. Créer utilisateur de base
        const emailName = session.user.email.split('@')[0];
        const baseUser = {
          id: session.user.id,
          email: session.user.email,
          firstName: emailName,
          lastName: '',
          name: emailName
        };

        // 3. FORCER récupération profil
        console.log('🔍 FRIDAY: RECHERCHE PROFIL FORCÉE...');
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single();

        console.log('📋 FRIDAY: Résultat profil:', { profile, error });

        if (profile) {
          const enrichedUser = {
            ...baseUser,
            firstName: profile.prenom || baseUser.firstName,
            lastName: profile.nom || '',
            name: `${profile.prenom || baseUser.firstName} ${profile.nom || ''}`.trim(),
            profile: profile
          };
          console.log('✅ FRIDAY: Utilisateur enrichi:', enrichedUser);
          setUser(enrichedUser);
        } else {
          console.log('⚠️ FRIDAY: Profil non trouvé, utilisation données de base');
          setUser(baseUser);
        }

      } catch (error) {
        console.error('❌ FRIDAY: Erreur chargement:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();

    // Écouter les changements d'authentification
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔄 FRIDAY: Auth change:', event);
      
      if (event === 'SIGNED_IN') {
        loadUserData(); // Recharger les données
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
        setLoading(false);
      }
    });

    return () => subscription?.unsubscribe();
  }, []);

  return { user, loading };
}