-- Migration: Add last_login field to users table
-- This field is required by Django's AbstractBaseUser

ALTER TABLE users 
ADD COLUMN last_login TIMESTAMP;

-- Add comment for field documentation
COMMENT ON COLUMN users.last_login IS 'Timestamp of user last login, required by Django AbstractBaseUser';