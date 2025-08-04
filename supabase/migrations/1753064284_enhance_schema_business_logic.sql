-- Migration: Add missing business logic fields to achieve single source of truth
-- This enhances Supabase schema to include all Django business logic fields

-- Enhance users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'analyst';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';

-- Enhance videos table with business logic fields
ALTER TABLE videos ADD COLUMN IF NOT EXISTS title VARCHAR(255);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS upload_progress INTEGER DEFAULT 0;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS processing_priority VARCHAR(20) DEFAULT 'standard';
ALTER TABLE videos ADD COLUMN IF NOT EXISTS file_size BIGINT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS content_type VARCHAR(100);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Enhance analyses table with business logic fields  
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS progress_percentage INTEGER DEFAULT 0;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS current_step VARCHAR(100);
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add indexes for business logic queries
CREATE INDEX IF NOT EXISTS idx_videos_processing_priority ON videos(processing_priority);
CREATE INDEX IF NOT EXISTS idx_videos_upload_progress ON videos(upload_progress);
CREATE INDEX IF NOT EXISTS idx_analyses_progress ON analyses(progress_percentage);
CREATE INDEX IF NOT EXISTS idx_analyses_status_started ON analyses(status, started_at);

-- Add constraints for business logic
ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS chk_users_role 
    CHECK (role IN ('admin', 'analyst', 'coach'));
    
ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS chk_users_subscription_tier 
    CHECK (subscription_tier IN ('free', 'pro', 'enterprise'));
    
ALTER TABLE videos ADD CONSTRAINT IF NOT EXISTS chk_videos_upload_progress 
    CHECK (upload_progress >= 0 AND upload_progress <= 100);
    
ALTER TABLE videos ADD CONSTRAINT IF NOT EXISTS chk_videos_processing_priority 
    CHECK (processing_priority IN ('low', 'standard', 'high', 'enterprise'));
    
ALTER TABLE analyses ADD CONSTRAINT IF NOT EXISTS chk_analyses_progress_percentage 
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100);