import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

export default function useUserCreations(userId) {
  const [creations, setCreations] = useState([]);
  const [loading, setLoading] = useState(true); // Commencer en true pour affichage immédiat
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
        console.log('📥 FRIDAY: Récupération créations utilisateur:', userId);
        
        const { data, error: fetchError } = await supabase
          .from('creations')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        if (fetchError) {
          console.error('❌ FRIDAY: Erreur récupération créations:', fetchError);
          setError(fetchError.message);
        } else {
          console.log('✅ FRIDAY: Créations récupérées:', data?.length || 0);
          setCreations(data || []);
          setError(null);
        }
      } catch (err) {
        console.error('❌ FRIDAY: Erreur critique récupération créations:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // Charger uniquement si on a un userId
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
