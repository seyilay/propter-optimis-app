-- Migration: create_performance_indexes
-- Created at: 1753064283

-- Create performance indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_videos_user_status ON videos(user_id, status);
CREATE INDEX IF NOT EXISTS idx_analyses_video ON analyses(video_id);
CREATE INDEX IF NOT EXISTS idx_exports_analysis ON exports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);;