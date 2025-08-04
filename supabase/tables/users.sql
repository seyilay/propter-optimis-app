CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    team_name VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'coach')),
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    created_at TIMESTAMP DEFAULT NOW(),
    referral_source VARCHAR(100)
);