-- CORRECTION DÉFINITIVE - Structure table profiles
-- Copier ce code dans l'éditeur SQL Supabase et cliquer "Run"

-- 1. Supprimer le trigger défaillant
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- 2. Ajouter les colonnes manquantes à la table existante
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW());

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW());

-- 3. Mettre à jour les enregistrements existants
UPDATE profiles 
SET created_at = TIMEZONE('utc'::text, NOW())
WHERE created_at IS NULL;

UPDATE profiles 
SET updated_at = TIMEZONE('utc'::text, NOW())
WHERE updated_at IS NULL;

-- 4. Créer le trigger corrigé
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Vérifier la structure finale
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
ORDER BY ordinal_position;

-- 6. Message de confirmation
SELECT 'STRUCTURE CORRIGÉE - Toutes les colonnes sont maintenant présentes !' as resultat;
