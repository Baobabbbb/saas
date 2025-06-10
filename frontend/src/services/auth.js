import { supabase } from '../supabaseClient'

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

// Connexion
export async function signIn({ email, password }) {
  return await supabase.auth.signInWithPassword({ email, password });
}

// Déconnexion
export async function signOut() {
  return await supabase.auth.signOut();
}
