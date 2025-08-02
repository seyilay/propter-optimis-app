CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    s3_url TEXT,
    duration INTEGER,
    status VARCHAR(50) DEFAULT 'uploaded',
    analysis_intent VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);