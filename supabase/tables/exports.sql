CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);