CREATE DATABASE resume_analyzer;
USE resume_analyzer;

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    company VARCHAR(100),
    skills_required VARCHAR(255)
);

CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    content TEXT,
    skills TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample jobs
INSERT INTO jobs (title, company, skills_required) VALUES 
('Data Scientist', 'Tech Corp', 'Python,SQL,Machine Learning'),
('Web Developer', 'Web Solutions', 'JavaScript,HTML,CSS'),
('DevOps Engineer', 'Cloud Inc', 'AWS,Docker,Kubernetes');