// Diagnostic de la structure de la table profiles
import { supabase } from './src/supabaseClient.js';

async function diagnosticTable() {
  console.log('🔍 DIAGNOSTIC DE LA TABLE PROFILES\n');
  
  try {
    // Test 1: Vérifier les colonnes de la table
    console.log('📋 Structure de la table profiles...');
    
    const { data: columns, error: columnsError } = await supabase
      .from('information_schema.columns')
      .select('column_name, data_type, is_nullable, column_default')
      .eq('table_name', 'profiles')
      .order('ordinal_position');
    
    if (columnsError) {
      console.error('❌ Erreur lecture structure:', columnsError.message);
    } else {
      console.log('✅ Colonnes trouvées:');
      columns.forEach(col => {
        console.log(`  - ${col.column_name}: ${col.data_type} ${col.is_nullable === 'YES' ? '(nullable)' : '(required)'}`);
      });
    }
    
    // Test 2: Créer un utilisateur et voir ce qui se passe
    console.log('\n👤 Test de création utilisateur...');
    
    const testEmail = `diagnostic.structure.${Date.now()}@example.com`;
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: testEmail,
      password: 'DiagnosticStruct123!'
    });
    
    if (signUpError && !signUpError.message.includes('already registered')) {
      console.error('❌ Erreur création utilisateur:', signUpError.message);
      return;
    }
    
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      console.error('❌ Pas d\'utilisateur connecté');
      return;
    }
    
    console.log('✅ Utilisateur créé:', user.email);
    
    // Test 3: Insérer un profil basique
    console.log('\n📝 Test d\'insertion basique...');
    
    const { data: insertData, error: insertError } = await supabase
      .from('profiles')
      .insert([
        {
          id: user.id,
          prenom: 'Diagnostic',
          nom: 'Structure'
        }
      ])
      .select();
    
    if (insertError) {
      console.error('❌ Erreur insertion:', insertError.message);
    } else {
      console.log('✅ Insertion réussie:', insertData);
    }
    
    // Test 4: Lire le profil créé
    console.log('\n📖 Lecture du profil créé...');
    
    const { data: profile, error: readError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (readError) {
      console.error('❌ Erreur lecture:', readError.message);
    } else {
      console.log('✅ Profil lu:');
      Object.keys(profile).forEach(key => {
        console.log(`  ${key}: ${profile[key]}`);
      });
    }
    
    // Test 5: Mise à jour sans updated_at
    console.log('\n✏️ Test de mise à jour simple (sans trigger)...');
    
    const { data: updateData, error: updateError } = await supabase
      .from('profiles')
      .update({
        prenom: 'Diagnostic-Modifié'
      })
      .eq('id', user.id)
      .select();
    
    if (updateError) {
      console.error('❌ Erreur mise à jour simple:', updateError.message);
      console.log('Détails:', updateError);
    } else {
      console.log('✅ Mise à jour simple réussie:', updateData);
    }
    
    // Nettoyage
    await supabase.auth.signOut();
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution
diagnosticTable()
  .then(() => {
    console.log('\n✅ Diagnostic terminé');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur:', error);
    process.exit(1);
  });
