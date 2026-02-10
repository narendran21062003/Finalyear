-- Database Schema for Lead Management System
-- Create database
CREATE DATABASE IF NOT EXISTS lead_management;
USE lead_management;

-- Create leads table
CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    business_name VARCHAR(255),
    website_url VARCHAR(255),
    technical_status VARCHAR(50),
    reviews_snippet TEXT,
    pain_point VARCHAR(100),
    email_draft TEXT,
    contact_status VARCHAR(50)
);

-- Create indexes for better query performance
CREATE INDEX idx_business_name ON leads(business_name);
CREATE INDEX idx_timestamp ON leads(timestamp);
CREATE INDEX idx_technical_status ON leads(technical_status);
