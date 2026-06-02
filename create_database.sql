-- =====================================================
-- BitMEX Growth Engineering Simulation
-- PostgreSQL Database Setup
-- =====================================================

-- Create User
CREATE USER growth WITH PASSWORD 'growth_secret';

-- Create Database
CREATE DATABASE growth_analytics
OWNER growth
ENCODING 'UTF8'
LC_COLLATE='C'
LC_CTYPE='C'
TEMPLATE template0;

-- Grant Privileges
GRANT ALL PRIVILEGES ON DATABASE growth_analytics TO growth;

-- Connect to database
\c growth_analytics

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO growth;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO growth;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO growth;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON FUNCTIONS TO growth;

-- Verify
SELECT current_database();
SELECT current_user;
