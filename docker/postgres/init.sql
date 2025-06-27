-- PostgreSQL initialization script for IT Asset Manager
-- This script sets up the database with proper permissions and extensions

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional indexes for better performance
-- These will be created after the application creates the tables

-- Function to create indexes after tables exist
CREATE OR REPLACE FUNCTION create_performance_indexes()
RETURNS void AS $$
BEGIN
    -- Check if tables exist before creating indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        -- User table indexes
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token);
        CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'assets') THEN
        -- Asset table indexes
        CREATE INDEX IF NOT EXISTS idx_assets_asset_tag ON assets(asset_tag);
        CREATE INDEX IF NOT EXISTS idx_assets_serial_number ON assets(serial_number);
        CREATE INDEX IF NOT EXISTS idx_assets_asset_type ON assets(asset_type);
        CREATE INDEX IF NOT EXISTS idx_assets_asset_category ON assets(asset_category);
        CREATE INDEX IF NOT EXISTS idx_assets_ownership_type ON assets(ownership_type);
        CREATE INDEX IF NOT EXISTS idx_assets_brand ON assets(brand);
        CREATE INDEX IF NOT EXISTS idx_assets_assigned_to ON assets(assigned_to);
        CREATE INDEX IF NOT EXISTS idx_assets_location ON assets(location);
        CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
        CREATE INDEX IF NOT EXISTS idx_assets_condition ON assets(condition);
        CREATE INDEX IF NOT EXISTS idx_assets_created_at ON assets(created_at);
        CREATE INDEX IF NOT EXISTS idx_assets_updated_at ON assets(updated_at);
        
        -- Composite indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_assets_type_status ON assets(asset_type, status);
        CREATE INDEX IF NOT EXISTS idx_assets_category_condition ON assets(asset_category, condition);
        CREATE INDEX IF NOT EXISTS idx_assets_ownership_status ON assets(ownership_type, status);
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'application_access') THEN
        -- Application access indexes
        CREATE INDEX IF NOT EXISTS idx_app_access_user_name ON application_access(user_name);
        CREATE INDEX IF NOT EXISTS idx_app_access_application_name ON application_access(application_name);
        CREATE INDEX IF NOT EXISTS idx_app_access_access_level ON application_access(access_level);
        CREATE INDEX IF NOT EXISTS idx_app_access_status ON application_access(status);
        CREATE INDEX IF NOT EXISTS idx_app_access_created_at ON application_access(created_at);
        
        -- Composite indexes
        CREATE INDEX IF NOT EXISTS idx_app_access_user_app ON application_access(user_name, application_name);
        CREATE INDEX IF NOT EXISTS idx_app_access_app_status ON application_access(application_name, status);
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'github_access') THEN
        -- GitHub access indexes
        CREATE INDEX IF NOT EXISTS idx_github_access_user_name ON github_access(user_name);
        CREATE INDEX IF NOT EXISTS idx_github_access_organization_name ON github_access(organization_name);
        CREATE INDEX IF NOT EXISTS idx_github_access_repo_name ON github_access(repo_name);
        CREATE INDEX IF NOT EXISTS idx_github_access_access_type ON github_access(access_type);
        CREATE INDEX IF NOT EXISTS idx_github_access_status ON github_access(status);
        CREATE INDEX IF NOT EXISTS idx_github_access_created_at ON github_access(created_at);
        
        -- Composite indexes
        CREATE INDEX IF NOT EXISTS idx_github_access_org_repo ON github_access(organization_name, repo_name);
        CREATE INDEX IF NOT EXISTS idx_github_access_user_org ON github_access(user_name, organization_name);
        CREATE INDEX IF NOT EXISTS idx_github_access_repo_status ON github_access(repo_name, status);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO it_assets_user;
GRANT CREATE ON SCHEMA public TO it_assets_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO it_assets_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO it_assets_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO it_assets_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO it_assets_user;
