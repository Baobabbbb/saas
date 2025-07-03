import { supabase } from '../supabaseClient.js'

// Connexion avec meilleure gestion d'erreurs
export async function signIn({ email, password }) {
  try {
    const result = await supabase.auth.signInWithPassword({ email, password });
    
    if (result.error) {
      // Pour Supabase, "Invalid login credentials" signifie généralement un mauvais mot de passe
      // Nous simplifions la logique pour éviter les effets de bord
      if (result.error.message.includes('Invalid login credentials')) {
        // On retourne toujours "WRONG_PASSWORD" par défaut
        // L'utilisateur peut toujours cliquer sur "S'inscrire" s'il n'a pas de compte
        return { 
          error: { 
            ...result.error, 
            message: 'WRONG_PASSWORD',
            originalMessage: result.error.message 
          } 
        };
      }
      
      // Pour d'autres types d'erreurs, retourner tel quel
      return result;
    }
    
    // Succès de connexion - stocker les informations utilisateur
    if (result.data?.user) {
      localStorage.setItem('userEmail', result.data.user.email);
      
      // Récupérer le profil utilisateur pour obtenir le nom
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('prenom, nom')
        .eq('id', result.data.user.id)
        .single();
      
      if (profile && !profileError) {
        localStorage.setItem('userName', `${profile.prenom} ${profile.nom}`);
        localStorage.setItem('userFirstName', profile.prenom);
        localStorage.setItem('userLastName', profile.nom);
      } else {
        // Fallback si pas de profil ou erreur RLS
        const fallbackName = result.data.user.email.split('@')[0];
        localStorage.setItem('userName', fallbackName);
        localStorage.setItem('userFirstName', fallbackName);
        localStorage.setItem('userLastName', '');
        console.warn('Impossible de récupérer le profil depuis la base, utilisation du fallback:', profileError?.message);
      }
    }
    
    return result;
  } catch (err) {
    return { error: err };
  }
}

// Inscription avec création de profil
export async function signUpWithProfile({ email, password, firstName, lastName }) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  if (error) return { error };

  const user = data.user;
  if (user) {
    // Stocker les informations utilisateur même si l'insertion du profil échoue
    localStorage.setItem('userEmail', email);
    localStorage.setItem('userName', `${firstName} ${lastName}`);
    localStorage.setItem('userFirstName', firstName);
    localStorage.setItem('userLastName', lastName);
    
    // Essayer d'insérer le profil, mais ne pas faire échouer l'inscription si ça ne marche pas
    const { error: errorProfile } = await supabase
      .from('profiles')
      .insert([{ id: user.id, prenom: firstName, nom: lastName }]);
    
    if (errorProfile) {
      console.warn('Impossible de créer le profil en base (RLS), mais localStorage est mis à jour:', errorProfile.message);
      // Ne pas retourner l'erreur pour ne pas faire échouer l'inscription
    }
  }
  return { data };
}

// Déconnexion
export async function signOut() {
  // Nettoyer le localStorage
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userName');
  localStorage.removeItem('userFirstName');
  localStorage.removeItem('userLastName');
  return await supabase.auth.signOut();
}

// Mise à jour du profil utilisateur
export async function updateUserProfile({ firstName, lastName }) {
  try {
    // Obtenir l'utilisateur connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return { error: { message: 'Utilisateur non connecté' } };
    }

    // Mettre à jour le localStorage en premier (fallback qui fonctionne toujours)
    localStorage.setItem('userFirstName', firstName);
    localStorage.setItem('userLastName', lastName);
    localStorage.setItem('userName', `${firstName} ${lastName}`);

    // Essayer de mettre à jour le profil dans la base de données
    const { data, error } = await supabase
      .from('profiles')
      .update({ 
        prenom: firstName, 
        nom: lastName 
      })
      .eq('id', user.id)
      .select()
      .single();

    if (error) {
      console.warn('Impossible de mettre à jour le profil en base (RLS), mais localStorage est mis à jour:', error.message);
      // Retourner un succès car localStorage est mis à jour
      return { 
        data: { 
          prenom: firstName, 
          nom: lastName,
          fallback: true 
        } 
      };
    }

    return { data };
  } catch (err) {
    // En cas d'erreur, au moins localStorage est mis à jour
    localStorage.setItem('userFirstName', firstName);
    localStorage.setItem('userLastName', lastName);
    localStorage.setItem('userName', `${firstName} ${lastName}`);
    
    return { 
      data: { 
        prenom: firstName, 
        nom: lastName,
        fallback: true 
      } 
    };
  }
}

