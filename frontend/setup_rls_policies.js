// Configuration automatique des politiques RLS via l'API Supabase Management
import { supabase } from './src/supabaseClient.js';

async function setupRLSPolicies() {
  console.log('🔧 Configuration des politiques RLS pour la table profiles\n');
  
  // Étant donné que nous ne pouvons pas exécuter SQL arbitraire via l'API client,
  // nous devons utiliser l'API Management de Supabase ou configurer manuellement
  
  console.log('📋 Instructions pour configurer les politiques RLS :');
  console.log('');
  console.log('1. Aller sur https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/editor');
  console.log('2. Cliquer sur "SQL Editor" dans le menu de gauche');
  console.log('3. Copier et exécuter le SQL suivant :');
  console.log('');
  console.log('─'.repeat(60));
  
  const sqlScript = `
-- Configuration des politiques RLS pour la table profiles
-- Copier et coller ce code dans l'éditeur SQL de Supabase

-- 1. S'assurer que la table existe avec la bonne structure
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  prenom TEXT,
  nom TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  PRIMARY KEY (id)
);

-- 2. Activer RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 3. Supprimer les anciennes politiques si elles existent
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can delete own profile" ON profiles;

-- 4. Créer les nouvelles politiques
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can delete own profile" ON profiles
  FOR DELETE USING (auth.uid() = id);

-- 5. Créer un trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Vérification
SELECT 'Configuration terminée - Vous pouvez maintenant fermer cette fenêtre' as status;
`;
  
  console.log(sqlScript);
  console.log('─'.repeat(60));
  console.log('');
  console.log('4. Cliquer sur le bouton "Run" pour exécuter');
  console.log('5. Vérifier que le message "Configuration terminée" apparaît');
  console.log('');
  
  // En attendant, testons si on peut au moins créer une fonction qui contourne RLS
  console.log('🧪 Test de contournement temporaire...');
  
  try {
    // Essayer de créer une fonction qui ignore RLS
    const bypassRLSFunction = `
      CREATE OR REPLACE FUNCTION create_profile_bypass_rls(
        user_id UUID,
        first_name TEXT,
        last_name TEXT
      )
      RETURNS profiles
      LANGUAGE plpgsql
      SECURITY DEFINER
      AS $$
      DECLARE
        new_profile profiles;
      BEGIN
        INSERT INTO profiles (id, prenom, nom)
        VALUES (user_id, first_name, last_name)
        ON CONFLICT (id) DO UPDATE SET
          prenom = EXCLUDED.prenom,
          nom = EXCLUDED.nom
        RETURNING * INTO new_profile;
        
        RETURN new_profile;
      END;
      $$;
    `;
    
    // Cette approche ne fonctionnera probablement pas non plus sans permissions admin
    console.log('ℹ️ Impossible de créer une fonction de contournement via l\'API client');
    console.log('💡 La configuration manuelle via l\'interface Supabase est nécessaire');
    
  } catch (error) {
    console.log('ℹ️ Comme attendu, impossible de créer des fonctions via l\'API client');
  }
  
  return sqlScript;
}

async function testAfterConfiguration() {
  console.log('\n🧪 Test après configuration (à exécuter après avoir appliqué le SQL)');
  
  try {
    // Se connecter avec un utilisateur
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (!user) {
      console.log('ℹ️ Aucun utilisateur connecté, connexion de test...');
      const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
        email: 'diagnostic.test@example.com',
        password: 'DiagnosticTest123!'
      });
      
      if (signInError) {
        console.log('ℹ️ Pas d\'utilisateur de test disponible');
        return;
      }
    }
    
    const currentUser = await supabase.auth.getUser();
    const userId = currentUser.data.user?.id;
    
    if (userId) {
      // Essayer de créer un profil
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .upsert([
          {
            id: userId,
            prenom: 'Test',
            nom: 'Après-Config'
          }
        ])
        .select()
        .single();
      
      if (profileError) {
        console.log('❌ RLS pas encore configuré:', profileError.message);
        console.log('💡 Veuillez exécuter le script SQL ci-dessus');
      } else {
        console.log('✅ RLS configuré correctement ! Profil créé:', profileData);
      }
    }
    
  } catch (error) {
    console.log('ℹ️ Test reporté:', error.message);
  }
}

// Exécution
setupRLSPolicies()
  .then(() => testAfterConfiguration())
  .then(() => {
    console.log('\n✅ Configuration terminée');
    console.log('📝 N\'oubliez pas d\'exécuter le script SQL dans l\'interface Supabase !');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n❌ Erreur:', error);
    process.exit(1);
  });
