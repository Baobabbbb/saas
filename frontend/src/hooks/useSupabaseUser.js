import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour créer/récupérer un utilisateur Supabase
    const initializeUser = async () => {
      try {
        // 1. Vérifier s'il y a déjà une session Supabase
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (session?.user) {
          console.log('✅ Session Supabase trouvée:', session.user.email);
          setUser({
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.name || session.user.email.split('@')[0],
            firstName: session.user.user_metadata?.firstName || session.user.email.split('@')[0]
          });
          setLoading(false);
          return;
        }

        // 2. Récupérer les données localStorage (migration)
        const userEmail = localStorage.getItem('userEmail');
        const userName = localStorage.getItem('userName');
        const userFirstName = localStorage.getItem('userFirstName');

        if (userEmail && userEmail.trim()) {
          console.log('🔄 Migration localStorage vers Supabase:', userEmail);
          
          // 3. Créer un compte Supabase avec un mot de passe temporaire
          const tempPassword = 'FridayTemp' + Date.now();
          
          const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
            email: userEmail.trim(),
            password: tempPassword,
            options: {
              data: {
                name: userName || userEmail.split('@')[0],
                firstName: userFirstName || userEmail.split('@')[0],
                source: 'friday_migration'
              }
            }
          });

          if (signUpError && signUpError.message.includes('already registered')) {
            // 4. Si l'utilisateur existe déjà, se connecter
            console.log('👤 Utilisateur existe, tentative de connexion...');
            
            // Créer une session factice pour cet utilisateur
            const userData = {
              id: 'friday-user-' + btoa(userEmail).slice(0, 10),
              email: userEmail.trim(),
              name: userName || userEmail.split('@')[0],
              firstName: userFirstName || userEmail.split('@')[0]
            };
            
            setUser(userData);
            
            // Stocker dans la session Supabase (hack pour la persistence)
            localStorage.setItem('friday_supabase_user', JSON.stringify(userData));
            
          } else if (signUpData?.user) {
            console.log('✅ Nouveau compte Supabase créé:', signUpData.user.email);
            setUser({
              id: signUpData.user.id,
              email: signUpData.user.email,
              name: signUpData.user.user_metadata?.name || signUpData.user.email.split('@')[0],
              firstName: signUpData.user.user_metadata?.firstName || signUpData.user.email.split('@')[0]
            });
          } else {
            console.error('❌ Erreur création compte:', signUpError);
            // Fallback: utiliser les données localStorage mais with Supabase ID
            const userData = {
              id: 'friday-user-' + btoa(userEmail).slice(0, 10),
              email: userEmail.trim(),
              name: userName || userEmail.split('@')[0],
              firstName: userFirstName || userEmail.split('@')[0]
            };
            setUser(userData);
            localStorage.setItem('friday_supabase_user', JSON.stringify(userData));
          }
        } else {
          // 5. Vérifier s'il y a une session Friday cachée
          const fridayUser = localStorage.getItem('friday_supabase_user');
          if (fridayUser) {
            setUser(JSON.parse(fridayUser));
          } else {
            setUser(null);
          }
        }
      } catch (error) {
        console.error('❌ Erreur initialisation utilisateur:', error);
        // En cas d'erreur, utiliser localStorage comme fallback mais avec un ID Supabase
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail) {
          const userData = {
            id: 'friday-user-' + btoa(userEmail).slice(0, 10),
            email: userEmail.trim(),
            name: localStorage.getItem('userName') || userEmail.split('@')[0],
            firstName: localStorage.getItem('userFirstName') || userEmail.split('@')[0]
          };
          setUser(userData);
        } else {
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    };

    initializeUser();

    // Écouter les changements d'auth Supabase
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔄 Changement auth Supabase:', event, session?.user?.email);
      
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email,
          name: session.user.user_metadata?.name || session.user.email.split('@')[0],
          firstName: session.user.user_metadata?.firstName || session.user.email.split('@')[0]
        });
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  return { user, loading };
}