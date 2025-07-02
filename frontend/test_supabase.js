// Test de la connexion Supabase et de la table profiles
import { supabase } from './src/supabaseClient.js';

async function testSupabaseConnection() {
  console.log('🔍 Test de la connexion Supabase...');
  
  try {
    // Test 1: Vérifier la connexion générale
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    console.log('✅ Connexion Supabase OK');
    console.log('Utilisateur connecté:', user ? user.email : 'Aucun');
    
    // Test 2: Vérifier l'accès à la table profiles
    console.log('\n🔍 Test d\'accès à la table profiles...');
    const { data: profiles, error: profilesError } = await supabase
      .from('profiles')
      .select('*')
      .limit(5);
    
    if (profilesError) {
      console.error('❌ Erreur accès table profiles:', profilesError);
      
      // Test alternatif: essayer de créer la table si elle n'existe pas
      console.log('\n🔧 Tentative de création de la structure...');
      const { error: createError } = await supabase.rpc('create_profiles_table_if_not_exists');
      if (createError) {
        console.error('❌ Impossible de créer la table:', createError);
      }
    } else {
      console.log('✅ Accès table profiles OK');
      console.log('Profils trouvés:', profiles.length);
      if (profiles.length > 0) {
        console.log('Exemple:', profiles[0]);
      }
    }
    
    // Test 3: Vérifier la structure de la table
    console.log('\n🔍 Vérification de la structure de la table...');
    const { data: tableInfo, error: tableError } = await supabase
      .from('information_schema.columns')
      .select('column_name, data_type')
      .eq('table_name', 'profiles');
    
    if (!tableError && tableInfo) {
      console.log('✅ Structure de la table profiles:');
      tableInfo.forEach(col => {
        console.log(`  - ${col.column_name}: ${col.data_type}`);
      });
    }
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Test des fonctions d'authentification
async function testAuthFunctions() {
  console.log('\n🔍 Test des fonctions d\'authentification...');
  
  // Import dynamique des fonctions auth
  const { getCurrentUserProfile, updateUserProfile } = await import('./src/services/auth.js');
  
  try {
    // Test de récupération du profil
    const { data: profile, error: profileError } = await getCurrentUserProfile();
    
    if (profileError) {
      console.log('ℹ️ Aucun utilisateur connecté ou erreur profil:', profileError.message);
    } else {
      console.log('✅ Profil utilisateur récupéré:', profile);
    }
    
  } catch (error) {
    console.error('❌ Erreur test fonctions auth:', error);
  }
}

// Exécution des tests
console.log('🚀 Début des tests Supabase\n');
testSupabaseConnection()
  .then(() => testAuthFunctions())
  .then(() => {
    console.log('\n✅ Tests terminés');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n❌ Erreur lors des tests:', error);
    process.exit(1);
  });
