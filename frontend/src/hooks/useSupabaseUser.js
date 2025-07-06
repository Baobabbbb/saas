import { useEffect, useState } from "react";
import { supabase } from "../supabaseClient";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour synchroniser les données utilisateur avec localStorage
    const syncUserData = async (user) => {
      try {
        if (user) {
          localStorage.setItem('userEmail', user.email);
          
          // Récupérer le profil utilisateur pour obtenir le nom
          const { data: profile, error } = await supabase
            .from('profiles')
            .select('prenom, nom')
            .eq('id', user.id)
            .single();
          
          console.log('Profile data:', profile, 'Error:', error); // Debug
          
          if (profile && profile.prenom) {
            localStorage.setItem('userName', `${profile.prenom} ${profile.nom}`);
            localStorage.setItem('userFirstName', profile.prenom);
            console.log('Stored firstName:', profile.prenom); // Debug
          } else {
            // Cas spécial pour l'admin si pas de profil
            if (user.email === 'fredagathe77@gmail.com') {
              // Créer ou mettre à jour le profil admin avec un prénom par défaut
              const adminFirstName = 'Freda';
              const adminLastName = 'Gathe';
              
              const { error: upsertError } = await supabase
                .from('profiles')
                .upsert([{ 
                  id: user.id, 
                  prenom: adminFirstName, 
                  nom: adminLastName 
                }]);
              
              if (!upsertError) {
                localStorage.setItem('userName', `${adminFirstName} ${adminLastName}`);
                localStorage.setItem('userFirstName', adminFirstName);
                console.log('Created admin profile with firstName:', adminFirstName);
              } else {
                console.error('Error creating admin profile:', upsertError);
                const fallbackName = user.email.split('@')[0];
                localStorage.setItem('userName', fallbackName);
                localStorage.setItem('userFirstName', fallbackName);
              }
            } else {
              // Fallback pour les autres utilisateurs
              const fallbackName = user.email.split('@')[0];
              localStorage.setItem('userName', fallbackName);
              localStorage.setItem('userFirstName', fallbackName);
              console.log('Using fallback name:', fallbackName); // Debug
            }
          }
        } else {
          // Utilisateur déconnecté - nettoyer localStorage
          localStorage.removeItem('userEmail');
          localStorage.removeItem('userName');
          localStorage.removeItem('userFirstName');
        }
      } catch (error) {
        console.warn('Supabase user sync error (non-critical):', error);
        // En cas d'erreur Supabase, utiliser des valeurs par défaut
        if (user) {
          const fallbackName = user.email.split('@')[0];
          localStorage.setItem('userEmail', user.email);
          localStorage.setItem('userName', fallbackName);
          localStorage.setItem('userFirstName', fallbackName);
        }
      }
    };

    // Initialisation de l'utilisateur avec gestion d'erreur
    const initializeUser = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        setUser(user);
        await syncUserData(user);
        setLoading(false);
      } catch (error) {
        console.warn('Supabase initialization error (non-critical):', error);
        setUser(null);
        setLoading(false);
      }
    };

    initializeUser();

    // Listener pour les changements d'authentification avec gestion d'erreur
    let authListener;
    try {
      const { data: listener } = supabase.auth.onAuthStateChange(async (_event, session) => {
        try {
          const currentUser = session?.user || null;
          setUser(currentUser);
          await syncUserData(currentUser);
          setLoading(false);
        } catch (error) {
          console.warn('Auth state change error (non-critical):', error);
          setUser(session?.user || null);
          setLoading(false);
        }
      });
      authListener = listener;
    } catch (error) {
      console.warn('Auth listener setup error (non-critical):', error);
      setLoading(false);
    }

    return () => {
      try {
        authListener?.subscription?.unsubscribe();
      } catch (error) {
        console.warn('Auth listener cleanup error (non-critical):', error);
      }
    };
  }, []);

  return { user, loading };
}
