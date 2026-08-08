import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    """
    Clean, lowercase, strip special characters and extra whitespaces.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_text_similarity(item1_text, item2_text):
    """
    Calculates TF-IDF vector cosine similarity between two text strings.
    Returns similarity float between 0.0 and 1.0.
    """
    clean_text1 = preprocess_text(item1_text)
    clean_text2 = preprocess_text(item2_text)
    
    if not clean_text1 or not clean_text2:
        return 0.0
    
    # Simple fallback if texts are exact match
    if clean_text1 == clean_text2:
        return 1.0
        
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([clean_text1, clean_text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(max(0.0, min(1.0, sim)))
    except Exception:
        # Fallback to SequenceMatcher if vectorizer fails on tiny input
        return float(SequenceMatcher(None, clean_text1, clean_text2).ratio())

def calculate_field_fuzzy_similarity(val1, val2):
    """
    Fuzzy ratio for shorter attributes like brand, color, or location.
    """
    clean1 = preprocess_text(val1)
    clean2 = preprocess_text(val2)
    
    if not clean1 or not clean2:
        return 0.0
        
    if clean1 == clean2:
        return 1.0
        
    # Check token overlap
    tokens1 = set(clean1.split())
    tokens2 = set(clean2.split())
    if tokens1 and tokens2:
        intersection = tokens1.intersection(tokens2)
        if intersection:
            jaccard = len(intersection) / float(len(tokens1.union(tokens2)))
            seq_ratio = SequenceMatcher(None, clean1, clean2).ratio()
            return max(jaccard, seq_ratio)
            
    return SequenceMatcher(None, clean1, clean2).ratio()
