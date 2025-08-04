-- Complete schema synchronization for Supabase database
-- This adds all missing columns that Django models expect

-- Add missing columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'analyst';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';

-- Add constraints for role and subscription_tier
ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS users_role_check 
    CHECK (role IN ('admin', 'analyst', 'coach'));
ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS users_subscription_tier_check 
    CHECK (subscription_tier IN ('free', 'pro', 'enterprise'));

-- Add missing columns to videos table
ALTER TABLE videos ADD COLUMN IF NOT EXISTS title VARCHAR(255);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS upload_progress INTEGER DEFAULT 0;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS processing_priority VARCHAR(20) DEFAULT 'standard';
ALTER TABLE videos ADD COLUMN IF NOT EXISTS file_size BIGINT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS content_type VARCHAR(100);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add constraints for videos
ALTER TABLE videos ADD CONSTRAINT IF NOT EXISTS videos_upload_progress_check 
    CHECK (upload_progress >= 0 AND upload_progress <= 100);
ALTER TABLE videos ADD CONSTRAINT IF NOT EXISTS videos_processing_priority_check 
    CHECK (processing_priority IN ('low', 'standard', 'high', 'enterprise'));

-- Add missing columns to analyses table
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS progress_percentage INTEGER DEFAULT 0;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS current_step VARCHAR(100);
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add constraints for analyses
ALTER TABLE analyses ADD CONSTRAINT IF NOT EXISTS analyses_progress_percentage_check 
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100);

-- Add comments for documentation
COMMENT ON COLUMN users.last_login IS 'Required by Django AbstractBaseUser';
COMMENT ON COLUMN users.role IS 'User role: admin, analyst, or coach';
COMMENT ON COLUMN users.subscription_tier IS 'Subscription level: free, pro, or enterprise';
COMMENT ON COLUMN videos.upload_progress IS 'Upload progress percentage (0-100)';
COMMENT ON COLUMN videos.processing_priority IS 'Processing priority based on user tier';
COMMENT ON COLUMN analyses.progress_percentage IS 'Analysis progress percentage (0-100)';