import re
import os
import mysql.connector
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
import pandas as pd

# =============================================
# NLTK Initialization (MUST COME FIRST)
# =============================================

def initialize_nltk():
    """Ensure all required NLTK data is downloaded"""
    # Set custom download path (optional but recommended)
    nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.data.path.append(nltk_data_path)
    
    # Download required datasets if not present
    required_datasets = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'omw-1.4': 'corpora/omw-1.4'
    }
    
    for dataset_name, dataset_path in required_datasets.items():
        try:
            nltk.data.find(dataset_path)
        except LookupError:
            print(f"Downloading NLTK {dataset_name} dataset...")
            nltk.download(dataset_name, download_dir=nltk_data_path)

# Initialize NLTK when this module loads
initialize_nltk()

# =============================================
# Database Functions
# =============================================

def get_db_connection():
    """Create and return MySQL database connection"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",          # Change to your MySQL username
            password="Prajwal@123.",           # Change to your MySQL password
            database="resume_analyzer"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# =============================================
# Resume Processing Functions
# =============================================

def extract_text_from_pdf(file):
    """Extract raw text from PDF resume"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_skills(text):
    """Extract skills from resume text using NLP"""
    try:
        # Get English stopwords
        stop_words = set(stopwords.words('english'))
        
        # Add custom stopwords
        custom_stopwords = {
            'experience', 'work', 'project', 'using', 
            'skill', 'skills', 'ability', 'strong'
        }
        stop_words.update(custom_stopwords)
        
        # Tokenize text
        words = word_tokenize(text.lower())
        
        # Define technical skills to look for
        tech_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
            # Data Science
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'matplotlib', 'seaborn',
            # DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            # Other
            'git', 'linux', 'rest api', 'graphql'
        }
        
        # Extract matching skills
        skills = []
        for word in words:
            if word.isalpha() and word not in stop_words and len(word) > 2:
                if word in tech_skills:
                    skills.append(word)
        
        return list(set(skills))  # Remove duplicates
        
    except Exception as e:
        print(f"Skill extraction error: {e}")
        return []

# =============================================
# Database Operations
# =============================================

def save_resume_to_db(name, content, skills):
    """Save parsed resume to database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO resumes (name, content, skills)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (name, content, ','.join(skills)))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB save error: {e}")
            return False
        finally:
            conn.close()
    return False

def fetch_all_jobs():
    """Retrieve all jobs from database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM jobs")
            return cursor.fetchall()
        except Exception as e:
            print(f"DB fetch error: {e}")
            return []
        finally:
            conn.close()
    return []

def match_jobs_with_resume(skills):
    """Match resume skills with job requirements"""
    jobs = fetch_all_jobs()
    results = []
    
    for job in jobs:
        required_skills = [s.strip().lower() for s in job['skills_required'].split(',')]
        common_skills = set(skills) & set(required_skills)
        match_percentage = (len(common_skills) / len(required_skills)) * 100 if required_skills else 0
        
        results.append({
            'Job Title': job['title'],
            'Company': job['company'],
            'Match %': round(match_percentage, 2),
            'Required Skills': job['skills_required'],
            'Your Matching Skills': ', '.join(common_skills)
        })
    
    return pd.DataFrame(results) 