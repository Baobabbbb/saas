import { supabase } from '../supabaseClient'

// Ajouter une création
export async function addCreation({ type, title, data }) {
  const { data: userData } = await supabase.auth.getUser();
  if (!userData?.user) return { error: "Non authentifié" };
  return await supabase
    .from('creations')
    .insert([{
      user_id: userData.user.id,
      type,
      title,
      data
    }]);
}

// Récupérer l'historique des créations de l'utilisateur
export async function getUserCreations() {
  const { data: userData } = await supabase.auth.getUser();
  if (!userData?.user) return [];
  const { data, error } = await supabase
    .from('creations')
    .select('*')
    .eq('user_id', userData.user.id)
    .order('created_at', { ascending: false });
  return data || [];
}

export async function deleteCreation(id) {
  return await supabase.from('creations').delete().eq('id', id);
}
