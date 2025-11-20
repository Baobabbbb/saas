import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

// Fonction pour migrer les anciennes créations vers l'utilisateur Supabase actuel
async function attemptCreationsMigration(currentUserId) {
  try {
    
    // Récupérer l'email de l'utilisateur actuel
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user?.email) {
      return;
    }
    
    const userEmail = session.user.email;
    
    // Chercher les créations avec ancien format basé sur l'email
    const emailHash = btoa(userEmail).slice(0, 10);
    const legacyUserId = `friday-user-${emailHash}`;
    
    
    const { data: legacyCreations, error: legacyError } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', legacyUserId);
    
    if (legacyError) {
      console.error('❌ HERBBIE: Erreur recherche créations legacy:', legacyError);
      return;
    }
    
    if (legacyCreations && legacyCreations.length > 0) {
      
      // Migrer chaque création vers le nouvel ID
      for (const creation of legacyCreations) {
        const { error: updateError } = await supabase
          .from('creations')
          .update({ user_id: currentUserId })
          .eq('id', creation.id);
          
        if (updateError) {
          console.error('❌ HERBBIE: Erreur migration création:', creation.id, updateError);
        }
      }
      
    } else {
    }
    
  } catch (error) {
    console.error('❌ HERBBIE: Erreur critique migration:', error);
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
        const { data, error: fetchError } = await supabase
          .from('creations')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        if (fetchError) {
          console.error('Erreur récupération créations:', fetchError);
          setError(fetchError.message);
          setCreations([]);
        } else {
          setCreations(data || []);
          setError(null);
        }
      } catch (err) {
        console.error('Erreur critique récupération créations:', err);
        setError(err.message);
        setCreations([]);
      } finally {
        setLoading(false);
      }
    };
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
