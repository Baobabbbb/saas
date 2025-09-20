import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

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
        console.log('📥 FRIDAY: Récupération créations utilisateur:', userId);
        
        console.log('🔍 FRIDAY: Requête Supabase pour user_id:', userId);
        const { data, error: fetchError, count } = await supabase
          .from('creations')
          .select('*', { count: 'exact' })
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        console.log('📊 FRIDAY: Résultat requête Supabase:', {
          data: data,
          count: count,
          error: fetchError,
          userId: userId
        });

        // Vérification supplémentaire : compter TOUTES les créations
        const { count: totalCount } = await supabase
          .from('creations')
          .select('*', { count: 'exact', head: true });
        
        console.log('🔢 FRIDAY: Nombre total de créations dans la base:', totalCount);
        
        // Vérification : quelques créations pour voir les user_id existants
        const { data: sampleCreations } = await supabase
          .from('creations')
          .select('user_id, type, title, created_at')
          .limit(5)
          .order('created_at', { ascending: false });
          
        console.log('🔍 FRIDAY: Échantillon créations existantes:', sampleCreations);

        if (fetchError) {
          console.error('❌ FRIDAY: Erreur récupération créations:', fetchError);
          setError(fetchError.message);
        } else {
          console.log('✅ FRIDAY: Créations récupérées:', data?.length || 0, 'pour user_id:', userId);
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
