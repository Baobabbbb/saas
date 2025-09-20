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
        try {
          const { count: totalCount } = await supabase
            .from('creations')
            .select('*', { count: 'exact', head: true });
          
          console.log('🔢 FRIDAY: Nombre total de créations dans la base:', totalCount);
          
          // Vérification : quelques créations pour voir les user_id existants
          const { data: sampleCreations } = await supabase
            .from('creations')
            .select('user_id, type, title, created_at')
            .limit(10)
            .order('created_at', { ascending: false });
            
          console.log('🔍 FRIDAY: Échantillon créations existantes:', sampleCreations);
          
          // Recherche de créations avec des patterns d'anciens user_id
          const { data: legacyCreations } = await supabase
            .from('creations')
            .select('user_id, type, title, created_at')
            .like('user_id', 'friday-%')
            .limit(5);
            
          console.log('🔍 FRIDAY: Créations avec ancien format user_id:', legacyCreations);
          
        } catch (debugError) {
          console.error('❌ FRIDAY: Erreur diagnostics:', debugError);
        }

        if (fetchError) {
          console.error('❌ FRIDAY: Erreur récupération créations:', fetchError);
          setError(fetchError.message);
        } else {
          console.log('✅ FRIDAY: Créations récupérées:', data?.length || 0, 'pour user_id:', userId);
          
          // Si aucune création trouvée avec l'ID Supabase, chercher les anciennes créations à migrer
          if ((!data || data.length === 0) && userId) {
            console.log('🔄 FRIDAY: Aucune création trouvée, recherche de créations à migrer...');
            await attemptCreationsMigration(userId);
            
            // Nouvelle tentative après migration
            const { data: migratedData } = await supabase
              .from('creations')
              .select('*')
              .eq('user_id', userId)
              .order('created_at', { ascending: false });
              
            if (migratedData && migratedData.length > 0) {
              console.log('✅ FRIDAY: Créations migrées récupérées:', migratedData.length);
              setCreations(migratedData);
            } else {
              setCreations(data || []);
            }
          } else {
            setCreations(data || []);
          }
          
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
