CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    s3_url TEXT,
    duration INTEGER,
    status VARCHAR(50) DEFAULT 'uploaded',
    analysis_intent VARCHAR(100),
    upload_progress INTEGER DEFAULT 0 CHECK (upload_progress >= 0 AND upload_progress <= 100),
    processing_priority VARCHAR(20) DEFAULT 'standard' CHECK (processing_priority IN ('low', 'standard', 'high', 'enterprise')),
    file_size BIGINT,
    content_type VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);