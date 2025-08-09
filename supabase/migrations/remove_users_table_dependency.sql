-- Remove dependency on custom users table
-- The videos table will reference Supabase auth.users directly

-- Drop foreign key constraint if it exists (this might not exist if we never created it)
-- ALTER TABLE videos DROP CONSTRAINT IF EXISTS videos_user_id_fkey;

-- The user_id column will now reference auth.users.id directly
-- No foreign key constraint needed in Django context

-- Add comment for documentation
COMMENT ON COLUMN videos.user_id IS 'References Supabase auth.users.id directly';
COMMENT ON TABLE videos IS 'Videos table now uses Supabase auth.users for user references';