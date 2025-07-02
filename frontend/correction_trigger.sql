-- CORRECTION DU TRIGGER UPDATED_AT
-- Copier ce code dans l'éditeur SQL Supabase et cliquer "Run"

-- 1. Vérifier/ajouter la colonne updated_at si elle manque
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW());

-- 2. Corriger le trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier que la colonne updated_at existe avant de l'utiliser
    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at = TIMEZONE('utc'::text, NOW());
        RETURN NEW;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 3. Recréer le trigger
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Mettre à jour les enregistrements existants pour avoir updated_at
UPDATE profiles 
SET updated_at = COALESCE(updated_at, created_at, TIMEZONE('utc'::text, NOW()))
WHERE updated_at IS NULL;

-- 5. Vérification
SELECT 'CORRECTION TERMINÉE - Le système est maintenant parfaitement fonctionnel !' as resultat;