// Récupérer le profil utilisateur actuel
export async function getCurrentUserProfile() {
  try {
    // Obtenir l'utilisateur connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return { error: { message: 'Utilisateur non connecté' } };
    }

    // Récupérer le profil depuis la base de données
    const { data, error } = await supabase
      .from('profiles')
      .select('prenom, nom')
      .eq('id', user.id)
      .single();

    if (error) {
      console.warn('Impossible de récupérer le profil depuis la base (RLS), utilisation du fallback localStorage:', error.message);
      
      // Fallback vers localStorage
      return { 
        data: {
          firstName: localStorage.getItem('userFirstName') || '',
          lastName: localStorage.getItem('userLastName') || '',
          email: user.email,
          fallback: true
        }
      };
    }

    return { 
      data: {
        firstName: data.prenom,
        lastName: data.nom,
        email: user.email
      }
    };
  } catch (err) {
    // Fallback vers localStorage en cas d'erreur
    const email = localStorage.getItem('userEmail');
    return { 
      data: {
        firstName: localStorage.getItem('userFirstName') || '',
        lastName: localStorage.getItem('userLastName') || '',
        email: email || '',
        fallback: true
      }
    };
  }
}

// Suppression complète du compte utilisateur
export async function deleteUserAccount() {
  try {
    // Obtenir l'utilisateur connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return { error: { message: 'Utilisateur non connecté' } };
    }

    console.log('🗑️ Suppression du compte utilisateur:', user.email, 'ID:', user.id);

    // Étape 1: Les suppressions sont maintenant gérées par la fonction RPC
    console.log('ℹ️ Suppression des données utilisateur via fonction RPC...');

    // Étape 2: Utiliser la fonction RPC pour supprimer complètement l'utilisateur
    const { data: rpcResult, error: rpcError } = await supabase.rpc('delete_user_account', {
      user_id: user.id
    });

    if (rpcError) {
      console.error('❌ Erreur RPC:', rpcError);
      
      // Si la fonction RPC n'existe pas, essayer une suppression manuelle
      if (rpcError.message.includes('function') && rpcError.message.includes('does not exist')) {
        console.warn('⚠️ Fonction delete_user_account non disponible');
        
        // Supprimer manuellement le profil
        const { error: profileError } = await supabase
          .from('profiles')
          .delete()
          .eq('id', user.id);

        if (profileError) {
          console.warn('Erreur suppression profil:', profileError.message);
        }

        // Déconnexion (l'utilisateur auth devra être supprimé manuellement)
        await supabase.auth.signOut();
        
        // Nettoyer le localStorage
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userName');
        localStorage.removeItem('userFirstName');
        localStorage.removeItem('userLastName');

        return { 
          error: { 
            message: 'Fonction de suppression non disponible. Profil supprimé mais utilisateur auth encore présent. Contactez l\'administrateur.',
            requiresAdminCleanup: true,
            userEmail: user.email,
            userId: user.id
          } 
        };
      }
      
      return { error: { message: 'Erreur lors de la suppression: ' + rpcError.message } };
    }

    // Vérifier le résultat de la fonction RPC
    if (rpcResult && rpcResult.success) {
      console.log('✅ Suppression réussie:', rpcResult);
      
      // Déconnexion après suppression réussie
      await supabase.auth.signOut();
      
      // Nettoyer le localStorage
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      localStorage.removeItem('userFirstName');
      localStorage.removeItem('userLastName');

      return { 
        data: { 
          success: true, 
          message: rpcResult.message || 'Compte supprimé avec succès'
        } 
      };
    } else {
      console.error('❌ Échec suppression:', rpcResult);
      return { 
        error: { 
          message: rpcResult?.error || 'Échec de la suppression du compte'
        } 
      };
    }

  } catch (err) {
    console.error('❌ Erreur générale:', err);
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
      return { error };
    }

    return { data };
  } catch (err) {
    return { error: { message: 'Erreur lors de l\'envoi de l\'email de réinitialisation: ' + err.message } };
  }
}
