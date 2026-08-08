import os

class Config:
    # Base Directory of Project
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Secret Key for Sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-ai-lost-found-key-2026'
    
    # Database Configuration
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Uploads Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # AI Matching Engine Weights Configuration
    # Total sum of weights equals 1.00 (100%)
    MATCHING_WEIGHTS = {
        'text_similarity': 0.35,        # NLP TF-IDF + Cosine similarity (35%)
        'category_similarity': 0.20,    # Exact / taxonomy category matching (20%)
        'color_brand_similarity': 0.15, # Color and brand token matching (15%)
        'location_similarity': 0.15,    # Location fuzzy & token matching (15%)
        'datetime_similarity': 0.10,    # Date distance proximity decay (10%)
        'image_similarity': 0.05        # OpenCV HSV color histogram correlation (5%)
    }
    
    # Score Thresholds for Matching & Notifications
    MATCH_SCORE_THRESHOLDS = {
        'RECORD_THRESHOLD': 40.0,       # Minimum matching score to record in DB
        'NOTIFICATION_THRESHOLD': 75.0, # Minimum score to auto-trigger alert notification
        'VERY_HIGH': 90.0,              # 90-100% Very High Match
        'HIGH': 75.0,                   # 75-89% High Match
        'POSSIBLE': 50.0                # 50-74% Possible Match
    }
