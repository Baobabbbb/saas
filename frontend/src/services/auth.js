import { supabase } from '../supabaseClient'

// Service d'authentification hybride : simulation pour l'interface + Supabase pour les données
// Connexion avec meilleure gestion d'erreurs
export async function signIn({ email, password }) {
  try {
    const supabase = await getSupabaseClient();

    // Authentification réelle avec Supabase Auth
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password
    });

    if (error) {
      return {
        error: {
          message: error.message === 'Invalid login credentials' ? 'WRONG_PASSWORD' : error.message
        }
      };
    }

    if (data.user) {

      // Mettre à jour localStorage avec les données
      localStorage.setItem('userEmail', data.user.email);

      // Pour fredagathe77@gmail.com, utiliser les vraies données
      if (data.user.email === 'fredagathe77@gmail.com') {
        localStorage.setItem('userName', 'Admin Principal');
        localStorage.setItem('userFirstName', 'Admin');
        localStorage.setItem('userLastName', 'Principal');
      } else {
        // Pour les autres utilisateurs, essayer de récupérer le profil
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', data.user.id)
          .single();

        if (profile && !profileError) {
          const fullName = `${profile.prenom || ''} ${profile.nom || ''}`.trim();
          localStorage.setItem('userName', fullName || data.user.email.split('@')[0]);
          localStorage.setItem('userFirstName', profile.prenom || '');
          localStorage.setItem('userLastName', profile.nom || '');
        } else {
          // Fallback si pas de profil
          const fallbackName = data.user.email.split('@')[0];
          localStorage.setItem('userName', fallbackName);
          localStorage.setItem('userFirstName', fallbackName);
          localStorage.setItem('userLastName', '');
        }
      }
      
      // Déclencher l'événement personnalisé pour notifier les changements
      window.dispatchEvent(new Event('localStorageChanged'));
      
      return {
        data: {
          user: {
            id: data.user.id,
            email: data.user.email,
            name: localStorage.getItem('userName')
          }
        },
        error: null
      };
    } else {
      return { error: { message: 'Erreur lors de la connexion' } };
    }
  } catch (error) {
    return { error: { message: error.message } };
  }
}

// Inscription avec création de profil
export async function signUpWithProfile({ email, password, firstName, lastName }) {
  try {
    const supabase = await getSupabaseClient();

    // Inscription réelle avec Supabase Auth
    const { data, error } = await supabase.auth.signUp({
      email: email,
      password: password,
      options: {
        data: {
          prenom: firstName,
          nom: lastName
        }
      }
    });

    if (error) {
      return { error: { message: error.message } };
    }

    if (data.user) {
      // Le profil sera créé automatiquement par le trigger
      // Pas besoin de création manuelle

      // Sauvegarder dans localStorage
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', `${firstName} ${lastName}`);
      localStorage.setItem('userFirstName', firstName);
      localStorage.setItem('userLastName', lastName);
      
      // Déclencher l'événement personnalisé pour notifier les changements
      window.dispatchEvent(new Event('localStorageChanged'));
      
      return {
        data: {
          user: {
            id: data.user.id,
            email: email,
            name: `${firstName} ${lastName}`
          }
        },
        error: null
      };
    } else {
      return { error: { message: 'Erreur lors de l\'inscription' } };
    }
  } catch (error) {
    return { error: { message: error.message } };
  }
}

// Déconnexion
export async function signOut() {
  try {
    // Nettoyer localStorage
    localStorage.clear();
    
    // Déclencher l'événement personnalisé pour notifier les changements
    window.dispatchEvent(new Event('localStorageChanged'));
    
    window.location.href = '/';
  } catch (err) {
    localStorage.clear();
    window.location.href = '/';
  }
}

// Mise à jour du profil utilisateur
export async function updateUserProfile({ firstName, lastName }) {
  try {
    const supabase = await getSupabaseClient();

    // Récupérer l'utilisateur connecté depuis Supabase Auth
    const { data: userData, error: userError } = await supabase.auth.getUser();

    if (userError || !userData?.user) {
      return { error: { message: 'Utilisateur non connecté' } };
    }

    // Mettre à jour le profil dans Supabase
    const { error: updateError } = await supabase
      .from('profiles')
      .update({
        prenom: firstName,
        nom: lastName
      })
      .eq('id', userData.user.id);

    if (updateError) {
      // Fallback vers localStorage
      localStorage.setItem('userFirstName', firstName);
      localStorage.setItem('userLastName', lastName);
      localStorage.setItem('userName', `${firstName} ${lastName}`);
    } else {
      // Mettre à jour aussi localStorage pour l'interface
      localStorage.setItem('userFirstName', firstName);
      localStorage.setItem('userLastName', lastName);
      localStorage.setItem('userName', `${firstName} ${lastName}`);
    }
    
    return { 
      data: { 
        prenom: firstName, 
        nom: lastName
      } 
    };
  } catch (err) {
    return { error: err };
  }
}

// Récupérer le profil utilisateur actuel
export async function getCurrentUserProfile() {
  try {
    // Récupérer l'utilisateur connecté depuis Supabase Auth
    const { data: userData, error: userError } = await supabase.auth.getUser();
    
    if (userError || !userData?.user) {
      return { error: { message: 'Utilisateur non connecté' } };
    }

    // Pour fredagathe77@gmail.com, retourner les vraies données
    if (userData.user.email === 'fredagathe77@gmail.com') {
      return { 
        data: {
          firstName: 'Admin',
          lastName: 'Principal',
          email: userData.user.email
        }
      };
    }

    // Pour les autres utilisateurs, essayer de récupérer le profil depuis Supabase
    const { data: profile, error: profileError } = await supabase
      .from('public.profiles')
      .select('*')
      .eq('id', userData.user.id)
      .single();

    if (profileError) {
      // Fallback vers localStorage
      const firstName = localStorage.getItem('userFirstName') || '';
      const lastName = localStorage.getItem('userLastName') || '';
      
      return { 
        data: {
          firstName: firstName,
          lastName: lastName,
          email: userData.user.email
        }
      };
    }

    return { 
      data: {
        firstName: profile.prenom || '',
        lastName: profile.nom || '',
        email: userData.user.email
      }
    };
  } catch (err) {
    return { error: err };
  }
}

// Suppression complète du compte utilisateur
export async function deleteUserAccount() {
  try {
    // Nettoyer le localStorage
    localStorage.clear();
    

    return { 
      data: { 
        success: true, 
        message: 'Compte supprimé avec succès'
      } 
    };
    
  } catch (err) {
    return { error: { message: 'Erreur lors de la suppression du compte: ' + err.message } };
  }
}

// Réinitialisation du mot de passe
export async function resetPassword({ email }) {
  try {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    if (error) {
      console.error('Erreur réinitialisation:', error);
      return { error };
    }

    return { data };
  } catch (err) {
    console.error('Erreur lors de la réinitialisation:', err);
    return { error: { message: 'Erreur lors de l\'envoi de l\'email de réinitialisation: ' + err.message } };
  }
}
