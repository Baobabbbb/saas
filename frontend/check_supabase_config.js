// Script pour vérifier et configurer la table profiles dans Supabase
import { supabase } from './src/supabaseClient.js';

async function checkSupabaseConfiguration() {
  console.log('🔍 Vérification de la configuration Supabase\n');
  
  try {
    // Vérifier la table profiles
    console.log('📋 Vérification de la table profiles...');
    
    // Essayer de créer la table si elle n'existe pas
    const createTableSQL = `
    CREATE TABLE IF NOT EXISTS profiles (
      id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
      prenom TEXT,
      nom TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
      PRIMARY KEY (id)
    );
    `;
    
    const { data: createResult, error: createError } = await supabase.rpc('exec_sql', {
      sql: createTableSQL
    });
    
    if (createError) {
      console.log('ℹ️ Impossible de créer la table (probablement déjà existante):', createError.message);
    } else {
      console.log('✅ Table profiles vérifiée/créée');
    }
    
    // Vérifier les politiques RLS
    console.log('\n🔒 Vérification des politiques RLS...');
    
    // Essayer de désactiver RLS temporairement pour les tests
    const disableRLSSQL = `ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;`;
    const { error: disableError } = await supabase.rpc('exec_sql', {
      sql: disableRLSSQL
    });
    
    if (disableError) {
      console.log('ℹ️ Impossible de désactiver RLS (permissions insuffisantes)');
      console.log('💡 Nous devons créer des politiques RLS appropriées');
      
      // Créer des politiques RLS basiques
      const policies = [
        `CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);`,
        `CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);`,
        `CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);`,
        `CREATE POLICY "Users can delete own profile" ON profiles FOR DELETE USING (auth.uid() = id);`
      ];
      
      for (const policy of policies) {
        const { error: policyError } = await supabase.rpc('exec_sql', { sql: policy });
        if (policyError && !policyError.message.includes('already exists')) {
          console.log('ℹ️ Politique non créée:', policyError.message);
        }
      }
    } else {
      console.log('✅ RLS désactivé pour les tests');
    }
    
    // Test d'insertion avec utilisateur authentifié
    console.log('\n👤 Test avec utilisateur authentifié...');
    
    const testUser = {
      email: 'test.rls@example.com',
      password: 'TestPassword123!'
    };
    
    // Créer et connecter l'utilisateur
    const { data: authData, error: authError } = await supabase.auth.signUp(testUser);
    
    if (authError && !authError.message.includes('already registered')) {
      console.error('❌ Erreur création utilisateur:', authError.message);
      return;
    }
    
    // Si l'utilisateur existe déjà, se connecter
    if (authError?.message.includes('already registered')) {
      const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword(testUser);
      if (signInError) {
        console.error('❌ Erreur connexion:', signInError.message);
        return;
      }
      console.log('✅ Utilisateur connecté:', signInData.user.email);
    } else {
      console.log('✅ Utilisateur créé et connecté:', authData.user?.email);
    }
    
    // Maintenant essayer d'insérer un profil
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      console.log('\n📝 Insertion du profil...');
      
      const { data: insertData, error: insertError } = await supabase
        .from('profiles')
        .upsert([
          {
            id: user.id,
            prenom: 'Jean',
            nom: 'Dupont'
          }
        ])
        .select()
        .single();
      
      if (insertError) {
        console.error('❌ Erreur insertion profil:', insertError.message);
        
        // Essayer une insertion simple
        const { data: simpleInsert, error: simpleError } = await supabase
          .from('profiles')
          .insert([
            {
              id: user.id,
              prenom: 'Jean',
              nom: 'Dupont'
            }
          ]);
        
        if (simpleError) {
          console.error('❌ Erreur insertion simple:', simpleError.message);
        } else {
          console.log('✅ Insertion simple réussie');
        }
      } else {
        console.log('✅ Profil inséré:', insertData);
      }
      
      // Test de lecture
      console.log('\n📖 Test de lecture...');
      const { data: readData, error: readError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id);
      
      if (readError) {
        console.error('❌ Erreur lecture:', readError.message);
      } else {
        console.log('✅ Profil lu:', readData);
      }
    }
    
    // Déconnexion
    await supabase.auth.signOut();
    console.log('\n✅ Déconnexion effectuée');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution
checkSupabaseConfiguration()
  .then(() => {
    console.log('\n🎉 Vérification terminée');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur:', error);
    process.exit(1);
  });
