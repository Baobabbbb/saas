import { supabase } from '../supabaseClient'

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
    
    return result;
  } catch (err) {
    return { error: err };
  }
}

// Inscription avec création de profil
export async function signUpWithProfile({ email, password, prenom, nom }) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  if (error) return { error };

  const user = data.user;
  if (user) {
    const { error: errorProfile } = await supabase
      .from('profiles')
      .insert([{ id: user.id, prenom, nom }]);
    if (errorProfile) return { error: errorProfile };
  }
  return { data };
}

// Déconnexion
export async function signOut() {
  return await supabase.auth.signOut();
}
