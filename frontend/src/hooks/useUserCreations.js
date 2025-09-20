import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

// Fonction pour migrer les anciennes créations vers l'utilisateur Supabase actuel
async function attemptCreationsMigration(currentUserId) {
  try {
    console.log('🔄 FRIDAY: Tentative de migration des créations...');
    
    // Récupérer l'email de l'utilisateur actuel
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user?.email) {
      console.log('⚠️ FRIDAY: Pas d\'email utilisateur pour la migration');
      return;
    }
    
    const userEmail = session.user.email;
    console.log('📧 FRIDAY: Email utilisateur pour migration:', userEmail);
    
    // Chercher les créations avec ancien format basé sur l'email
    const emailHash = btoa(userEmail).slice(0, 10);
    const legacyUserId = `friday-user-${emailHash}`;
    
    console.log('🔍 FRIDAY: Recherche créations avec ancien ID:', legacyUserId);
    
    const { data: legacyCreations, error: legacyError } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', legacyUserId);
    
    if (legacyError) {
      console.error('❌ FRIDAY: Erreur recherche créations legacy:', legacyError);
      return;
    }
    
    if (legacyCreations && legacyCreations.length > 0) {
      console.log(`🔄 FRIDAY: ${legacyCreations.length} créations à migrer trouvées`);
      
      // Migrer chaque création vers le nouvel ID
      for (const creation of legacyCreations) {
        const { error: updateError } = await supabase
          .from('creations')
          .update({ user_id: currentUserId })
          .eq('id', creation.id);
          
        if (updateError) {
          console.error('❌ FRIDAY: Erreur migration création:', creation.id, updateError);
        }
      }
      
      console.log('✅ FRIDAY: Migration terminée');
    } else {
      console.log('ℹ️ FRIDAY: Aucune création legacy trouvée à migrer');
    }
    
  } catch (error) {
    console.error('❌ FRIDAY: Erreur critique migration:', error);
  }
}

export default function useUserCreations(userId) {
  const [creations, setCreations] = useState([]);
  const [loading, setLoading] = useState(false); // Commencer en false
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) {
      setCreations([]);
      setLoading(false);
      return;
    }

    // Ne charger les créations que quand on en a besoin (lazy loading)
    const fetchUserCreations = async () => {
      setLoading(true);
      try {
        console.log('📥 FRIDAY: Récupération créations pour userId:', userId);
        
        const { data, error: fetchError } = await supabase
          .from('creations')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        if (fetchError) {
          console.error('❌ FRIDAY: Erreur récupération créations:', fetchError);
          setError(fetchError.message);
          setCreations([]);
        } else {
          console.log('✅ FRIDAY: Créations récupérées:', data?.length || 0);
          setCreations(data || []);
          setError(null);
        }
      } catch (err) {
        console.error('❌ FRIDAY: Erreur critique récupération créations:', err);
        setError(err.message);
        setCreations([]);
      } finally {
        setLoading(false);
      }
    };

    // Charger uniquement si on a un userId
    console.log('🔍 FRIDAY: useUserCreations démarré pour userId:', userId);
    fetchUserCreations();
  }, [userId]);

  const refreshCreations = async () => {
    if (!userId) return;

    setLoading(true);
    try {
      const { data, error: fetchError } = await supabase
        .from('creations')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (fetchError) {
        setError(fetchError.message);
      } else {
        setCreations(data || []);
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { creations, loading, error, refreshCreations };
}
