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
        console.log('📥 FRIDAY: Récupération créations utilisateur:', userId);
        
        // Test simple : compter toutes les créations d'abord
        console.log('🧪 FRIDAY: Test connexion base - comptage total...');
        const testResult = await supabase
          .from('creations')
          .select('*', { count: 'exact', head: true });
        
        console.log('🧪 FRIDAY: Test résultat:', {
          count: testResult.count,
          error: testResult.error
        });
        
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

        // Si pas de créations trouvées, faire des vérifications simples
        if (!data || data.length === 0) {
          console.log('🔍 FRIDAY: Aucune création pour cet utilisateur, vérifications...');
          
          try {
            // Compter toutes les créations
            const { count: totalCount, error: countError } = await supabase
              .from('creations')
              .select('*', { count: 'exact', head: true });
            
            console.log('🔢 FRIDAY: Total créations base:', totalCount, 'erreur:', countError);
            
            // Récupérer quelques exemples
            const { data: samples, error: samplesError } = await supabase
              .from('creations')
              .select('user_id, type, title')
              .limit(3);
              
            console.log('🔍 FRIDAY: Échantillons:', samples, 'erreur:', samplesError);
            
          } catch (err) {
            console.error('❌ FRIDAY: Erreur vérifications:', err);
          }
        }

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
