-- =====================================================
-- BitMEX Growth Engineering Simulation
-- PostgreSQL Database Setup
-- =====================================================

-- Create User
CREATE USER growth WITH PASSWORD 'growth_secret';

CREATE ROLE growth WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  NOBYPASSRLS
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:rv/0whaO/efxsHlIMzOsGQ==$pIV2EARiEuKuxEbJ/xvkn4+wYuhtjf+CJjTjT2nk0oM=:HYA4Iwp8d00emQH4LGshZ+jnxnzhMXFNybdYQEhIbEg=';

-- Create Database
CREATE DATABASE growth_analytics
    WITH
    OWNER = growth
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
