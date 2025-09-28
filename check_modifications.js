const fs = require('fs');

// Lire le fichier compilé
const content = fs.readFileSync('saas/static/assets/main-03d95cb5.js', 'utf8');

// Chercher des indices de nos modifications
const hasPrenom = content.includes('prenom');
const hasNom = content.includes('nom');
const hasRole = content.includes('role');
const hasSignUpWithProfile = content.includes('signUpWithProfile');

console.log('🔍 Vérification des modifications dans le fichier compilé:');
console.log('✅ Contient "prenom":', hasPrenom);
console.log('✅ Contient "nom":', hasNom);
console.log('✅ Contient "role":', hasRole);
console.log('✅ Contient "signUpWithProfile":', hasSignUpWithProfile);

if (hasPrenom && hasNom && hasRole && hasSignUpWithProfile) {
  console.log('🎉 Toutes les modifications sont présentes dans le fichier compilé !');
} else {
  console.log('❌ Certaines modifications manquent dans le fichier compilé.');
}
