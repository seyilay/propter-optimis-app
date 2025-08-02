CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    openstarlab_results JSONB,
    ai_insights JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    processing_time INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);